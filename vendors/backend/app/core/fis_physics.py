import json
import os
import math
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from app.core.config import settings

# Modular Engine Imports
from app.safety_engine.core.v_tsr import VTsrCore, TSRState, SafetyContext
from app.engines.v_kinetics.core import VKineticsEngine, ReactionModel
from app.engines.v_diffusivity.core import VDiffusivityEngine, DiffusionContext
from app.engines.v_viscosity.core import VViscosityEngine, FluidProperties
from app.engines.v_calibration.core import VCalibrationEngine, Observation
from app.engines.v_profiler.core import VProfilerEngine, PulseReading
from app.engines.v_optimizer.core import VOptimizerEngine, OptimizationGoal
from app.engines.v_surface.core import VSurfaceEngine, SurfaceState

class CalibrationContext(BaseModel):
    ingredient_offsets: Dict[str, Dict[str, float]] = {}
    env_overrides: Dict[str, float] = {}
    efficiency_multiplier: float = 1.0

class PhysicsReactor(BaseModel):
    ingredients: Dict[str, float]
    thickness_mm: float = 20.0 # Default 2cm steak
    current_temp: float = 23.0
    core_temp: float = 23.0
    total_mass_g: float = 0.0
    elapsed_time: float = 0.0
    reaction_progress: Dict[str, float] = {"MAILLARD": 0.0, "CARAMELIZE": 0.0, "PROTEIN_DENATURE": 0.0}
    composite_ph: float = 7.0
    composite_viscosity: float = 1.0
    tsr: TSRState = TSRState()
    cal: CalibrationContext = CalibrationContext()
    surface: SurfaceState = SurfaceState()
    heating_method: str = "INDUCTION" # INDUCTION, GAS, HIGHLIGHT
    sensor_mode: str = "DUAL"        # DUAL (IR+Camera), SINGLE (Camera Only)
    cooking_method: str = "NONE"
    amb_humidity: float = 0.45

    def model_post_init(self, __context):
        self.total_mass_g = sum(self.ingredients.values())

class FisPhysics:
    """
    [The V-ORCHESTRATOR] 
    Main FIS Engine now acting as a high-level orchestrator of modular engines.
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    DATA_PATH = os.path.join(BASE_DIR, settings.PHYSICS_DATA_PATH)
    PHYSICS_DB = {}

    @classmethod
    def _load_db(cls):
        if not cls.PHYSICS_DB:
            try:
                target_path = os.path.abspath(cls.DATA_PATH)
                with open(target_path, "r", encoding="utf-8") as f:
                    cls.PHYSICS_DB = json.load(f)
            except Exception:
                cls.PHYSICS_DB = {"water": {"viscosity_cp": 1, "ph": 7.0, "state": "Liquid", "specific_heat": 4.18, "diffusivity": 0.14e-6}}

    REACTION_THRESHOLDS = {"MAILLARD": 154, "CARAMELIZE": 160, "WATER_BOIL": 100, "SIMMER_POINT": 95, "PROTEIN_DENATURE": 60, "OIL_SMOKE": 230}
    EVAPORATION_RATES = {"BOILING": 0.0005, "SIMMERING": 0.0002, "STIR_FRY": 0.0008, "FRYING": 0.0012}

    @classmethod
    def get_physics_properties(cls, name: str, cal: CalibrationContext = None) -> Dict[str, Any]:
        cls._load_db()
        n = name.lower().replace(" ", "_").strip()
        props_entry = cls.PHYSICS_DB.get(n, {"viscosity_cp": 1000, "ph": 7.0, "state": "Solid", "specific_heat": 2.5, "diffusivity": 0.14e-6, "water_content": 0.1})
        props = props_entry.copy()
        if cal and n in cal.ingredient_offsets:
            for p, v in cal.ingredient_offsets[n].items():
                if p in props: props[p] += v
        if "water_content" not in props: 
            props["water_content"] = 0.9 if props.get("state") == "Liquid" and "oil" not in n else 0.7
        if "fat_content" not in props:
            props["fat_content"] = 0.9 if "oil" in n or "butter" in n else 0.15
        return props

    @classmethod
    def add_ingredient(cls, reactor: PhysicsReactor, name: str, mass_g: float, temp_c: float) -> PhysicsReactor:
        """
        [Enhanced Thermal Mixing with Phase Change]
        Now accounts for the HUGE energy sink of steam formation (Latent Heat).
        Prevents over-predicting temp after adding water to a hot pan.
        """
        props = cls.get_physics_properties(name, cal=reactor.cal)
        
        # 1. Energy of new ingredient
        q_new = mass_g * props["specific_heat"] * temp_c
        
        # 2. Phase Change Shock (If adding liquid to pan > 100C)
        latent_loss = 0.0
        if reactor.current_temp > 100.0 and props["state"] == "Liquid" and "oil" not in name:
            # Estimate 5% of added mass flashes to steam instantly
            flash_mass = mass_g * 0.05 
            latent_loss = flash_mass * 2260 # 2260 J/g for water
            reactor.ingredients["water_lost_steam"] = reactor.ingredients.get("water_lost_steam", 0) + flash_mass

        # 3. New Equilibrium
        current_total_q = sum(m * cls.get_physics_properties(n)["specific_heat"] * reactor.current_temp for n, m in reactor.ingredients.items())
        combined_q = (current_total_q + q_new) - latent_loss
        
        reactor.ingredients[name] = reactor.ingredients.get(name, 0) + mass_g
        new_total_mass = sum(reactor.ingredients.values())
        
        # Recalculate mean SH
        weighted_sh = sum(cls.get_physics_properties(n)["specific_heat"] * m for n, m in reactor.ingredients.items())
        new_sh = weighted_sh / max(new_total_mass, 1e-6)
        
        reactor.current_temp = combined_q / (new_total_mass * new_sh)
        reactor.total_mass_g = new_total_mass
        return reactor

    @classmethod
    def step_simulation(cls, reactor: PhysicsReactor, dt: float, power_watts: float = 1500) -> PhysicsReactor:
        # 1. Thermal Evolution (Universal Input Model)
        props_map = {n: cls.get_physics_properties(n, cal=reactor.cal) for n in reactor.ingredients.keys()}
        weighted_sh = sum(props_map[n]["specific_heat"] * m for n, m in reactor.ingredients.items())
        total_sh = weighted_sh / max(reactor.total_mass_g, 1e-6)
        
        # Method-specific Efficiency
        eff_map = {"INDUCTION": 0.85, "GAS": 0.40, "HIGHLIGHT": 0.70}
        base_eff = eff_map.get(reactor.heating_method.upper(), 0.85)
        
        # Apply Pulse Heating effect (V-Surface Strategy)
        if reactor.surface.adhesion_risk > 0.5:
             # Vibrational energy from pulsing reduces effective energy slightly but aids separation
             base_eff *= 0.95 

        q_in = power_watts * (base_eff * reactor.cal.efficiency_multiplier) * dt
        
        # Convective Waste (GAS mode loses more to air)
        waste_coeff = 12.0 if reactor.heating_method != "GAS" else 25.0
        vol_m3 = (reactor.total_mass_g / 1e6)
        area = 6 * (vol_m3**(2/3))
        q_out = waste_coeff * area * (reactor.current_temp - 23.0) * dt
        
        net_energy = q_in - q_out
        
        free_water = sum(m * props_map[n].get("water_content", 0.0) for n, m in reactor.ingredients.items() if props_map[n]["state"] == "Liquid" and "oil" not in n)
        
        if free_water > 1.0 and reactor.current_temp >= 100:
            reactor.current_temp = 100
            evap = net_energy / 2260
            for n in reactor.ingredients:
                if props_map[n]["state"] == "Liquid" and "oil" not in n:
                    reactor.ingredients[n] -= min(reactor.ingredients[n], evap * (reactor.ingredients[n]/free_water))
        else:
            reactor.current_temp += net_energy / (reactor.total_mass_g * total_sh)

        reactor.total_mass_g = sum(reactor.ingredients.values())

        # 2. V-SURFACE: Surface Health & Adhesion (Delegated)
        reactor.surface = VSurfaceEngine.apply_aging_effect(reactor.surface, reactor.current_temp, dt)
        adhesion_risk = VSurfaceEngine.analyze_adhesion_risk(reactor.surface, reactor.current_temp)
        
        # 3. V-TSR: Safety Engine (Delegated)
        # 2. V-DIFFUSION: (Material & Geometry Aware)
        # alpha is derived from composition (Choi-Okos model)
        water_ratio = free_water / max(reactor.total_mass_g, 1e-6)
        fat_ratio = sum(m * props_map[n].get("fat_content", 0.0) for n, m in reactor.ingredients.items()) / max(reactor.total_mass_g, 1e-6)
        
        diff_context = VDiffusivityEngine.get_context(reactor.thickness_mm, water_ratio, fat_ratio)
        res = VDiffusivityEngine.estimate_core_temperature(
            surface_temp=reactor.current_temp,
            initial_temp=reactor.core_temp,
            duration=dt,
            context=diff_context
        )
        reactor.core_temp = res["core_temp"]
        temp_gradient = reactor.current_temp - reactor.core_temp

        # 3. SAFETY & QUALITY: Charring Risk
        # If surface is 80C higher than core, surface will char before core cooks.
        charring_risk = max(0, (temp_gradient - 80.0) / 100.0)
        
        s_context = SafetyContext(hazard_activation_energy=75000, critical_threshold_temp=230)
        reactor.tsr = VTsrCore.update_state(reactor.tsr, reactor.current_temp, dt, s_context)

        # 4. V-KINETICS: (Solvent Effect & Moisture Corrected)
        water_ratio = free_water / max(reactor.total_mass_g, 1e-6)
        models = {"MAILLARD": ReactionModel(name="MAILLARD", A=1e12, Ea=85000, Cf=1e-6), "CARAMELIZE": ReactionModel(name="CARAMELIZE", A=1e13, Ea=105000, Cf=1e-4)}
        
        # Solvent Effect: Water acts as a catalyst for intermediate flavor precursors
        # Even if temp drops, flavor complexing can INCREASE in presence of moisture.
        solvent_boost = 1.0 + (water_ratio * 0.5) if water_ratio > 0.1 else 1.0
        
        # Quality penalty due to bad surface or bad gradient
        quality_factor = (1.0 - adhesion_risk * 0.5) * (1.0 - charring_risk) * solvent_boost
        for r_type, model in models.items():
            # If food sticks, Maillard becomes uncontrolled carbonization
            reactor.reaction_progress[r_type] = VKineticsEngine.step_progress(
                reactor.reaction_progress[r_type], 
                reactor.current_temp, 
                dt, 
                model, 
                water_mass_ratio=water_ratio
            ) * quality_factor

        # 4. V-VISCOSITY: (Non-Newtonian)
        initial_mass = sum(reactor.ingredients.values())
        fluids = [FluidProperties(viscosity_cp=props_map[n]["viscosity_cp"], ph=props_map[n]["ph"], weight_fraction=m/max(initial_mass,1e-6)) for n, m in reactor.ingredients.items()]
        visc_results = VViscosityEngine.blend_and_concentrate(fluids, 1.0, shear_rate=2.0)
        reactor.composite_ph, reactor.composite_viscosity = visc_results["ph"], visc_results["viscosity_cp"]

        reactor.elapsed_time += dt
        return reactor

    @classmethod
    def get_target_temp(cls, action: str, ingredients: List[str], duration: float = 60.0, cal: CalibrationContext = None) -> Dict[str, Any]:
        temp, phenomenon = 100, "Boiling"
        if "fry" in action.lower() or "sear" in action.lower(): temp, phenomenon = 154, "Searing"
        avg_diff = sum(cls.get_physics_properties(i, cal=cal)["diffusivity"] for i in ingredients) / max(len(ingredients), 1)
        diff_context = DiffusionContext(diffusivity=avg_diff)
        lag = VDiffusivityEngine.estimate_core_temperature(temp, 25.0, duration, diff_context)
        risk = VDiffusivityEngine.predict_overcook_risk(lag["core_temp"], temp, duration)
        return {"surface_temp": temp, "phenomenon": phenomenon, "core_temp_estimate": lag["core_temp"], "overcook_risk": risk}

    @classmethod
    def estimate_composite_properties(cls, ingredients_mass_map: Dict[str, float]) -> Dict[str, Any]:
        """
        [HARDENING FIX]
        Calculates the composite physical properties of a mixture.
        Ensures NO NULL values are returned for critical physics fields.
        """
        total_mass = sum(ingredients_mass_map.values())
        if total_mass == 0:
            return {
                "composite_viscosity_cp": 1.0, 
                "composite_ph": 7.0, 
                "composite_specific_heat": 4.18,
                "components": 0
            }

        total_k_visc = 0.0 # Logarithmic mixing rule for viscosity
        total_ph_conc = 0.0 # H+ ion concentration
        total_sh = 0.0
        
        for name, mass in ingredients_mass_map.items():
            props = cls.get_physics_properties(name)
            weight = mass / total_mass
            
            # Viscosity (Arrhenius mixture rule approximation: ln(n_mix) = sum(xi * ln(ni)))
            # We use a simplified linear-log approach for stability
            v = max(props.get("viscosity_cp", 1), 1)
            total_k_visc += weight * math.log(v)
            
            # pH (H+ = 10^-pH)
            ph = props.get("ph", 7.0)
            h_ions = 10**(-ph)
            total_ph_conc += weight * h_ions
            
            # Specific Heat (Linear)
            sh = props.get("specific_heat", 4.18)
            total_sh += weight * sh

        # Reconstruct
        comp_visc = math.exp(total_k_visc)
        comp_ph = -math.log10(total_ph_conc) if total_ph_conc > 0 else 7.0
        
        return {
            "composite_viscosity_cp": round(comp_visc, 2),
            "composite_ph": round(comp_ph, 2),
            "composite_specific_heat": round(total_sh, 2),
            "components": len(ingredients_mass_map)
        }

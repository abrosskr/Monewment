from typing import List, Dict, Optional
from pydantic import BaseModel
import datetime
import uuid

from app.models.matter import IngredientModel, FlavorProfile
from app.models.machine_ir import MachineCommand
from app.models.fis_protocol import FisFile, FisMetadata
from app.core.taste_dna import TasteDNA
from app.engines.v_academy.core import VAcademyEngine
from app.engines.compatibility import CompatibilityEngine

class CompilationResult(BaseModel):
    fis_file: Optional[FisFile]
    status: str # "SUCCESS", "FAILED", "WARNING"
    issues: List[Dict]
    logs: List[str]

class CompilerEngine:
    """
    [The Food Compiler]
    Orchestrates the conversion from Text -> Physics -> Robot Code.
    """
    
    @classmethod
    def compile_recipe(cls, title: str, ingredients_text: List[str], instructions_text: List[str]) -> CompilationResult:
        logs = []
        logs.append(f"Starting Compilation for '{title}'...")
        
        # 1. Matter Analysis (Ingredients -> Matter DB)
        matter_map: Dict[str, IngredientModel] = {}
        for ing_text in ingredients_text:
            # Heuristic: Split "1 cup Flour" -> "Flour"
            # In Phase 5, this should be more robust, but using TasteDNA simple lookup for now
            # Assume ing_text is just name for simplicity of prototype
            name = ing_text.split(" ")[-1] # Very dumb parser
            matter = TasteDNA.get_matter(name)
            matter_map[name] = matter
            logs.append(f"Resolved Material: {ing_text} -> {matter.name} (Conf: HIGH)")
            
        # 2. Physics Extraction (Instructions -> Machine Commands)
        commands: List[MachineCommand] = []
        step_id = 1
        
        full_text = " ".join(instructions_text)
        primitives = VAcademyEngine.process_transcript(full_text)
        
        for p in primitives:
            # Convert Primitive -> MachineCommand
            # In a real compiler, this is a complex mapping.
            # Here we map 1:1 for demonstration.
            
            # Extract extracted params from tags
            temp = None
            duration = None
            confidence = "LOW"
            
            for tag in p.context_tags:
                if "PARAM_TEMP" in tag: temp = float(tag.split(":")[1])
                if "PARAM_TIME" in tag: duration = int(tag.split(":")[1])
                if "META_CONFIDENCE" in tag: confidence = tag.split(":")[1]
            
            # Map Category to Action
            action = "WAIT"
            if "THERMAL" in p.category.name: action = "HEAT_SURFACE"
            if "HYDRATION" in p.category.name: action = "HEAT_LIQUID"
            if "SURFACE" in p.category.name: action = "STIR"
            
            cmd = MachineCommand(
                step_id=step_id,
                action=action,              # type: ignore (Enum vs String mismatch simplified)
                target_ingredient_id="mix_01",
                temperature_c=temp,
                duration_sec=duration,
                goal=None 
            )
            commands.append(cmd)
            logs.append(f"Compiled Instruction: {cmd.to_instruction_string()} [Conf: {confidence}]")
            step_id += 1
            
        # 3. Edibility Validation (The Firewall)
        validation = CompatibilityEngine.validate_recipe(title, list(matter_map.values()))
        issues = validation.get("issues", [])
        
        status = "SUCCESS"
        if not validation["compatible"]:
            status = "FAILED"
            logs.append("CRITICAL: Compilation halted due to Edibility Check failure.")
            return CompilationResult(fis_file=None, status=status, issues=issues, logs=logs)
        elif issues:
            status = "WARNING"
            logs.append(f"Compilation finished with {len(issues)} warnings.")
            
        # 4. Construct FIS File
        # Calculate Vectors
        # Summing vectors for final taste profile (Simplified)
        final_salt = sum([m.flavor.salt for m in matter_map.values()])
        final_sugar = sum([m.flavor.sugar for m in matter_map.values()])
        
        fis = FisFile(
            metadata=FisMetadata(
                recipe_id=str(uuid.uuid4()),
                name=title,
                author="Vendors Compiler v1.0",
                data_quality=0.8 if status == "SUCCESS" else 0.5,
                extra_info={"compiler_logs": logs}
            ),
            ingredients={k: v.physical.dict() for k, v in matter_map.items()}, # Explicit dict conversion
            taste_profile=FlavorProfile(salt=final_salt, sugar=final_sugar), # Use FlavorProfile
            timeline=[c.dict() for c in commands] # Explicit dict conversion
        )
        
        return CompilationResult(fis_file=fis, status=status, issues=issues, logs=logs)

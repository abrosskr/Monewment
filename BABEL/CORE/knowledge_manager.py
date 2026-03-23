# [V9.0 BABEL SOVEREIGNTY] Knowledge Manager
# c:\monewment\BABEL\CORE\knowledge_manager.py

import json
from enum import Enum

class BabelCategory(Enum):
    ING = "INGREDIENT"
    DIS = "DISH"
    NUT = "NUTRIENT"
    REL = "RELATION"
    CAT = "CATEGORY"

# [SOVEREIGN KNOWLEDGE] 본토에서 회수한 지식의 본가
MATERIAL_CONSTANTS = {
    "BBL.ING.PORK_BELLY": {"water": 0.45, "fat": 0.35, "dens": 1050, "heat": 2800},
    "BBL.ING.CHICKEN_BREAST": {"water": 0.74, "fat": 0.02, "dens": 1040, "heat": 3500},
    "BBL.NUT.WATER": {"water": 1.0, "fat": 0.0, "dens": 1000, "heat": 4184}
}

CORE_CONCEPTS = {
    "BBL.REL.REFERENCED_IN": {"name": "Referenced In Asset", "cat": "REL"},
    "BBL.REL.CONTRAINDICATED": {"name": "Contraindicated with", "cat": "REL"},
    "BBL.REL.SYNERGIZES": {"name": "Synergizes with", "cat": "REL"}
}

class SovereignKnowledge:
    @staticmethod
    def get_constants():
        return MATERIAL_CONSTANTS

    @staticmethod
    def get_concepts():
        return CORE_CONCEPTS

    @staticmethod
    def export_knowledge():
        return {
            "constants": MATERIAL_CONSTANTS,
            "concepts": CORE_CONCEPTS
        }

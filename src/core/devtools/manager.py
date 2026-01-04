import os
from .inspectors.structure import StructureInspector
from .inspectors.database import DatabaseInspector
from .inspectors.network import NetworkInspector
from .inspectors.config import ConfigInspector

class DevToolsManager:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.docs_dir = os.path.join(root_dir, "docs", "auto_generated")
        os.makedirs(self.docs_dir, exist_ok=True)
        
        # 4대 담당관 고용
        self.structure = StructureInspector()
        self.database = DatabaseInspector()
        self.network = NetworkInspector()
        self.config = ConfigInspector()

    def run_all_inspections(self):
        """모든 감시를 수행하고 파일로 저장"""
        self._save("STRUCTURE.md", self.structure.inspect(self.root_dir))
        self._save("DATA_SCHEMA.md", self.database.inspect(self.root_dir))
        self._save("API_SPEC.md", self.network.inspect(self.root_dir))
        self._save("CONFIG_MAP.md", self.config.inspect(self.root_dir))
        
        return "All inspections completed."

    def _save(self, filename, content):
        with open(os.path.join(self.docs_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)

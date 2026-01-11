
import logging
from typing import Dict, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.models import Cluster
from src.core.k8s_client import K8sClient
from src.database import AsyncSessionLocal
from kubernetes import client, config

logger = logging.getLogger(__name__)

class ClusterManager:
    _instance: Optional['ClusterManager'] = None

    def __init__(self):
        self.clients: Dict[int, K8sClient] = {}
        self.default_client: Optional[K8sClient] = None
        self.is_initialized = False

    @classmethod
    def get_instance(cls) -> 'ClusterManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(self):
        """
        Loads all clusters from the database and initializes K8s clients.
        Async because we need DB access.
        """
        if self.is_initialized:
            return

        logger.info("🌐 Initializing Cluster Manager...")
        
        # 1. Initialize Default (Local) Client
        try:
            self.default_client = K8sClient() # Global config
            # Assume ID 1 is the default/local cluster if not specified otherwise
            # In a real scenario, we might query which DB entry corresponds to "local"
            self.clients[1] = self.default_client 
            logger.info("✅ Default Cluster (ID: 1) Client Initialized.")
        except Exception as e:
            logger.warning(f"⚠️ Failed to init default cluster: {e}")
            self.default_client = None

        # 2. Load Remote Clusters from DB
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Cluster))
            clusters = result.scalars().all()
            
            for cluster in clusters:
                if cluster.id in self.clients: continue 
                
                logger.info(f"🔌 Connecting to Cluster '{cluster.name}' (ID: {cluster.id})...")
                
                # [Production Logic Placeholder]
                # In a real environment, we would:
                # 1. Fetch encrypted kubeconfig from Vault/DB using cluster.name
                # 2. Decrypt it
                # 3. Create a temporary file or use KubeConfigLoader to creation an ApiClient
                # api_client = config.new_client_from_config_dict(cluster.kubeconfig_dict)
                
                # [Simulation/Mock Logic] 
                # Since we don't have real remote clusters, we create a proxy/mock connection.
                # We reuse the default client's connection parameters if available, or just a generic one.
                # This allows the API to "think" it's talking to a different cluster.
                
                try:
                    # Creating a Client PROXY
                    # For demonstration, we reuse the default api_client. 
                    # If this were real, we'd pass a different ApiClient here.
                    target_api_client = self.default_client.api_client if self.default_client else None
                    
                    remote_client = K8sClient(api_client=target_api_client)
                    self.clients[cluster.id] = remote_client
                    logger.info(f"✅ Cluster '{cluster.name}' Connected (Proxy/Mock).")
                except Exception as e:
                    logger.error(f"❌ Failed to connect cluster {cluster.name}: {e}")
                    
        self.is_initialized = True

    def get_client(self, cluster_id: int) -> Optional[K8sClient]:
        """
        Returns the specific K8s client for the requested cluster ID.
        Falls back to default if not found (or optionally raises error).
        """
        client = self.clients.get(cluster_id)
        if not client:
            logger.warning(f"⚠️ Client for Cluster ID {cluster_id} not found. Falling back to default.")
            return self.default_client
        return client

    def get_client_by_project(self, project) -> Optional[K8sClient]:
        """
        Helper: Resolves K8s client directly from Project object.
        Project -> Organization -> Cluster ID
        """
        if not project.organization:
            logger.warning(f"Project {project.name} has no organization. Using default cluster.")
            return self.default_client
            
        cluster_id = project.organization.cluster_id
        if not cluster_id:
            # Fallback to default if Org not assigned to cluster
             return self.default_client
             
        return self.get_client(cluster_id)

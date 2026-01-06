import logging
from kubernetes import client, config
from src.config import settings

logger = logging.getLogger(__name__)

class K8sClient:
    def __init__(self):
        self.load_config()
        self.custom_api = client.CustomObjectsApi()
        self.core_api = client.CoreV1Api()

    def load_config(self):
        try:
            # First try in-cluster config (Production/K8s)
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes config.")
        except config.ConfigException:
            try:
                # Fallback to local kubeconfig (Dev)
                config.load_kube_config()
                logger.info("Loaded local kubeconfig.")
            except Exception as e:
                logger.error(f"Failed to load Kubernetes config: {e}")
                raise e

# Create a singleton instance
try:
    k8s = K8sClient()
except Exception:
    k8s = None

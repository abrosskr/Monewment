import logging
from kubernetes import client, config
from src.config import settings
from kubernetes.client.rest import ApiException
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class K8sClient:
    def __init__(self, api_client: Optional[client.ApiClient] = None):
        """
        Initialize K8s Client.
        :param api_client: Optional custom ApiClient (for Multi-Cluster). If None, loads global default config.
        """
        self.api_client = api_client
        
        if not self.api_client:
            try:
                # Try in-cluster config first (when running inside K8s)
                config.load_incluster_config()
                logger.info("Loaded in-cluster Kubernetes config.")
            except config.ConfigException:
                try:
                    # Fallback to local kubeconfig
                    config.load_kube_config()
                    logger.info("Loaded local kubeconfig.")
                except Exception as e:
                    logger.error(f"Failed to load Kubernetes config: {e}")
                    raise
        else:
             logger.info("Initialized K8sClient with injected ApiClient.")
        
        # Initialize APIs with specific client (or default global if None)
        self.core_api = client.CoreV1Api(api_client=self.api_client)
        self.apps_api = client.AppsV1Api(api_client=self.api_client)
        self.networking_api = client.NetworkingV1Api(api_client=self.api_client)
        self.custom_api = client.CustomObjectsApi(api_client=self.api_client)
    
    # [Phase 11] Autonomous Deployment Methods
    
    def create_deployment(
        self,
        name: str,
        namespace: str,
        image: str,
        port: int,
        replicas: int = 1,
        env_vars: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Create Kubernetes Deployment
        
        Args:
            name: Deployment name
            namespace: Namespace
            image: Docker image tag
            port: Container port
            replicas: Number of replicas
            env_vars: Environment variables
        
        Returns:
            True if successful
        """
        # Environment variables
        env_list = []
        if env_vars:
            for key, value in env_vars.items():
                env_list.append(
                    client.V1EnvVar(
                        name=key,
                        value_from=client.V1EnvVarSource(
                            secret_key_ref=client.V1SecretKeySelector(
                                name=f"{name}-secrets",
                                key=key
                            )
                        )
                    )
                )
        
        # Container spec
        container = client.V1Container(
            name="app",
            image=image,
            ports=[client.V1ContainerPort(container_port=port)],
            env=env_list if env_list else None
        )
        
        # Pod template
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": name}),
            spec=client.V1PodSpec(containers=[container])
        )
        
        # Deployment spec
        spec = client.V1DeploymentSpec(
            replicas=replicas,
            selector=client.V1LabelSelector(match_labels={"app": name}),
            template=template
        )
        
        # Deployment
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=name),
            spec=spec
        )
        
        try:
            self.apps_api.create_namespaced_deployment(
                namespace=namespace,
                body=deployment
            )
            logger.info(f"Deployment {name} created in namespace {namespace}")
            return True
        except ApiException as e:
            logger.error(f"Failed to create deployment: {e}")
            return False
    
    def create_service(
        self,
        name: str,
        namespace: str,
        port: int,
        target_port: int
    ) -> bool:
        """
        Create Kubernetes Service
        
        Args:
            name: Service name
            namespace: Namespace
            port: Service port
            target_port: Container port
        
        Returns:
            True if successful
        """
        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(name=f"{name}-service"),
            spec=client.V1ServiceSpec(
                selector={"app": name},
                ports=[client.V1ServicePort(
                    port=port,
                    target_port=target_port
                )],
                type="ClusterIP"
            )
        )
        
        try:
            self.core_api.create_namespaced_service(
                namespace=namespace,
                body=service
            )
            logger.info(f"Service {name}-service created in namespace {namespace}")
            return True
        except ApiException as e:
            logger.error(f"Failed to create service: {e}")
            return False
    
    def create_ingress(
        self,
        name: str,
        namespace: str,
        host: str,
        service_name: str,
        service_port: int
    ) -> bool:
        """
        Create Kubernetes Ingress
        
        Args:
            name: Ingress name
            namespace: Namespace
            host: Domain name
            service_name: Backend service name
            service_port: Backend service port
        
        Returns:
            True if successful
        """
        ingress = client.V1Ingress(
            api_version="networking.k8s.io/v1",
            kind="Ingress",
            metadata=client.V1ObjectMeta(
                name=f"{name}-ingress",
                annotations={
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod"
                }
            ),
            spec=client.V1IngressSpec(
                tls=[client.V1IngressTLS(
                    hosts=[host],
                    secret_name=f"{name}-tls"
                )],
                rules=[client.V1IngressRule(
                    host=host,
                    http=client.V1HTTPIngressRuleValue(
                        paths=[client.V1HTTPIngressPath(
                            path="/",
                            path_type="Prefix",
                            backend=client.V1IngressBackend(
                                service=client.V1IngressServiceBackend(
                                    name=service_name,
                                    port=client.V1ServiceBackendPort(number=service_port)
                                )
                            )
                        )]
                    )
                )]
            )
        )
        
        try:
            self.networking_api.create_namespaced_ingress(
                namespace=namespace,
                body=ingress
            )
            logger.info(f"Ingress {name}-ingress created in namespace {namespace}")
            return True
        except ApiException as e:
            logger.error(f"Failed to create ingress: {e}")
            return False
    
    def create_secret(
        self,
        name: str,
        namespace: str,
        data: Dict[str, str]
    ) -> bool:
        """
        Create Kubernetes Secret
        
        Args:
            name: Secret name
            namespace: Namespace
            data: Secret data (will be base64 encoded automatically)
        
        Returns:
            True if successful
        """
        import base64
        
        # Base64 encode all values
        encoded_data = {
            key: base64.b64encode(value.encode()).decode()
            for key, value in data.items()
        }
        
        secret = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=client.V1ObjectMeta(name=name),
            data=encoded_data
        )
        
        try:
            self.core_api.create_namespaced_secret(
                namespace=namespace,
                body=secret
            )
            logger.info(f"Secret {name} created in namespace {namespace}")
            return True
        except ApiException as e:
            logger.error(f"Failed to create secret: {e}")
            return False
    
    def delete_deployment(self, name: str, namespace: str) -> bool:
        """Delete Deployment"""
        try:
            self.apps_api.delete_namespaced_deployment(name=name, namespace=namespace)
            logger.info(f"Deployment {name} deleted from namespace {namespace}")
            return True
        except ApiException as e:
            logger.error(f"Failed to delete deployment: {e}")
            return False
    
    def delete_service(self, name: str, namespace: str) -> bool:
        """Delete Service"""
        try:
            self.core_api.delete_namespaced_service(name=f"{name}-service", namespace=namespace)
            logger.info(f"Service {name}-service deleted from namespace {namespace}")
            return True
        except ApiException as e:
            logger.error(f"Failed to delete service: {e}")
            return False
    
    def delete_ingress(self, name: str, namespace: str) -> bool:
        """Delete Ingress"""
        try:
            self.networking_api.delete_namespaced_ingress(name=f"{name}-ingress", namespace=namespace)
            logger.info(f"Ingress {name}-ingress deleted from namespace {namespace}")
            return True
        except ApiException as e:
            logger.error(f"Failed to delete ingress: {e}")
            return False

# Singleton instance
try:
    k8s = K8sClient()
except Exception as e:
    logger.warning(f"K8s client initialization failed: {e}. Running in STUB mode.")
    k8s = None

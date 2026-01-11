"""
자동 배포 엔진
Git 저장소에서 코드를 가져와 Docker 이미지를 빌드하고 Kubernetes에 배포합니다.
"""
import os
import asyncio
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timezone
from dataclasses import dataclass

from src.core.logger import setup_logger

logger = setup_logger()

@dataclass
class DeploymentResult:
    """배포 결과"""
    status: str  # SUCCESS, FAILED
    url: Optional[str] = None
    image_tag: Optional[str] = None
    error: Optional[str] = None
    build_logs: str = ""

class AutoDeployer:
    """자동 배포 엔진"""
    
    def __init__(self, docker_registry: str = "localhost:5000"):
        self.docker_registry = docker_registry
        self.logger = logger
    
    async def deploy_from_git(
        self,
        git_repo: str,
        branch: str,
        project_name: str,
        port: int,
        env_vars: Dict[str, str],
        git_token: Optional[str] = None
    ) -> DeploymentResult:
        """
        Git 저장소에서 자동 배포
        
        Args:
            git_repo: Git 저장소 URL
            branch: 브랜치 이름
            project_name: 프로젝트 이름
            port: 컨테이너 포트
            env_vars: 환경 변수
            git_token: Git 인증 토큰 (private repo용)
        
        Returns:
            DeploymentResult
        """
        build_logs = []
        
        try:
            # 1. Git 클론
            self.logger.info("deployment_started", project=project_name, repo=git_repo)
            build_logs.append(f"[{datetime.now()}] Cloning repository...")
            
            repo_path = await self._clone_repo(git_repo, branch, git_token)
            build_logs.append(f"[{datetime.now()}] Repository cloned to {repo_path}")
            
            # 2. Dockerfile 감지
            dockerfile = await self._find_dockerfile(repo_path)
            build_logs.append(f"[{datetime.now()}] Found Dockerfile: {dockerfile}")
            
            # 3. Docker 이미지 빌드
            build_logs.append(f"[{datetime.now()}] Building Docker image...")
            image_tag = await self._build_image(repo_path, dockerfile, project_name, build_logs)
            build_logs.append(f"[{datetime.now()}] Image built: {image_tag}")
            
            # 4. Kubernetes 리소스 생성 (Stub 모드)
            build_logs.append(f"[{datetime.now()}] Creating Kubernetes resources...")
            await self._create_k8s_resources(project_name, image_tag, port, env_vars, build_logs)
            
            # 5. 도메인 할당
            subdomain = f"{project_name}.monewment.io"
            url = f"https://{subdomain}"
            build_logs.append(f"[{datetime.now()}] Deployment complete: {url}")
            
            # 정리
            shutil.rmtree(repo_path, ignore_errors=True)
            
            self.logger.info("deployment_success", project=project_name, url=url)
            
            return DeploymentResult(
                status="SUCCESS",
                url=url,
                image_tag=image_tag,
                build_logs="\n".join(build_logs)
            )
            
        except Exception as e:
            error_msg = str(e)
            build_logs.append(f"[{datetime.now()}] ERROR: {error_msg}")
            
            self.logger.error("deployment_failed", project=project_name, error=error_msg)
            
            return DeploymentResult(
                status="FAILED",
                error=error_msg,
                build_logs="\n".join(build_logs)
            )
    
    async def _clone_repo(self, git_repo: str, branch: str, git_token: Optional[str] = None) -> Path:
        """Git 저장소 클론"""
        temp_dir = tempfile.mkdtemp(prefix="monewment_deploy_")
        
        # Git 토큰이 있으면 URL에 포함
        if git_token and "github.com" in git_repo:
            git_repo = git_repo.replace("https://", f"https://{git_token}@")
        
        cmd = ["git", "clone", "-b", branch, "--depth", "1", git_repo, temp_dir]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Git clone failed: {stderr.decode()}")
        
        return Path(temp_dir)
    
    async def _find_dockerfile(self, repo_path: Path) -> Path:
        """Dockerfile 찾기"""
        # 일반적인 위치 확인
        candidates = [
            repo_path / "Dockerfile",
            repo_path / "docker" / "Dockerfile",
            repo_path / ".docker" / "Dockerfile",
        ]
        
        for dockerfile in candidates:
            if dockerfile.exists():
                return dockerfile
        
        raise Exception("Dockerfile not found in repository")
    
    async def _build_image(
        self, 
        repo_path: Path, 
        dockerfile: Path, 
        project_name: str,
        build_logs: list
    ) -> str:
        """Docker 이미지 빌드"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        image_tag = f"{self.docker_registry}/{project_name}:{timestamp}"
        
        cmd = [
            "docker", "build",
            "-f", str(dockerfile),
            "-t", image_tag,
            str(repo_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        
        # 실시간 로그 수집
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            log_line = line.decode().strip()
            build_logs.append(log_line)
        
        await process.wait()
        
        if process.returncode != 0:
            raise Exception("Docker build failed")
        
        return image_tag
    
    async def _create_k8s_resources(
        self,
        project_name: str,
        image_tag: str,
        port: int,
        env_vars: Dict[str, str],
        build_logs: list
    ):
        """Kubernetes 리소스 생성 (실제 구현)"""
        from src.core.k8s_client import k8s
        
        namespace = "monewment"  # 또는 프로젝트별 namespace
        
        if not k8s:
            # Stub 모드
            build_logs.append(f"[STUB] Creating Deployment: {project_name}")
            build_logs.append(f"[STUB] Image: {image_tag}")
            build_logs.append(f"[STUB] Port: {port}")
            build_logs.append(f"[STUB] Environment variables: {len(env_vars)} vars")
            build_logs.append(f"[STUB] Creating Service: {project_name}-service")
            build_logs.append(f"[STUB] Creating Ingress: {project_name}-ingress")
            self.logger.info("k8s_resources_created", project=project_name, mode="STUB")
            return
        
        # 실제 Kubernetes 리소스 생성
        try:
            # 1. Secret 생성 (환경 변수)
            if env_vars:
                build_logs.append(f"Creating Secret: {project_name}-secrets")
                success = k8s.create_secret(
                    name=f"{project_name}-secrets",
                    namespace=namespace,
                    data=env_vars
                )
                if not success:
                    raise Exception("Failed to create Secret")
            
            # 2. Deployment 생성
            build_logs.append(f"Creating Deployment: {project_name}")
            success = k8s.create_deployment(
                name=project_name,
                namespace=namespace,
                image=image_tag,
                port=port,
                replicas=1,
                env_vars=env_vars if env_vars else None
            )
            if not success:
                raise Exception("Failed to create Deployment")
            
            # 3. Service 생성
            build_logs.append(f"Creating Service: {project_name}-service")
            success = k8s.create_service(
                name=project_name,
                namespace=namespace,
                port=80,
                target_port=port
            )
            if not success:
                raise Exception("Failed to create Service")
            
            # 4. Ingress 생성
            subdomain = f"{project_name}.monewment.io"
            build_logs.append(f"Creating Ingress: {project_name}-ingress")
            success = k8s.create_ingress(
                name=project_name,
                namespace=namespace,
                host=subdomain,
                service_name=f"{project_name}-service",
                service_port=80
            )
            if not success:
                raise Exception("Failed to create Ingress")
            
            self.logger.info("k8s_resources_created", 
                project=project_name, 
                mode="REAL",
                namespace=namespace
            )
            
        except Exception as e:
            error_msg = f"Kubernetes resource creation failed: {str(e)}"
            build_logs.append(f"[ERROR] {error_msg}")
            self.logger.error("k8s_creation_failed", project=project_name, error=str(e))
            raise Exception(error_msg)

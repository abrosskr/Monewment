# 🧩 Functional Specification

> **Last Updated:** 2026-01-24 22:17:52

## 📄 src\ant_client\app.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `MockVaultDownloader` | `class MockVaultDownloader` | 설명 없음 |
| ⓒ Class | `MockVaultUploader` | `class MockVaultUploader` | 설명 없음 |
| ⓒ Class | `AntWorker` | `class AntWorker` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, client_id, token)` | 설명 없음 |
| Ⓜ️ Function | `update_token` | `update_token(self, token)` | 설명 없음 |
| Ⓜ️ Function | `run` | `run(self)` | 설명 없음 |
| Ⓜ️ Function | `stop` | `stop(self)` | 설명 없음 |
| Ⓜ️ Function | `ensure_single_instance` | `ensure_single_instance()` | 설명 없음 |
| ⓒ Class | `MonewmentApp` | `class MonewmentApp` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self)` | 설명 없음 |
| Ⓜ️ Function | `on_auth_success` | `on_auth_success(self, token)` | 설명 없음 |
| Ⓜ️ Function | `start_worker` | `start_worker(self, token)` | 설명 없음 |
| Ⓜ️ Function | `on_exit` | `on_exit(self)` | 설명 없음 |
| Ⓜ️ Function | `run` | `run(self)` | 설명 없음 |
| Ⓜ️ Function | `main` | `main()` | 설명 없음 |

---

## 📄 src\ant_client\core\connection.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `ConnectionManager` | `class ConnectionManager` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, server_url, client_id, security)` | 설명 없음 |
| Ⓜ️ Function | `set_executor` | `set_executor(self, executor)` | 설명 없음 |
| Ⓜ️ Function | `set_p2p_callback` | `set_p2p_callback(self, callback)` | 설명 없음 |

---

## 📄 src\ant_client\core\executor.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `JobExecutor` | `class JobExecutor` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, client_id, vault_downloader, vault_uploader)` | 설명 없음 |

---

## 📄 src\ant_client\core\p2p\engine.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `P2PEngine` | `class P2PEngine` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, p2p_id, port)` | 설명 없음 |
| Ⓜ️ Function | `set_relay_transport` | `set_relay_transport(self, callback)` | Sets the callback for sending packets via Queen Relay. |
| Ⓜ️ Function | `stop` | `stop(self)` | 설명 없음 |

---

## 📄 src\ant_client\core\p2p\protocol.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `P2PProtocol` | `class P2PProtocol` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, engine)` | 설명 없음 |
| Ⓜ️ Function | `connection_made` | `connection_made(self, transport)` | 설명 없음 |
| Ⓜ️ Function | `datagram_received` | `datagram_received(self, data, addr)` | Packet Format: [MAGIC(4)] [TYPE(1)] [PAYLOAD_LEN(4)] [PAYLOAD(N)] |
| Ⓜ️ Function | `send_message` | `send_message(self, msg_type, data, addr)` | 설명 없음 |
| Ⓜ️ Function | `set_relay_transport` | `set_relay_transport(self, callback)` | 설명 없음 |

---

## 📄 src\ant_client\core\render\blender_ops.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `BlenderOps` | `class BlenderOps` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, blender_path)` | 설명 없음 |

---

## 📄 src\ant_client\core\updater.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `AntUpdater` | `class AntUpdater` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, current_version, server_url)` | 설명 없음 |
| Ⓜ️ Function | `_verify_hash` | `_verify_hash(self, file_path, expected_hash)` | 설명 없음 |
| Ⓜ️ Function | `_is_newer` | `_is_newer(self, remote_ver)` | 설명 없음 |
| Ⓜ️ Function | `to_int` | `to_int(v)` | 설명 없음 |

---

## 📄 src\ant_client\core\vault\shredder.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `VaultShredder` | `class VaultShredder` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self)` | 설명 없음 |
| Ⓜ️ Function | `process_file` | `process_file(self, file_path)` | Reads file -> Encrypts -> Shards. |
| Ⓜ️ Function | `recover_file` | `recover_file(self, shards, key_hex, original_size)` | Shards -> Reassemble (EC) -> Decrypt -> Raw Data |

---

## 📄 src\ant_client\core\watchdog.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `Watchdog` | `class Watchdog` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, target_script)` | 설명 없음 |
| Ⓜ️ Function | `start_worker` | `start_worker(self)` | Starts the worker process. |
| Ⓜ️ Function | `monitor` | `monitor(self)` | Monitors the worker process and restarts if it dies. |
| Ⓜ️ Function | `stop` | `stop(self)` | 설명 없음 |

---

## 📄 src\ant_client\main.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| Ⓜ️ Function | `main` | `main()` | 설명 없음 |

---

## 📄 src\ant_client\repair_agent.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `RepairAgent` | `class RepairAgent` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, api_url, api_key, p2p_engine)` | 설명 없음 |

---

## 📄 src\ant_client\ui\dashboard.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `AntDashboard` | `class AntDashboard` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, on_auth_success)` | 설명 없음 |
| Ⓜ️ Function | `_find_edge` | `_find_edge(self)` | Locate Microsoft Edge executable on Windows |
| Ⓜ️ Function | `start` | `start(self, url, hidden)` | 설명 없음 |
| Ⓜ️ Function | `show` | `show(self)` | 설명 없음 |
| Ⓜ️ Function | `hide` | `hide(self)` | 설명 없음 |
| Ⓜ️ Function | `load_config` | `load_config(self)` | Load persistent config from disk |
| Ⓜ️ Function | `save_config` | `save_config(self, config)` | Save config to disk |
| Ⓜ️ Function | `navigate` | `navigate(self, url)` | 설명 없음 |
| Ⓜ️ Function | `resize` | `resize(self, width, height)` | 설명 없음 |

---

## 📄 src\ant_client\ui\tray.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `AntTray` | `class AntTray` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, on_exit_callback, dashboard)` | 설명 없음 |
| Ⓜ️ Function | `create_image` | `create_image(self, width, height)` | 설명 없음 |
| Ⓜ️ Function | `on_open_dashboard` | `on_open_dashboard(self, icon, item)` | 설명 없음 |
| Ⓜ️ Function | `on_exit` | `on_exit(self, icon, item)` | 설명 없음 |
| Ⓜ️ Function | `run` | `run(self)` | 설명 없음 |

---

## 📄 src\ant_client\vault_downloader.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `VaultDownloader` | `class VaultDownloader` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, api_url, api_key, p2p_engine)` | 설명 없음 |
| Ⓜ️ Function | `on_shard_received` | `on_shard_received(self, shard_index, data)` | Callback for P2P Engine when a shard arrives |

---

## 📄 src\ant_client\vault_uploader.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `VaultUploader` | `class VaultUploader` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, api_url, api_key, p2p_engine)` | 설명 없음 |

---

## 📄 src\api\v1\admin\dashboard.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| Ⓜ️ Function | `get_real_db_schema` | `get_real_db_schema()` | [최적화] DB Inspector를 통해 실제 테이블 구조를 반환합니다. |
| Ⓜ️ Function | `get_real_api_endpoints` | `get_real_api_endpoints()` | [신규] FastAPI 라우트 정보를 실시간으로 추출하여 반환합니다. |

---

## 📄 src\api\v1\endpoints\billing.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `ChargeRequest` | `class ChargeRequest` | 설명 없음 |
| ⓒ Class | `BalanceResponse` | `class BalanceResponse` | 설명 없음 |

---

## 📄 src\api\v1\endpoints\deploy.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `AutoDeployRequest` | `class AutoDeployRequest` | 설명 없음 |
| ⓒ Class | `DeploymentStatusResponse` | `class DeploymentStatusResponse` | 설명 없음 |
| ⓒ Class | `BuildLogResponse` | `class BuildLogResponse` | 설명 없음 |

---

## 📄 src\api\v1\endpoints\email_service.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `EmailRequest` | `class EmailRequest` | 설명 없음 |
| ⓒ Class | `VerifyRequest` | `class VerifyRequest` | 설명 없음 |

---

## 📄 src\api\v1\endpoints\projects.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| Ⓜ️ Function | `get_project_tree` | `get_project_tree(project_name)` | [신규] 특정 프로젝트 폴더의 실시간 구조 트리를 반환합니다. |

---

## 📄 src\api\v1\endpoints\services.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| Ⓜ️ Function | `get_services_list` | `get_services_list()` | 플랫폼에서 제공하는 설치 가능 및 설치된 기능 목록을 조회합니다. |
| Ⓜ️ Function | `update_api_key` | `update_api_key(req)` | Gemini 또는 OpenAI의 API 키를 .env 파일에 안전하게 업데이트합니다. |

---

## 📄 src\api\v1\endpoints\vm.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `VMCreateRequest` | `class VMCreateRequest` | 설명 없음 |
| ⓒ Class | `VMSwitchModelRequest` | `class VMSwitchModelRequest` | 설명 없음 |
| ⓒ Class | `VMStatusResponse` | `class VMStatusResponse` | 설명 없음 |
| Ⓜ️ Function | `calculate_cost` | `calculate_cost(usage, end_time)` | 설명 없음 |

---

## 📄 src\api\v1\render\router.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `JobDatabase` | `class JobDatabase` | 설명 없음 |
| Ⓜ️ Function | `add_job` | `add_job(cls, job)` | 설명 없음 |
| Ⓜ️ Function | `add_result` | `add_result(cls, res)` | 설명 없음 |
| Ⓜ️ Function | `get_all` | `get_all(cls)` | 설명 없음 |

---

## 📄 src\api\v1\vault\manager.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `UploadInitRequest` | `class UploadInitRequest` | 설명 없음 |
| ⓒ Class | `UploadInitRequest` | `class UploadInitRequest` | 설명 없음 |
| ⓒ Class | `ShardAssignment` | `class ShardAssignment` | 설명 없음 |
| ⓒ Class | `UploadInitResponse` | `class UploadInitResponse` | 설명 없음 |
| ⓒ Class | `ShardReport` | `class ShardReport` | 설명 없음 |
| ⓒ Class | `UploadCompleteRequest` | `class UploadCompleteRequest` | 설명 없음 |
| ⓒ Class | `DownloadInitRequest` | `class DownloadInitRequest` | 설명 없음 |
| ⓒ Class | `DownloadShardInfo` | `class DownloadShardInfo` | 설명 없음 |
| ⓒ Class | `DownloadInitResponse` | `class DownloadInitResponse` | 설명 없음 |
| ⓒ Class | `RepairInitRequest` | `class RepairInitRequest` | 설명 없음 |

---

## 📄 src\api\v1\vault\tracker.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `PeerAnnounce` | `class PeerAnnounce` | 설명 없음 |
| ⓒ Class | `PeerInfo` | `class PeerInfo` | 설명 없음 |

---

## 📄 src\api\v1\vault\watchdog.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `VaultWatchdog` | `class VaultWatchdog` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, db)` | 설명 없음 |

---

## 📄 src\common\erasure_coding.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `ErasureCoding` | `class ErasureCoding` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, n, m)` | N: Original Data Shards |
| Ⓜ️ Function | `encode` | `encode(self, data)` | Striped Encoding (RAID-style). |
| Ⓜ️ Function | `decode` | `decode(self, shards)` | Striped Decoding. |

---

## 📄 src\config.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `Settings` | `class Settings` | 설명 없음 |
| Ⓜ️ Function | `SQLALCHEMY_DATABASE_URI` | `SQLALCHEMY_DATABASE_URI(self)` | 설명 없음 |
| Ⓜ️ Function | `ALLOWED_ORIGINS_LIST` | `ALLOWED_ORIGINS_LIST(self)` | CORS 허용 도메인 리스트 반환 |
| Ⓜ️ Function | `validate_security_keys` | `validate_security_keys(self)` | 보안 키 검증 |
| Ⓜ️ Function | `PROJECTS_DIR` | `PROJECTS_DIR(self)` | 설명 없음 |
| Ⓜ️ Function | `TEMPLATES_DIR` | `TEMPLATES_DIR(self)` | 설명 없음 |
| Ⓜ️ Function | `ENV_FILE_PATH` | `ENV_FILE_PATH(self)` | 설명 없음 |

---

## 📄 src\core\ant_security.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `AntSecurity` | `class AntSecurity` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, key_bytes)` | Initialize with a 32-byte (256-bit) key. |
| Ⓜ️ Function | `generate_key` | `generate_key()` | 설명 없음 |
| Ⓜ️ Function | `encrypt_payload` | `encrypt_payload(self, data)` | Encrypts a dictionary payload into a base64 encoded string. |
| Ⓜ️ Function | `decrypt_payload` | `decrypt_payload(self, token)` | Decrypts a token string back into a dictionary. |

---

## 📄 src\core\billing\profit_engine.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `GpuType` | `class GpuType` | 설명 없음 |
| ⓒ Class | `GpuSpec` | `class GpuSpec` | 설명 없음 |
| ⓒ Class | `ProfitCalculationRequest` | `class ProfitCalculationRequest` | 설명 없음 |
| ⓒ Class | `ProfitCalculationResponse` | `class ProfitCalculationResponse` | 설명 없음 |
| ⓒ Class | `ProfitEngine` | `class ProfitEngine` | 설명 없음 |
| Ⓜ️ Function | `calculate_profit` | `calculate_profit(request)` | 설명 없음 |

---

## 📄 src\core\cluster_manager.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `ClusterManager` | `class ClusterManager` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self)` | 설명 없음 |
| Ⓜ️ Function | `get_instance` | `get_instance(cls)` | 설명 없음 |
| Ⓜ️ Function | `get_client` | `get_client(self, cluster_id)` | Returns the specific K8s client for the requested cluster ID. |
| Ⓜ️ Function | `get_client_by_project` | `get_client_by_project(self, project)` | Helper: Resolves K8s client directly from Project object. |

---

## 📄 src\core\deployer.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `DeploymentResult` | `class DeploymentResult` | 배포 결과 |
| ⓒ Class | `AutoDeployer` | `class AutoDeployer` | 자동 배포 엔진 |
| Ⓜ️ Function | `__init__` | `__init__(self, docker_registry)` | 설명 없음 |

---

## 📄 src\core\devtools\inspectors\config.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `ConfigInspector` | `class ConfigInspector` | 설명 없음 |
| Ⓜ️ Function | `inspect` | `inspect(self, root_dir)` | 설명 없음 |
| Ⓜ️ Function | `_extract_value` | `_extract_value(self, node_value)` | AST 노드에서 값을 추출하는 헬퍼 메서드 (중복 제거 및 최적화) |

---

## 📄 src\core\devtools\inspectors\database.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `DatabaseInspector` | `class DatabaseInspector` | 설명 없음 |
| Ⓜ️ Function | `inspect` | `inspect(self, root_dir)` | 설명 없음 |
| Ⓜ️ Function | `_get_type_name` | `_get_type_name(self, node)` | 설명 없음 |

---

## 📄 src\core\devtools\inspectors\network.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `NetworkInspector` | `class NetworkInspector` | 설명 없음 |
| Ⓜ️ Function | `inspect` | `inspect(self, root_dir)` | 설명 없음 |
| Ⓜ️ Function | `_analyze_file` | `_analyze_file(self, file_path, title)` | 파일 단위 분석 로직 (중복 제거 및 최적화) |

---

## 📄 src\core\devtools\inspectors\structure.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `StructureInspector` | `class StructureInspector` | 설명 없음 |
| Ⓜ️ Function | `inspect` | `inspect(self, root_dir)` | 설명 없음 |

---

## 📄 src\core\devtools\manager.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `DevToolsManager` | `class DevToolsManager` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, root_dir)` | 설명 없음 |
| Ⓜ️ Function | `run_all_inspections` | `run_all_inspections(self)` | 모든 감시를 수행하고 파일로 저장 |
| Ⓜ️ Function | `_save` | `_save(self, filename, content)` | 설명 없음 |

---

## 📄 src\core\devtools\watcher.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `ProWatcher` | `class ProWatcher` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, root_dir)` | 설명 없음 |
| Ⓜ️ Function | `on_any_event` | `on_any_event(self, event)` | 설명 없음 |
| Ⓜ️ Function | `start_watching` | `start_watching(root_dir)` | 설명 없음 |

---

## 📄 src\core\email_utils.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `EmailUtils` | `class EmailUtils` | 설명 없음 |
| Ⓜ️ Function | `validate_format` | `validate_format(email)` | 이메일 형식이 유효한지 검사합니다. |

---

## 📄 src\core\env_crypto.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `EnvCrypto` | `class EnvCrypto` | 환경 변수 암호화/복호화 |
| Ⓜ️ Function | `__init__` | `__init__(self)` | 설명 없음 |
| Ⓜ️ Function | `encrypt` | `encrypt(self, value)` | 값 암호화 |
| Ⓜ️ Function | `decrypt` | `decrypt(self, encrypted)` | 값 복호화 |

---

## 📄 src\core\k8s_client.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `K8sClient` | `class K8sClient` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, api_client)` | Initialize K8s Client. |
| Ⓜ️ Function | `create_deployment` | `create_deployment(self, name, namespace, image, port, replicas, env_vars)` | Create Kubernetes Deployment |
| Ⓜ️ Function | `create_service` | `create_service(self, name, namespace, port, target_port)` | Create Kubernetes Service |
| Ⓜ️ Function | `create_ingress` | `create_ingress(self, name, namespace, host, service_name, service_port)` | Create Kubernetes Ingress |
| Ⓜ️ Function | `create_secret` | `create_secret(self, name, namespace, data)` | Create Kubernetes Secret |
| Ⓜ️ Function | `delete_deployment` | `delete_deployment(self, name, namespace)` | Delete Deployment |
| Ⓜ️ Function | `delete_service` | `delete_service(self, name, namespace)` | Delete Service |
| Ⓜ️ Function | `delete_ingress` | `delete_ingress(self, name, namespace)` | Delete Ingress |

---

## 📄 src\core\logger.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| Ⓜ️ Function | `mask_sensitive_data` | `mask_sensitive_data(logger, method_name, event_dict)` | 민감한 정보를 마스킹하는 프로세서 |
| Ⓜ️ Function | `setup_logger` | `setup_logger()` | Configures structlog for JSON output (production-ready) |

---

## 📄 src\core\protocol.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `JobType` | `class JobType` | 설명 없음 |
| ⓒ Class | `JobStatus` | `class JobStatus` | 설명 없음 |
| ⓒ Class | `JobRequest` | `class JobRequest` | User -> Queen -> Ant |
| ⓒ Class | `JobResult` | `class JobResult` | Ant -> Queen -> User (via API/DB) |

---

## 📄 src\core\redis_client.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `RedisManager` | `class RedisManager` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self)` | 설명 없음 |
| Ⓜ️ Function | `get_instance` | `get_instance(cls)` | 설명 없음 |
| Ⓜ️ Function | `get_client` | `get_client(self)` | Redis 클라이언트 반환. 연결되지 않은 경우 None 반환. |

---

## 📄 src\core\scheduler.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `AntNodeInfo` | `class AntNodeInfo` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, client_id, gpu_model, status, last_seen)` | 설명 없음 |
| Ⓜ️ Function | `is_online` | `is_online(self)` | 설명 없음 |
| ⓒ Class | `Scheduler` | `class Scheduler` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self)` | 설명 없음 |

---

## 📄 src\core\security.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| Ⓜ️ Function | `hash_password` | `hash_password(password)` | 평문 비밀번호를 Bcrypt 해시로 변환합니다. |
| Ⓜ️ Function | `verify_password` | `verify_password(plain_password, hashed_password)` | 평문 비밀번호와 해시된 비밀번호가 일치하는지 검증합니다. |
| Ⓜ️ Function | `create_access_token` | `create_access_token(data, expires_delta)` | 사용자 정보를 담은 서명된 JWT 토큰을 생성합니다. |
| Ⓜ️ Function | `validate_project_path` | `validate_project_path(project_name)` | Project 이름이 유효한지 검사하고, 상위 폴더 접근(Path Traversal)을 차단합니다. |
| Ⓜ️ Function | `generate_api_key` | `generate_api_key()` | 안전한 랜덤 API 키를 생성합니다. (Prefix: sk_live_) |
| Ⓜ️ Function | `hash_api_key` | `hash_api_key(api_key)` | API 키를 SHA-256으로 해싱합니다. |

---

## 📄 src\core\socket_manager.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `SocketManager` | `class SocketManager` | 설명 없음 |
| Ⓜ️ Function | `__new__` | `__new__(cls)` | 설명 없음 |
| Ⓜ️ Function | `get_instance` | `get_instance(cls)` | 설명 없음 |
| Ⓜ️ Function | `disconnect` | `disconnect(self, client_id)` | 설명 없음 |
| Ⓜ️ Function | `get_connection` | `get_connection(self, client_id)` | 설명 없음 |

---

## 📄 src\core\worker.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `WorkerSettings` | `class WorkerSettings` | 설명 없음 |

---

## 📄 src\main.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| Ⓜ️ Function | `read_root` | `read_root()` | 시스템 헬스 체크 및 현재 가동 모드를 확인합니다. |

---

## 📄 src\middleware\request_id.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `RequestIDMiddleware` | `class RequestIDMiddleware` | 모든 요청에 고유한 request_id를 추가하는 미들웨어 |

---

## 📄 src\models.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `UserRole` | `class UserRole` | 설명 없음 |
| ⓒ Class | `RoomStatus` | `class RoomStatus` | 설명 없음 |
| ⓒ Class | `Organization` | `class Organization` | [ProjectClient] 법인격 껍데기 |
| ⓒ Class | `User` | `class User` | [GeneralUser] 실제 사용자 |
| ⓒ Class | `Project` | `class Project` | [신규 추가] 프로젝트 메타데이터 |
| ⓒ Class | `ProjectMember` | `class ProjectMember` | [신규 추가] 프로젝트 멤버 (매핑 테이블) |
| ⓒ Class | `Cluster` | `class Cluster` | [Infrastructure] 물리적/논리적 리소스 클러스터 |
| ⓒ Class | `PolicyPreset` | `class PolicyPreset` | 설명 없음 |
| ⓒ Class | `Room` | `class Room` | 설명 없음 |
| ⓒ Class | `AuditLog` | `class AuditLog` | 설명 없음 |
| ⓒ Class | `SubscriptionPlan` | `class SubscriptionPlan` | [Billing] 월 정액 구독 플랜 (Product) |
| ⓒ Class | `ProjectSubscription` | `class ProjectSubscription` | [Billing] 프로젝트별 구독 현황 |
| ⓒ Class | `ProjectBudget` | `class ProjectBudget` | [Guardrails] 프로젝트별 예산 설정 및 현재 사용량 캐싱 |
| ⓒ Class | `PaymentHistory` | `class PaymentHistory` | [Payment] 결제 내역 (Audit Log) |
| ⓒ Class | `VMFlavor` | `class VMFlavor` | [Billing] VM 하드웨어 상품 (Pricing Catalog) |
| ⓒ Class | `AIModel` | `class AIModel` | [Billing] AI 모델 소프트웨어 상품 (Pricing Catalog) |
| ⓒ Class | `VMInstance` | `class VMInstance` | [Resource] 생성된 가상머신 (Business Object) |
| ⓒ Class | `VMUsage` | `class VMUsage` | [Billing] 과금 이력 세션 (Immutable History) |
| ⓒ Class | `VaultFile` | `class VaultFile` | [Storage] 업로드된 파일의 메타데이터 (File System Layer) |
| ⓒ Class | `VaultShard` | `class VaultShard` | [Storage] 파일 조각의 위치 정보 (Location Map) |
| ⓒ Class | `DeploymentConfig` | `class DeploymentConfig` | [Autonomous] 자동 배포 설정 |
| ⓒ Class | `ServiceEndpoint` | `class ServiceEndpoint` | [Autonomous] 서비스 엔드포인트 및 도메인 관리 |
| ⓒ Class | `EnvironmentVariable` | `class EnvironmentVariable` | [Autonomous] 환경 변수 보안 저장 |
| ⓒ Class | `BuildLog` | `class BuildLog` | [Autonomous] 빌드 및 배포 로그 |

---

## 📄 src\routers\devtools.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| Ⓜ️ Function | `get_current_schema` | `get_current_schema()` | [유료 기능] 현재 프로젝트의 DB 스키마를 분석해서 JSON으로 반환합니다. |

---

## 📄 src\routers\tools.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| Ⓜ️ Function | `generate_tree_api` | `generate_tree_api(file_paths)` | 파일 경로 리스트를 받아서 마크다운 트리로 변환 |
| Ⓜ️ Function | `draw_tree` | `draw_tree(current_tree, prefix)` | 설명 없음 |

---

## 📄 src\routers\ui_factory.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `UIRequest` | `class UIRequest` | 설명 없음 |
| Ⓜ️ Function | `generate_react_code` | `generate_react_code(name, spec)` | 설명 없음 |

---

## 📄 src\schemas.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `BaseSchema` | `class BaseSchema` | 설명 없음 |
| ⓒ Class | `UserCreate` | `class UserCreate` | 설명 없음 |
| ⓒ Class | `UserResponse` | `class UserResponse` | 설명 없음 |
| ⓒ Class | `PolicyCreate` | `class PolicyCreate` | 설명 없음 |
| ⓒ Class | `PolicyResponse` | `class PolicyResponse` | 설명 없음 |
| ⓒ Class | `ProjectCreate` | `class ProjectCreate` | 설명 없음 |
| ⓒ Class | `ProjectResponse` | `class ProjectResponse` | 설명 없음 |
| ⓒ Class | `RoomCreate` | `class RoomCreate` | 설명 없음 |
| ⓒ Class | `RoomResponse` | `class RoomResponse` | 설명 없음 |
| ⓒ Class | `APIResponse` | `class APIResponse` | 표준 API 응답 형식 |
| ⓒ Class | `HealthCheckResponse` | `class HealthCheckResponse` | Health Check 응답 형식 |
| ⓒ Class | `SignupRequest` | `class SignupRequest` | 설명 없음 |
| ⓒ Class | `LoginRequest` | `class LoginRequest` | 설명 없음 |
| ⓒ Class | `CreateProjectRequest` | `class CreateProjectRequest` | 설명 없음 |
| ⓒ Class | `ApiKeyUpdate` | `class ApiKeyUpdate` | 설명 없음 |
| ⓒ Class | `ChatRequest` | `class ChatRequest` | 설명 없음 |
| ⓒ Class | `InstallRequest` | `class InstallRequest` | 설명 없음 |
| ⓒ Class | `EnvUpdateRequest` | `class EnvUpdateRequest` | 설명 없음 |
| ⓒ Class | `PricingUpdateRequest` | `class PricingUpdateRequest` | 설명 없음 |
| ⓒ Class | `ClusterCreateRequest` | `class ClusterCreateRequest` | 설명 없음 |
| ⓒ Class | `OrgApproveRequest` | `class OrgApproveRequest` | 설명 없음 |
| ⓒ Class | `ProjectExpandRequest` | `class ProjectExpandRequest` | 설명 없음 |

---

## 📄 src\services\billing.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `PaymentGatewayError` | `class PaymentGatewayError` | 설명 없음 |
| ⓒ Class | `BillingService` | `class BillingService` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, db)` | 설명 없음 |
| Ⓜ️ Function | `_mock_process_payment` | `_mock_process_payment(self, amount, token)` | Simulates interacting with Stripe API. |

---

## 📄 src\services\metering.py

| Type | Name | Signature | Description |
|:---:|:---|:---|:---|
| ⓒ Class | `MeteringService` | `class MeteringService` | 설명 없음 |
| Ⓜ️ Function | `__init__` | `__init__(self, db)` | 설명 없음 |
| Ⓜ️ Function | `start_session` | `start_session(self, vm_id, ai_model_id)` | Starts a new metering session. |
| Ⓜ️ Function | `end_session` | `end_session(self, vm_id)` | Ends the currently active session for a VM. |
| Ⓜ️ Function | `_update_project_spend` | `_update_project_spend(self, project_id, added_cost)` | Increments the current_month_spend in ProjectBudget |
| Ⓜ️ Function | `get_project_current_usage` | `get_project_current_usage(self, project_id)` | Returns { |
| Ⓜ️ Function | `check_eligibility` | `check_eligibility(self, project_id)` | [Hybrid Model Logic] |

---

*Generated by Monewment Auto-Doc System v5.0*

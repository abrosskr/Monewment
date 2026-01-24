# 📋 API List

> **Last Updated:** 2026-01-24 22:17:51
> **Total APIs:** 52

| Method | Path | Function | Description | Source |
|:---:|:---|:---|:---|:---|
| 🔵 GET | `/` | `read_root` | 시스템 헬스 체크 및 현재 가동 모드를 확인합니다. | `src\main.py` |
| 🟢 POST | `/` | `chat_with_agent` | 실시간 로그를 컨텍스트로 사용하여 AI 에이전트와 대화하고 해결책을 구합니다. | `src\api\v1\endpoints\chat.py` |
| 🔵 GET | `/analyze/schema` | `get_current_schema` | [유료 기능] 현재 프로젝트의 DB 스키마를 분석해서 JSON으로 반환합니다. | `src\routers\devtools.py` |
| 🟢 POST | `/api-key` | `create_api_key` | Create api key | `src\api\v1\endpoints\auth.py` |
| 🟢 POST | `/auto-deploy` | `auto_deploy` | Auto deploy | `src\api\v1\endpoints\deploy.py` |
| 🔵 GET | `/balance/{project_id}` | `get_balance` | Get balance | `src\api\v1\endpoints\billing.py` |
| 🟢 POST | `/charge` | `charge_project` | Charge project | `src\api\v1\endpoints\billing.py` |
| 🟢 POST | `/clusters` | `create_cluster` | Create cluster | `src\api\v1\admin\dashboard.py` |
| 🟢 POST | `/create` | `create_project_saas` | Create project saas | `src\api\v1\endpoints\projects.py` |
| 🔴 DEL | `/deployments/{project_id}` | `delete_deployment` | Delete deployment | `src\api\v1\endpoints\deploy.py` |
| 🔵 GET | `/deployments/{project_id}` | `get_deployment_status` | Get deployment status | `src\api\v1\endpoints\deploy.py` |
| 🔵 GET | `/deployments/{project_id}/logs` | `get_build_logs` | Get build logs | `src\api\v1\endpoints\deploy.py` |
| 🔵 GET | `/endpoints` | `get_real_api_endpoints` | [신규] FastAPI 라우트 정보를 실시간으로 추출하여 반환합니다. | `src\api\v1\admin\dashboard.py` |
| 🟢 POST | `/generate` | `generate_data` | Generate data | `src\api\v1\sync\router.py` |
| 🟢 POST | `/generate` | `generate_ui` | Generate ui | `src\routers\ui_factory.py` |
| 🟢 POST | `/generate-tree` | `generate_tree_api` | Generate tree api | `src\routers\tools.py` |
| 🔵 GET | `/health` | `health_check` | Health check | `src\main.py` |
| 🔵 GET | `/hierarchy` | `get_system_hierarchy` | Get system hierarchy | `src\api\v1\admin\dashboard.py` |
| 🔵 GET | `/jobs` | `list_jobs` | [Admin] List all jobs. | `src\api\v1\render\router.py` |
| 🟢 POST | `/jobs` | `submit_render_job` | Submit render job | `src\api\v1\render\router.py` |
| 🟢 POST | `/keys` | `update_api_key` | Gemini 또는 OpenAI의 API 키를 .env 파일에 안전하게 업데이트합니다. | `src\api\v1\endpoints\services.py` |
| 🔵 GET | `/list` | `get_ant_list` | Get list of all connected Ants with details. | `src\api\v1\admin\monitoring.py` |
| 🔵 GET | `/list` | `get_services_list` | 플랫폼에서 제공하는 설치 가능 및 설치된 기능 목록을 조회합니다. | `src\api\v1\endpoints\services.py` |
| 🟢 POST | `/login` | `login` | Login | `src\api\v1\endpoints\auth.py` |
| 🟢 POST | `/manager/download/init` | `init_download` | Init download | `src\api\v1\vault\manager.py` |
| 🟢 POST | `/manager/maintenance/scan` | `trigger_maintenance` | Trigger maintenance | `src\api\v1\vault\manager.py` |
| 🔵 GET | `/manager/proxy/{file_id}` | `proxy_download_file` | Proxy download file | `src\api\v1\vault\manager.py` |
| 🟢 POST | `/manager/repair/init` | `init_repair` | Init repair | `src\api\v1\vault\manager.py` |
| 🟢 POST | `/manager/upload/complete` | `complete_upload` | Complete upload | `src\api\v1\vault\manager.py` |
| 🟢 POST | `/manager/upload/init` | `init_upload` | Init upload | `src\api\v1\vault\manager.py` |
| 🟢 POST | `/manager/upload/verify_header` | `verify_upload_header` | Verify upload header | `src\api\v1\vault\manager.py` |
| 🔵 GET | `/me` | `read_users_me` | Read users me | `src\api\v1\endpoints\auth.py` |
| 🟢 POST | `/organizations/approve` | `approve_organization` | Approve organization | `src\api\v1\admin\dashboard.py` |
| 🔵 GET | `/ping` | `ping` | Ping | `src\main.py` |
| 🔵 GET | `/pricing/flavors` | `get_flavors` | Get flavors | `src\api\v1\admin\dashboard.py` |
| ⚪ PATCH | `/pricing/flavors/{flavor_id}` | `update_flavor_rate` | Update flavor rate | `src\api\v1\admin\dashboard.py` |
| 🟢 POST | `/projects/expand` | `expand_project_topdown` | Expand project topdown | `src\api\v1\admin\dashboard.py` |
| 🔵 GET | `/schema` | `get_real_db_schema` | [최적화] DB Inspector를 통해 실제 테이블 구조를 반환합니다. | `src\api\v1\admin\dashboard.py` |
| 🟢 POST | `/send-verification` | `send_verification` | 이메일로 인증 코드를 발송합니다. | `src\api\v1\endpoints\email_service.py` |
| 🟢 POST | `/signup` | `signup` | Signup | `src\api\v1\endpoints\auth.py` |
| 🔵 GET | `/stats` | `get_admin_stats` | Get admin stats | `src\api\v1\admin\dashboard.py` |
| 🔵 GET | `/status` | `get_grid_status` | Get aggregate status of the DeepSync Grid. | `src\api\v1\admin\monitoring.py` |
| 🟢 POST | `/sync_token` | `sync_ant_token` | [Phase 10] Hand over a JWT token from Web UI to the target Ant Client. | `src\api\v1\admin\monitoring.py` |
| 🔵 GET | `/tasks/{task_id}` | `get_task_status` | Get task status | `src\api\v1\sync\router.py` |
| 🟢 POST | `/tracker/announce` | `announce_files` | Announce files | `src\api\v1\vault\tracker.py` |
| 🔵 GET | `/tracker/peers/{file_hash}` | `find_peers` | Find peers | `src\api\v1\vault\tracker.py` |
| 🟢 POST | `/validate` | `validate_email_format` | 이메일 주소의 형식이 올바른지 검사합니다. | `src\api\v1\endpoints\email_service.py` |
| 🟢 POST | `/verify-code` | `verify_code` | 이메일 인증 코드를 검증합니다. | `src\api\v1\endpoints\email_service.py` |
| 🔵 GET | `/vms` | `get_all_vms` | Get all vms | `src\api\v1\admin\dashboard.py` |
| 🔴 DEL | `/{name}` | `delete_vm` | Delete vm | `src\api\v1\endpoints\vm.py` |
| 🟢 POST | `/{name}/switch_model` | `switch_model` | Switch model | `src\api\v1\endpoints\vm.py` |
| 🔵 GET | `/{project_name}/structure` | `get_project_tree` | [신규] 특정 프로젝트 폴더의 실시간 구조 트리를 반환합니다. | `src\api\v1\endpoints\projects.py` |

*Generated by Monewment Auto-Doc System v5.0*

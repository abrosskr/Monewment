# 📂 Project Structure Map

📦 Monewment
├── 📂 .github/
│   └── 📂 workflows/
│       └── 📄 ci.yml
├── 📂 assets/
├── 📂 docs/
│   ├── 📂 auto_generated/
│   │   ├── 📄 API_LIST.md
│   │   ├── 📄 API_REFERENCE.md
│   │   ├── 📄 ARCHITECTURE.md
│   │   ├── 📄 DB_SCHEMA.md
│   │   └── 📄 STRUCTURE.md
│   ├── 📂 deployment/
│   │   └── 📄 DEPLOYMENT_GUIDE.md
│   ├── 📂 specs/
│   │   ├── 📄 BlueBox.md
│   │   ├── 📄 CleanTest.json
│   │   ├── 📄 DirectTest.json
│   │   ├── 📄 LoginBox.json
│   │   ├── 📄 YbDashboard.json
│   │   └── 📄 YbSidebar.json
│   ├── 📂 standards/
│   │   └── 📄 PORT_STRATEGY.md
│   ├── 📂 user_guide/
│   │   ├── 📄 METERING_MANUAL.md
│   │   └── 📄 SUPER_ADMIN_MANUAL.md
│   ├── 📄 ADMIN_RESOURCE_INVENTORY.md
│   ├── 📄 ADMIN_STRATEGY.md
│   ├── 📄 AUDIT_REPORT.md
│   ├── 📄 AUTONOMOUS_HOSTING_ANALYSIS.md
│   ├── 📄 AUTO_DEPLOY_GUIDE.md
│   ├── 📄 CCTV_GUIDE.md
│   ├── 📄 DEPLOYMENT_GUIDE.md
│   ├── 📄 FINAL_COMPLETION_REPORT.md
│   ├── 📄 LIVE_USAGE.md
│   ├── 📄 LOGGING_ANALYSIS.md
│   ├── 📄 LOGGING_COMPLETION.md
│   ├── 📄 LOGGING_GUIDE.md
│   ├── 📄 MANAGEMENT_GUIDE.md
│   ├── 📄 MANAGEMENT_STRATEGY.md
│   ├── 📄 MIDPOINT_REVIEW.md
│   ├── 📄 NEXT_ACTIONS.md
│   ├── 📄 PHASE1_COMPLETION.md
│   ├── 📄 PHASE2_COMPLETION.md
│   ├── 📄 SESSION_END_GUIDE.md
│   ├── 📄 STRUCTURE.md
│   ├── 📄 TESTING_PHASE1.md
│   ├── 📄 masterplan.md
│   ├── 📄 security_analysis.md
│   └── 📄 security_improvement_plan.md
├── 📂 gui/
│   ├── 📂 DprojectsMonewmentgui/
│   ├── 📂 app/
│   │   ├── 📂 admin/
│   │   │   ├── 📂 deepsync/
│   │   │   │   └── 📄 page.tsx
│   │   │   └── 📄 page.tsx
│   │   ├── 📂 builder/
│   │   │   ├── 📂 grid/
│   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 popup/
│   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 table/
│   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📄 layout.tsx
│   │   │   └── 📄 page.tsx
│   │   ├── 📂 dashboard/
│   │   │   └── 📄 page.tsx
│   │   ├── 📂 login/
│   │   │   └── 📄 page.tsx
│   │   ├── 📂 pixelgrid/
│   │   │   ├── 📂 editor/
│   │   │   │   └── 📄 page.tsx
│   │   │   └── 📄 page.tsx
│   │   ├── 📂 projects/
│   │   │   └── 📂 [projectName]/
│   │   │       └── 📄 page.tsx
│   │   ├── 📂 register/
│   │   │   └── 📄 page.tsx
│   │   ├── 📂 settings/
│   │   │   └── 📄 page.tsx
│   │   ├── 📂 signup/
│   │   │   └── 📄 page.tsx
│   │   ├── 📄 favicon.ico
│   │   ├── 📄 globals.css
│   │   ├── 📄 layout.tsx
│   │   └── 📄 page.tsx
│   ├── 📂 components/
│   │   ├── 📂 ui-engine/
│   │   │   ├── 📄 Renderer.tsx
│   │   │   └── 📄 parts.tsx
│   │   ├── 📄 AdminDashboard.tsx
│   │   ├── 📄 BlueBox.tsx
│   │   ├── 📄 CleanTest.tsx
│   │   ├── 📄 DirectTest.tsx
│   │   ├── 📄 LayoutProvider.tsx
│   │   ├── 📄 LoginBox.tsx
│   │   ├── 📄 MasterLayout.tsx
│   │   ├── 📄 YbDashboard.tsx
│   │   └── 📄 YbSidebar.tsx
│   ├── 📂 public/
│   │   ├── 📄 file.svg
│   │   ├── 📄 globe.svg
│   │   ├── 📄 login-side-bg.png
│   │   ├── 📄 next.svg
│   │   ├── 📄 vercel.svg
│   │   └── 📄 window.svg
│   ├── 📄 Dockerfile
│   ├── 📄 README.md
│   ├── 📄 eslint.config.mjs
│   ├── 📄 next-env.d.ts
│   ├── 📄 next.config.ts
│   ├── 📄 package-lock.json
│   ├── 📄 package.json
│   ├── 📄 postcss.config.mjs
│   ├── 📄 tailwind.config.ts
│   └── 📄 tsconfig.json
├── 📂 k8s/
│   ├── 📄 backend.yaml
│   ├── 📄 frontend.yaml
│   ├── 📄 guacamole-auth-bypass.yaml
│   ├── 📄 guacamole.yaml
│   ├── 📄 kubevirt-config-patch.yaml
│   ├── 📄 kubevirt-patch.yaml
│   ├── 📄 postgres.yaml
│   ├── 📄 rbac.yaml
│   ├── 📄 vm-service.yaml
│   ├── 📄 vm-test.yaml
│   └── 📄 vnc-fallback.yaml
├── 📂 logs/
│   ├── 📄 access.log
│   ├── 📄 errors.log
│   └── 📄 monewment.log
├── 📂 projects/
│   ├── 📂 Project-488/
│   ├── 📂 Project-581/
│   ├── 📂 TestProject/
│   ├── 📂 Verification-Node/
│   ├── 📂 hacked_creation/
│   │   ├── 📄 config.json
│   │   ├── 📄 main.log
│   │   └── 📄 main.py
│   ├── 📂 metering_proj_1767703931/
│   │   ├── 📄 config.json
│   │   ├── 📄 main.log
│   │   └── 📄 main.py
│   ├── 📂 metering_proj_1767703955/
│   │   ├── 📄 config.json
│   │   ├── 📄 main.log
│   │   └── 📄 main.py
│   ├── 📂 metering_proj_1768110352/
│   │   ├── 📄 config.json
│   │   ├── 📄 main.log
│   │   └── 📄 main.py
│   ├── 📂 metering_proj_1768110494/
│   │   ├── 📄 config.json
│   │   ├── 📄 main.log
│   │   └── 📄 main.py
│   ├── 📂 metering_proj_1768110556/
│   │   ├── 📄 config.json
│   │   ├── 📄 main.log
│   │   └── 📄 main.py
│   ├── 📂 metering_proj_1768111260/
│   │   ├── 📄 config.json
│   │   ├── 📄 main.log
│   │   └── 📄 main.py
│   └── 📂 metering_proj_1768111748/
│       ├── 📄 config.json
│       ├── 📄 main.log
│       └── 📄 main.py
├── 📂 scripts/
│   ├── 📂 generators/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 api_docs_generator.py
│   │   ├── 📄 api_list_generator.py
│   │   ├── 📄 architecture_generator.py
│   │   ├── 📄 db_schema_generator.py
│   │   ├── 📄 deployment_generator.py
│   │   ├── 📄 function_spec_generator.py
│   │   ├── 📄 structure_generator.py
│   │   └── 📄 user_manual_generator.py
│   ├── 📂 utils/
│   │   └── 📄 pack_context.py
│   ├── 📄 agent_server.py
│   ├── 📄 ai_agent.py
│   ├── 📄 build_ant.ps1
│   ├── 📄 check_api_keys.py
│   ├── 📄 check_health.py
│   ├── 📄 check_models.py
│   ├── 📄 connect_k8s.ps1
│   ├── 📄 create_test_user.py
│   ├── 📄 debug_user_auth.py
│   ├── 📄 fix_db_schema.py
│   ├── 📄 generate_docs_v4.py
│   ├── 📄 generate_docs_v5.py
│   ├── 📄 generate_keys.py
│   ├── 📄 init_metering_db.py
│   ├── 📄 install_git_hook.ps1
│   ├── 📄 mcp_server.py
│   ├── 📄 migrate_hybrid_model.py
│   ├── 📄 migrate_passwords.py
│   ├── 📄 migrate_payment_system.py
│   ├── 📄 migrate_v2_2.py
│   ├── 📄 mock_ants.py
│   ├── 📄 pre-commit.sh
│   ├── 📄 reset_db.py
│   ├── 📄 run_local_cctv.py
│   ├── 📄 seed_billing_data.py
│   ├── 📄 seed_hierarchy.py
│   ├── 📄 session_end.ps1
│   ├── 📄 smart_ant.py
│   ├── 📄 smart_commit.ps1
│   ├── 📄 test_db_connection.py
│   ├── 📄 test_env.py
│   ├── 📄 test_monitor_api.py
│   ├── 📄 ui_factory.py
│   ├── 📄 usage_cctv.py
│   ├── 📄 verify_admin.py
│   ├── 📄 verify_auth.py
│   ├── 📄 verify_billing.py
│   ├── 📄 verify_metering.py
│   ├── 📄 verify_relay.py
│   ├── 📄 verify_security.py
│   ├── 📄 verify_traversal.py
│   ├── 📄 verify_updater.py
│   └── 📄 watch_and_doc.py
├── 📂 src/
│   ├── 📂 ant_client/
│   │   ├── 📂 core/
│   │   │   ├── 📂 p2p/
│   │   │   │   ├── 📄 engine.py
│   │   │   │   └── 📄 protocol.py
│   │   │   ├── 📂 render/
│   │   │   │   └── 📄 blender_ops.py
│   │   │   ├── 📂 vault/
│   │   │   │   └── 📄 shredder.py
│   │   │   ├── 📄 connection.py
│   │   │   ├── 📄 executor.py
│   │   │   ├── 📄 updater.py
│   │   │   └── 📄 watchdog.py
│   │   ├── 📂 ui/
│   │   │   ├── 📄 dashboard.py
│   │   │   └── 📄 tray.py
│   │   ├── 📄 app.py
│   │   ├── 📄 main.py
│   │   ├── 📄 repair_agent.py
│   │   ├── 📄 vault_downloader.py
│   │   ├── 📄 vault_uploader.py
│   │   └── 📄 worker_main.py
│   ├── 📂 api/
│   │   └── 📂 v1/
│   │       ├── 📂 admin/
│   │       │   ├── 📄 dashboard.py
│   │       │   └── 📄 monitoring.py
│   │       ├── 📂 endpoints/
│   │       │   ├── 📄 ant_socket.py
│   │       │   ├── 📄 auth.py
│   │       │   ├── 📄 billing.py
│   │       │   ├── 📄 chat.py
│   │       │   ├── 📄 deploy.py
│   │       │   ├── 📄 email_service.py
│   │       │   ├── 📄 projects.py
│   │       │   ├── 📄 services.py
│   │       │   └── 📄 vm.py
│   │       ├── 📂 render/
│   │       │   └── 📄 router.py
│   │       ├── 📂 sync/
│   │       │   └── 📄 router.py
│   │       └── 📂 vault/
│   │           ├── 📄 manager.py
│   │           ├── 📄 router.py
│   │           ├── 📄 tracker.py
│   │           └── 📄 watchdog.py
│   ├── 📂 common/
│   │   └── 📄 erasure_coding.py
│   ├── 📂 core/
│   │   ├── 📂 billing/
│   │   │   └── 📄 profit_engine.py
│   │   ├── 📂 devtools/
│   │   │   ├── 📂 inspectors/
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 config.py
│   │   │   │   ├── 📄 database.py
│   │   │   │   ├── 📄 network.py
│   │   │   │   └── 📄 structure.py
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 manager.py
│   │   │   └── 📄 watcher.py
│   │   ├── 📄 ant_security.py
│   │   ├── 📄 background.py
│   │   ├── 📄 cluster_manager.py
│   │   ├── 📄 deployer.py
│   │   ├── 📄 email_utils.py
│   │   ├── 📄 env_crypto.py
│   │   ├── 📄 k8s_client.py
│   │   ├── 📄 limiter.py
│   │   ├── 📄 logger.py
│   │   ├── 📄 protocol.py
│   │   ├── 📄 redis_client.py
│   │   ├── 📄 scheduler.py
│   │   ├── 📄 security.py
│   │   ├── 📄 socket_manager.py
│   │   └── 📄 worker.py
│   ├── 📂 middleware/
│   │   └── 📄 request_id.py
│   ├── 📂 routers/
│   │   ├── 📄 devtools.py
│   │   ├── 📄 tools.py
│   │   └── 📄 ui_factory.py
│   ├── 📂 services/
│   │   ├── 📄 billing.py
│   │   └── 📄 metering.py
│   ├── 📄 collector.py
│   ├── 📄 config.py
│   ├── 📄 database.py
│   ├── 📄 dependencies.py
│   ├── 📄 main.py
│   ├── 📄 models.py
│   ├── 📄 models_append.txt
│   └── 📄 schemas.py
├── 📂 temp_test_updater/
│   ├── 📄 client.exe
│   └── 📄 client.exe.bak
├── 📂 templates/
│   └── 📂 standard/
│       └── 📄 main.py
├── 📂 test_output/
├── 📂 tests/
│   ├── 📂 ant_client/
│   │   └── 📄 test_security.py
│   ├── 📂 api/
│   │   └── 📄 test_vault_manager.py
│   ├── 📂 core/
│   │   ├── 📂 billing/
│   │   │   └── 📄 test_profit_engine.py
│   │   ├── 📄 test_architecture.py
│   │   ├── 📄 test_redis.py
│   │   └── 📄 test_vault.py
│   ├── 📂 integration/
│   │   ├── 📄 test_job_flow.py
│   │   ├── 📄 test_render_flow.py
│   │   ├── 📄 test_vault_download.py
│   │   ├── 📄 test_vault_flow.py
│   │   └── 📄 test_vault_repair.py
│   ├── 📂 p2p/
│   │   └── 📄 test_antnet.py
│   ├── 📄 conftest.py
│   ├── 📄 test_api_async.py
│   ├── 📄 test_blender_security.py
│   └── 📄 verify_real_blender.py
├── 📄 .env.example
├── 📄 Dockerfile.backend
├── 📄 MonewmentAnt.spec
├── 📄 Start-project.ps1
├── 📄 ant_client.log
├── 📄 cube.blend
├── 📄 docker-compose.yml
├── 📄 dump.rdb
├── 📄 gateway_launcher.py
├── 📄 init.sql
├── 📄 monewment.db
├── 📄 requirements.txt
├── 📄 start_monewment.ps1
└── 📄 test_upload.dat

*Generated by Monewment Auto-Doc System v5.0*

# 🏗️ Monewment & Vendors 통합 구조 및 설계 가이드
> **Last Updated:** 2026-01-06 15:39:15

## 1. 프로젝트 디렉토리 트리
```text
├── 📂 Monewment/
│   ├── 📄 requirements.txt
│   ├── 📄 gateway_launcher.py
│   ├── 📄 init.sql
│   ├── 📄 Start-project.ps1
│   ├── 📄 Dockerfile.backend
│   ├── 📄 docker-compose.yml
│   ├── 📄 monewment.db
│   └── 📄 start_monewment.ps1
│   ├── 📂 projects/
│   │   ├── 📂 metering_proj_1767703931/
│   │   │   ├── 📄 config.json
│   │   │   ├── 📄 main.log
│   │   │   └── 📄 main.py
│   │   ├── 📂 hacked_creation/
│   │   │   ├── 📄 config.json
│   │   │   ├── 📄 main.log
│   │   │   └── 📄 main.py
│   │   ├── 📂 metering_proj_1767703955/
│   │   │   ├── 📄 config.json
│   │   │   ├── 📄 main.log
│   │   │   └── 📄 main.py
│   ├── 📂 scripts/
│   │   ├── 📄 verify_auth.py
│   │   ├── 📄 migrate_passwords.py
│   │   ├── 📄 check_health.py
│   │   ├── 📄 seed_billing_data.py
│   │   ├── 📄 run_local_cctv.py
│   │   ├── 📄 seed_hierarchy.py
│   │   ├── 📄 verify_metering.py
│   │   ├── 📄 mcp_server.py
│   │   ├── 📄 watch_and_doc.py
│   │   ├── 📄 connect_k8s.ps1
│   │   ├── 📄 verify_admin.py
│   │   ├── 📄 pre-commit.sh
│   │   ├── 📄 generate_docs.py
│   │   ├── 📄 ui_factory.py
│   │   ├── 📄 verify_traversal.py
│   │   ├── 📄 migrate_v2_2.py
│   │   ├── 📄 install_git_hook.ps1
│   │   ├── 📄 agent_server.py
│   │   ├── 📄 test_env.py
│   │   ├── 📄 ai_agent.py
│   │   └── 📄 check_models.py
│   │   ├── 📂 utils/
│   │   │   └── 📄 pack_context.py
│   ├── 📂 .github/
│   │   ├── 📂 workflows/
│   │   │   └── 📄 ci.yml
│   ├── 📂 docs/
│   │   ├── 📄 AUDIT_REPORT.md
│   │   ├── 📄 STRUCTURE.md
│   │   ├── 📄 ADMIN_RESOURCE_INVENTORY.md
│   │   ├── 📄 masterplan.md
│   │   ├── 📄 ADMIN_STRATEGY.md
│   │   ├── 📄 CCTV_GUIDE.md
│   │   ├── 📄 MANAGEMENT_STRATEGY.md
│   │   └── 📄 MANAGEMENT_GUIDE.md
│   │   ├── 📂 auto_generated/
│   │   │   ├── 📄 STRUCTURE.md
│   │   │   ├── 📄 API_SPEC.md
│   │   │   ├── 📄 DATA_SCHEMA.md
│   │   │   └── 📄 CONFIG_MAP.md
│   │   ├── 📂 specs/
│   │   │   ├── 📄 YbSidebar.json
│   │   │   ├── 📄 BlueBox.md
│   │   │   ├── 📄 YbDashboard.json
│   │   │   ├── 📄 DirectTest.json
│   │   │   ├── 📄 CleanTest.json
│   │   │   └── 📄 LoginBox.json
│   ├── 📂 k8s/
│   │   ├── 📄 guacamole.yaml
│   │   ├── 📄 kubevirt-patch.yaml
│   │   ├── 📄 frontend.yaml
│   │   ├── 📄 backend.yaml
│   │   ├── 📄 postgres.yaml
│   │   ├── 📄 vm-test.yaml
│   │   ├── 📄 vnc-fallback.yaml
│   │   ├── 📄 rbac.yaml
│   │   ├── 📄 guacamole-auth-bypass.yaml
│   │   ├── 📄 vm-service.yaml
│   │   └── 📄 kubevirt-config-patch.yaml
│   ├── 📂 gui/
│   │   ├── 📄 Dockerfile
│   │   ├── 📄 postcss.config.mjs
│   │   ├── 📄 next.config.ts
│   │   ├── 📄 package-lock.json
│   │   ├── 📄 README.md
│   │   ├── 📄 package.json
│   │   ├── 📄 eslint.config.mjs
│   │   ├── 📄 tsconfig.json
│   │   └── 📄 tailwind.config.ts
│   │   ├── 📂 components/
│   │   │   ├── 📄 LoginBox.tsx
│   │   │   ├── 📄 AdminDashboard.tsx
│   │   │   ├── 📄 YbSidebar.tsx
│   │   │   ├── 📄 DirectTest.tsx
│   │   │   ├── 📄 CleanTest.tsx
│   │   │   ├── 📄 YbDashboard.tsx
│   │   │   └── 📄 BlueBox.tsx
│   │   │   ├── 📂 ui-engine/
│   │   │   │   ├── 📄 Renderer.tsx
│   │   │   │   └── 📄 parts.tsx
│   │   ├── 📂 app/
│   │   │   ├── 📄 globals.css
│   │   │   ├── 📄 layout.tsx
│   │   │   ├── 📄 favicon.ico
│   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 dashboard/
│   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 admin/
│   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 projects/
│   │   │   │   ├── 📂 [projectName]/
│   │   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 builder/
│   │   │   │   ├── 📄 layout.tsx
│   │   │   │   └── 📄 page.tsx
│   │   │   │   ├── 📂 grid/
│   │   │   │   │   └── 📄 page.tsx
│   │   │   │   ├── 📂 popup/
│   │   │   │   │   └── 📄 page.tsx
│   │   │   │   ├── 📂 table/
│   │   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 login/
│   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 settings/
│   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 register/
│   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 signup/
│   │   │   │   └── 📄 page.tsx
│   │   ├── 📂 public/
│   │   │   ├── 📄 file.svg
│   │   │   ├── 📄 next.svg
│   │   │   ├── 📄 globe.svg
│   │   │   ├── 📄 window.svg
│   │   │   └── 📄 vercel.svg
│   ├── 📂 src/
│   │   ├── 📄 logger.py
│   │   ├── 📄 models_append.txt
│   │   ├── 📄 dependencies.py
│   │   ├── 📄 database.py
│   │   ├── 📄 collector.py
│   │   ├── 📄 main.py
│   │   ├── 📄 schemas.py
│   │   ├── 📄 config.py
│   │   └── 📄 models.py
│   │   ├── 📂 api/
│   │   │   ├── 📂 v1/
│   │   │   │   ├── 📂 endpoints/
│   │   │   │   │   └── 📄 vm.py
│   │   ├── 📂 routers/
│   │   │   ├── 📄 devtools.py
│   │   │   ├── 📄 ui_factory.py
│   │   │   └── 📄 tools.py
│   │   ├── 📂 core/
│   │   │   ├── 📄 k8s_client.py
│   │   │   └── 📄 security.py
│   │   │   ├── 📂 devtools/
│   │   │   │   ├── 📄 watcher.py
│   │   │   │   ├── 📄 manager.py
│   │   │   │   └── 📄 __init__.py
│   │   │   │   ├── 📂 inspectors/
│   │   │   │   │   ├── 📄 structure.py
│   │   │   │   │   ├── 📄 network.py
│   │   │   │   │   ├── 📄 database.py
│   │   │   │   │   ├── 📄 config.py
│   │   │   │   │   └── 📄 __init__.py
│   ├── 📂 templates/
│   │   ├── 📂 standard/
│   │   │   └── 📄 main.py
```

> ❌ AI 서버 오류 (코드 404): models/gemini-1.5-flash is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods.

---
> Generated by Monewment Auto-Doc System v3.0 (Powered by Gemini)
# 🏗️ Monewment & Vendors 통합 구조 및 설계 가이드
> **Last Updated:** 2026-01-07 00:19:03

## 1. 프로젝트 디렉토리 트리
```text
├── 📂 Monewment/
│   ├── 📄 docker-compose.yml
│   ├── 📄 Dockerfile.backend
│   ├── 📄 gateway_launcher.py
│   ├── 📄 init.sql
│   ├── 📄 monewment.db
│   ├── 📄 requirements.txt
│   ├── 📄 Start-project.ps1
│   └── 📄 start_monewment.ps1
│   ├── 📂 .github/
│   │   ├── 📂 workflows/
│   │   │   └── 📄 ci.yml
│   ├── 📂 docs/
│   │   ├── 📄 ADMIN_STRATEGY.md
│   │   ├── 📄 AUDIT_REPORT.md
│   │   ├── 📄 CCTV_GUIDE.md
│   │   ├── 📄 MANAGEMENT_GUIDE.md
│   │   ├── 📄 MANAGEMENT_STRATEGY.md
│   │   ├── 📄 masterplan.md
│   │   └── 📄 STRUCTURE.md
│   │   ├── 📂 auto_generated/
│   │   │   ├── 📄 API_SPEC.md
│   │   │   ├── 📄 CONFIG_MAP.md
│   │   │   ├── 📄 DATA_SCHEMA.md
│   │   │   └── 📄 STRUCTURE.md
│   │   ├── 📂 specs/
│   │   │   ├── 📄 BlueBox.md
│   │   │   ├── 📄 CleanTest.json
│   │   │   ├── 📄 DirectTest.json
│   │   │   ├── 📄 LoginBox.json
│   │   │   ├── 📄 YbDashboard.json
│   │   │   └── 📄 YbSidebar.json
│   ├── 📂 gui/
│   │   ├── 📄 Dockerfile
│   │   ├── 📄 eslint.config.mjs
│   │   ├── 📄 next-env.d.ts
│   │   ├── 📄 next.config.ts
│   │   ├── 📄 package-lock.json
│   │   ├── 📄 package.json
│   │   ├── 📄 postcss.config.mjs
│   │   ├── 📄 README.md
│   │   ├── 📄 tailwind.config.ts
│   │   └── 📄 tsconfig.json
│   │   ├── 📂 app/
│   │   │   ├── 📄 favicon.ico
│   │   │   ├── 📄 globals.css
│   │   │   ├── 📄 layout.tsx
│   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 admin/
│   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 builder/
│   │   │   │   ├── 📄 layout.tsx
│   │   │   │   └── 📄 page.tsx
│   │   │   │   ├── 📂 grid/
│   │   │   │   │   └── 📄 page.tsx
│   │   │   │   ├── 📂 popup/
│   │   │   │   │   └── 📄 page.tsx
│   │   │   │   ├── 📂 table/
│   │   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 dashboard/
│   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 login/
│   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 projects/
│   │   │   │   ├── 📂 [projectName]/
│   │   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 register/
│   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 settings/
│   │   │   │   └── 📄 page.tsx
│   │   │   ├── 📂 signup/
│   │   │   │   └── 📄 page.tsx
│   │   ├── 📂 components/
│   │   │   ├── 📄 AdminDashboard.tsx
│   │   │   ├── 📄 BlueBox.tsx
│   │   │   ├── 📄 CleanTest.tsx
│   │   │   ├── 📄 DirectTest.tsx
│   │   │   ├── 📄 LoginBox.tsx
│   │   │   ├── 📄 YbDashboard.tsx
│   │   │   └── 📄 YbSidebar.tsx
│   │   │   ├── 📂 ui-engine/
│   │   │   │   ├── 📄 parts.tsx
│   │   │   │   └── 📄 Renderer.tsx
│   │   ├── 📂 public/
│   │   │   ├── 📄 file.svg
│   │   │   ├── 📄 globe.svg
│   │   │   ├── 📄 next.svg
│   │   │   ├── 📄 vercel.svg
│   │   │   └── 📄 window.svg
│   ├── 📂 k8s/
│   │   ├── 📄 backend.yaml
│   │   ├── 📄 frontend.yaml
│   │   ├── 📄 guacamole-auth-bypass.yaml
│   │   ├── 📄 guacamole.yaml
│   │   ├── 📄 kubevirt-config-patch.yaml
│   │   ├── 📄 kubevirt-patch.yaml
│   │   ├── 📄 postgres.yaml
│   │   ├── 📄 rbac.yaml
│   │   ├── 📄 vm-service.yaml
│   │   ├── 📄 vm-test.yaml
│   │   └── 📄 vnc-fallback.yaml
│   ├── 📂 projects/
│   │   ├── 📂 hacked_creation/
│   │   │   ├── 📄 config.json
│   │   │   ├── 📄 main.log
│   │   │   └── 📄 main.py
│   │   ├── 📂 metering_proj_1767703931/
│   │   │   ├── 📄 config.json
│   │   │   ├── 📄 main.log
│   │   │   └── 📄 main.py
│   │   ├── 📂 metering_proj_1767703955/
│   │   │   ├── 📄 config.json
│   │   │   ├── 📄 main.log
│   │   │   └── 📄 main.py
│   │   ├── 📂 Project-488/
│   │   ├── 📂 Project-581/
│   │   ├── 📂 TestProject/
│   │   ├── 📂 Verification-Node/
│   ├── 📂 scripts/
│   │   ├── 📄 agent_server.py
│   │   ├── 📄 ai_agent.py
│   │   ├── 📄 check_health.py
│   │   ├── 📄 check_models.py
│   │   ├── 📄 connect_k8s.ps1
│   │   ├── 📄 generate_docs.py
│   │   ├── 📄 install_git_hook.ps1
│   │   ├── 📄 mcp_server.py
│   │   ├── 📄 migrate_passwords.py
│   │   ├── 📄 migrate_v2_2.py
│   │   ├── 📄 pre-commit.sh
│   │   ├── 📄 run_local_cctv.py
│   │   ├── 📄 seed_billing_data.py
│   │   ├── 📄 seed_hierarchy.py
│   │   ├── 📄 test_env.py
│   │   ├── 📄 ui_factory.py
│   │   ├── 📄 verify_admin.py
│   │   ├── 📄 verify_auth.py
│   │   ├── 📄 verify_metering.py
│   │   ├── 📄 verify_traversal.py
│   │   └── 📄 watch_and_doc.py
│   │   ├── 📂 utils/
│   │   │   └── 📄 pack_context.py
│   ├── 📂 src/
│   │   ├── 📄 collector.py
│   │   ├── 📄 config.py
│   │   ├── 📄 database.py
│   │   ├── 📄 dependencies.py
│   │   ├── 📄 logger.py
│   │   ├── 📄 main.py
│   │   ├── 📄 models.py
│   │   ├── 📄 models_append.txt
│   │   └── 📄 schemas.py
│   │   ├── 📂 api/
│   │   │   ├── 📂 v1/
│   │   │   │   ├── 📂 endpoints/
│   │   │   │   │   └── 📄 vm.py
│   │   ├── 📂 core/
│   │   │   ├── 📄 k8s_client.py
│   │   │   └── 📄 security.py
│   │   │   ├── 📂 devtools/
│   │   │   │   ├── 📄 manager.py
│   │   │   │   ├── 📄 watcher.py
│   │   │   │   └── 📄 __init__.py
│   │   │   │   ├── 📂 inspectors/
│   │   │   │   │   ├── 📄 config.py
│   │   │   │   │   ├── 📄 database.py
│   │   │   │   │   ├── 📄 network.py
│   │   │   │   │   ├── 📄 structure.py
│   │   │   │   │   └── 📄 __init__.py
│   │   ├── 📂 routers/
│   │   │   ├── 📄 devtools.py
│   │   │   ├── 📄 tools.py
│   │   │   └── 📄 ui_factory.py
│   ├── 📂 templates/
│   │   ├── 📂 standard/
│   │   │   └── 📄 main.py
```

> ❌ AI 서버 오류 (코드 404): models/gemini-1.5-flash is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods.

---
> Generated by Monewment Auto-Doc System v3.0 (Powered by Gemini)
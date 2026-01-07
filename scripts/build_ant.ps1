
$ErrorActionPreference = "Stop"

echo "📦 Packaging Monewment Client..."

# Ensure cleaner build
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Run PyInstaller
# --hidden-import: Ensure dynamic imports in src.ant_client.app are found (like websockets, internal modules)
# --add-data: If we had assets (icon), we'd add "assets;assets" (Windows separator ;)
# --noconsole: GUI application
# --onefile: Single exe

pyinstaller `
    --noconsole `
    --onefile `
    --name "MonewmentAnt" `
    --hidden-import="src" `
    --hidden-import="src.core" `
    --hidden-import="src.config" `
    --hidden-import="websockets" `
    --hidden-import="pystray" `
    --hidden-import="PIL" `
    --collect-all "src" `
    --paths="." `
    src/ant_client/app.py

echo "✅ Build Complete! Executable is in: dist/MonewmentAnt.exe"

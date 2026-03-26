$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $projectRoot ".venv\\Scripts\\python.exe"
$iconPath = Join-Path $projectRoot "assets\\mouse_key_simulator.ico"
$entryPath = Join-Path $projectRoot "simulator\\main.py"

if (-not (Test-Path $pythonExe)) {
    throw "未找到虚拟环境 Python：$pythonExe"
}

& $pythonExe -c "import PyInstaller" 2>$null
if ($LASTEXITCODE -ne 0) {
    throw "当前虚拟环境未安装 PyInstaller，请先执行: .\\.venv\\Scripts\\pip install pyinstaller"
}

Push-Location $projectRoot
try {
    & $pythonExe -m PyInstaller `
        --noconfirm `
        --clean `
        --windowed `
        --onefile `
        --name "MouseKeySimulator" `
        --icon $iconPath `
        --add-data "assets;assets" `
        --hidden-import "pynput.keyboard._win32" `
        $entryPath
}
finally {
    Pop-Location
}

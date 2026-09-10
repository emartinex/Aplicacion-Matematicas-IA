# Lanzador de escritorio. No instala paquetes ni modifica la configuración.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
$pyCommand = Get-Command py -ErrorAction SilentlyContinue
$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if ($pythonCommand) {
    & $pythonCommand.Source (Join-Path $PSScriptRoot 'app.py')
} elseif ($pyCommand) {
    & $pyCommand.Source -3 (Join-Path $PSScriptRoot 'app.py')
} elseif (Test-Path -LiteralPath $bundledPython) {
    & $bundledPython (Join-Path $PSScriptRoot 'app.py')
} else {
    Write-Host 'Instala Python 3.10 o superior con Tcl/Tk y vuelve a ejecutar este archivo.'
    exit 1
}

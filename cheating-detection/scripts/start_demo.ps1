param([string]$Video = '',
      [int]$CameraIndex = -1,
      [ValidateSet('mediapipe','yolo')][string]$PoseBackend = 'mediapipe')
$ErrorActionPreference = 'Stop'
$demoRoot = Split-Path -Parent $PSScriptRoot
if (-not [string]::IsNullOrWhiteSpace($Video) -and $CameraIndex -ge 0) {
    throw 'Choose either -Video or -CameraIndex, not both.'
}
if ([string]::IsNullOrWhiteSpace($Video)) {
    if ($CameraIndex -ge 0) {
        $env:EXAMGUARD_VIDEO_SOURCE = [string]$CameraIndex
    } else {
        Remove-Item Env:EXAMGUARD_VIDEO_SOURCE -ErrorAction SilentlyContinue
    }
} else {
    if (-not (Test-Path -LiteralPath $Video -PathType Leaf)) { throw 'Video must be a file' }
    $demoVideo = (Resolve-Path -LiteralPath $Video).Path
    $env:EXAMGUARD_VIDEO_SOURCE = $demoVideo
}
$demoModel = Join-Path $demoRoot 'models\phone_v3_colab\weights\best.pt'
if (-not (Test-Path -LiteralPath $demoModel -PathType Leaf)) { throw 'Missing Colab checkpoint' }
$env:PYTHONUTF8 = '1'
$env:YOLO_CONFIG_DIR = Join-Path $demoRoot 'artifacts'
$env:EXAMGUARD_PHONE_CONFIRM_MODEL = $demoModel
$env:EXAMGUARD_POSE_BACKEND = $PoseBackend
Push-Location $demoRoot
try { & (Join-Path $demoRoot 'venv\Scripts\python.exe') 'src/fastapi_server.py' }
finally { Pop-Location }

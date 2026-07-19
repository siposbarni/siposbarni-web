$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$git = "$env:LOCALAPPDATA\GitHubDesktop\app-3.5.12\resources\app\git\cmd\git.exe"

if (!(Test-Path $git)) {
  $gitCommand = Get-Command git -ErrorAction Stop
  $git = $gitCommand.Source
}

Set-Location $repo

& $git pull --rebase
python tools\generate-artworks.py
& $git add assets\artworks artworks.json

$changes = & $git status --porcelain
if (!$changes) {
  Write-Output "No gallery changes to publish."
  exit 0
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
& $git commit -m "Update gallery from Drive ($timestamp)"
& $git push

param([switch]$SkipDocker)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure { param([string]$Message) $script:failures.Add($Message) }
function Require-File {
  param([string]$RelativePath)
  if (-not (Test-Path -LiteralPath (Join-Path $root $RelativePath) -PathType Leaf)) {
    Add-Failure "Missing file: $RelativePath"
  }
}
function Invoke-Checked {
  param([string]$Label, [scriptblock]$Command)
  & $Command
  if ($LASTEXITCODE -ne 0) { Add-Failure "$Label failed with exit code $LASTEXITCODE" }
  $global:LASTEXITCODE = 0
}

$requiredFiles = @(
  "README.md", "REFERENCES.md", "project.yaml", "Dockerfile", "constraints.lock",
  "data/clinical-fixture-manifest.json", "data/LICENSE.md",
  "contracts/medical-evaluation-report-v1.schema.json",
  "benchmarks/workload.json", "benchmarks/results/baseline.json",
  "sdd/spec.md", "sdd/benchmark-plan.md", "sdd/architecture-decision.md",
  "sdd/technical-decision.md", "sdd/agent-handoff.md", "sdd/reuse-improvement-review.md"
)
foreach ($file in $requiredFiles) { Require-File $file }

$manifestPath = Join-Path $root "project.yaml"
$manifest = if (Test-Path -LiteralPath $manifestPath) { Get-Content -Raw -LiteralPath $manifestPath } else { "" }
if ($manifest -match "(?m)^status:\s*published\s*$") {
  Require-File "benchmarks/publication/stroke-signal-v2.json"
}

$reusePath = Join-Path $root "sdd/reuse-improvement-review.md"
if (Test-Path -LiteralPath $reusePath) {
  $reuse = Get-Content -Raw -LiteralPath $reusePath
  foreach ($pattern in @(
    "(?m)^- \[x\] Reusable improvements were patched or recorded\.\r?$",
    "(?m)^- \[x\] Project-specific implementation was not moved into the kit\.\r?$",
    "(?m)^- \[x\] Validation reflects .+\.\r?$"
  )) {
    if ($reuse -notmatch $pattern) { Add-Failure "Incomplete reuse review gate: $pattern" }
  }
}

Push-Location -LiteralPath $root
try {
  $jsonFiles = @(Get-ChildItem benchmarks,data,contracts -Recurse -Filter *.json -File -ErrorAction SilentlyContinue)
  foreach ($file in $jsonFiles) {
    Invoke-Checked "JSON validation: $($file.Name)" { python -m json.tool $file.FullName | Out-Null }
  }
  $previousPythonPath = $env:PYTHONPATH
  $env:PYTHONPATH = Join-Path $root "src"
  Invoke-Checked "Python compile" { python -m compileall -q src tests tools }
  Invoke-Checked "Ruff" { python -m ruff check src tests tools }
  Invoke-Checked "pytest coverage" {
    python -m pytest --cov=stroke_signal --cov-report=term-missing --cov-fail-under=90
  }
  if (Test-Path -LiteralPath (Join-Path $root "benchmarks/results/baseline.json")) {
    Invoke-Checked "benchmark contract" { python tools/validate-benchmark.py }
    Invoke-Checked "publication evidence" { python tools/validate-publication.py }
  }
  $env:PYTHONPATH = $previousPythonPath
} finally {
  Pop-Location
}

$legacy = "ro" + "che" + "do"
$searchFiles = Get-ChildItem -Path $root -Recurse -File | Where-Object {
  $normalized = $_.FullName -replace "\\", "/"
  $normalized -notmatch "/.git/" -and $normalized -notmatch "/.venv/" -and
  $_.Extension -in @(".md", ".yaml", ".yml", ".json", ".ps1", ".py", ".ts", ".go", ".kt", ".java")
}
$forbidden = Select-String -Path $searchFiles.FullName -Pattern @($legacy, (Get-Culture).TextInfo.ToTitleCase($legacy)) -SimpleMatch -ErrorAction SilentlyContinue
if ($forbidden) { Add-Failure "Forbidden legacy project nickname found" }

if (-not $SkipDocker) {
  Invoke-Checked "Docker build" { docker build -t stroke-signal-demo $root | Out-Null }
  Invoke-Checked "Docker default run" { docker run --rm --network none stroke-signal-demo | Out-Null }
}

if ($failures.Count -gt 0) {
  Write-Host "portfolio project validation failed with $($failures.Count) issue(s):"
  foreach ($failure in $failures) {
    Write-Host "  - $failure"
    if ($env:GITHUB_ACTIONS -eq "true") { Write-Host "::error::$failure" }
  }
  exit 1
}
Write-Host "portfolio project validation passed"

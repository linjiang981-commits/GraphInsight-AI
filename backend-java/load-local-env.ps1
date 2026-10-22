
$ErrorActionPreference = 'Stop'
$localEnvPath = Join-Path $PSScriptRoot '.env'
if (-not (Test-Path -LiteralPath $localEnvPath)) {
    throw 'Missing backend-java/.env. Create it before starting Java.'
}
$allowedNames = @(
    'DB_URL', 'DB_USER', 'DB_PASSWORD', 'SERVER_PORT',
    'APP_JWT_SECRET', 'APP_JWT_TTL_SECONDS',
    'APP_DEMO_USERNAME', 'APP_DEMO_PASSWORD'
)
foreach ($line in Get-Content -LiteralPath $localEnvPath -Encoding UTF8) {
    $trimmed = $line.Trim()
    if ($trimmed.Length -eq 0 -or $trimmed.StartsWith('#')) { continue }
    $parts = $trimmed -split '=', 2
    if ($parts.Count -ne 2) { throw 'Invalid .env line; expected NAME=value.' }
    $name = $parts[0].Trim()
    if ($name -notin $allowedNames) { throw "Unsupported variable: $name" }
    [Environment]::SetEnvironmentVariable($name, $parts[1], 'Process')
}
Write-Host 'Local environment loaded. Values are not printed.'
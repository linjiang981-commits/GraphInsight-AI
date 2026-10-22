$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    . (Join-Path $PSScriptRoot 'load-local-env.ps1')
    & .\mvnw.cmd '-Dspring-boot.run.profiles=dev' spring-boot:run
    if ($LASTEXITCODE -ne 0) { throw "Spring Boot exited with code $LASTEXITCODE" }
}
finally { Pop-Location }
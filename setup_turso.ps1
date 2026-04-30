# PowerShell script to help set up Turso for VoteChain
# Run this script to easily configure Turso credentials

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "VoteChain Turso Setup Helper" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Turso CLI is installed
Write-Host "1. Checking Turso CLI..." -ForegroundColor Yellow
try {
    $tursoVersion = turso --version 2>&1
    Write-Host "   [OK] Turso CLI installed: $tursoVersion" -ForegroundColor Green
} catch {
    Write-Host "   [--] Turso CLI not found" -ForegroundColor Red
    Write-Host "   Installing Turso CLI..." -ForegroundColor Yellow
    try {
        iwr https://get.tur.so/install.ps1 -useb | iex
        Write-Host "   [OK] Turso CLI installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "   [XX] Failed to install Turso CLI" -ForegroundColor Red
        Write-Host "   Please install manually from: https://docs.tur.so/getting-started" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "2. Login to Turso..." -ForegroundColor Yellow
Write-Host "   (A browser window will open for authentication)" -ForegroundColor Gray
turso auth login

Write-Host ""
Write-Host "3. Creating database..." -ForegroundColor Yellow
$dbName = "votechain-db"
turso db create $dbName

Write-Host ""
Write-Host "4. Getting database URL..." -ForegroundColor Yellow
$dbUrl = turso db show $dbName | Select-String "URL"
if ($dbUrl -match "https://[^\s]+") {
    $url = $matches[0]
    Write-Host "   [OK] Database URL: $url" -ForegroundColor Green
} else {
    Write-Host "   [XX] Could not get database URL" -ForegroundColor Red
    Write-Host "   Please run: turso db show $dbName" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "5. Generating auth token..." -ForegroundColor Yellow
$token = turso auth token
Write-Host "   [OK] Auth token generated" -ForegroundColor Green

Write-Host ""
Write-Host "6. Updating .env file..." -ForegroundColor Yellow
$envPath = ".\.env"
if (Test-Path $envPath) {
    $envContent = Get-Content $envPath
    $envContent = $envContent -replace "TURSO_URL=.*", "TURSO_URL=$url"
    $envContent = $envContent -replace "TURSO_AUTH_TOKEN=.*", "TURSO_AUTH_TOKEN=$token"
    $envContent | Set-Content $envPath
    Write-Host "   [OK] .env file updated" -ForegroundColor Green
} else {
    Write-Host "   [XX] .env file not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Turso Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run: python test_setup.py" -ForegroundColor Gray
Write-Host "2. Start server: python -m uvicorn main:app --host localhost --port 8000" -ForegroundColor Gray
Write-Host "3. Deploy to Render with the same .env values" -ForegroundColor Gray
Write-Host ""

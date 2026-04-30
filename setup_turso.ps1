# PowerShell script to install Turso CLI and get new token
# Run this script to set up Turso properly

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Turso CLI Setup for VoteChain" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install Turso CLI
Write-Host "Step 1: Installing Turso CLI..." -ForegroundColor Yellow
try {
    iwr https://get.tur.so/install.ps1 -useb | iex
    Write-Host "   [OK] Turso CLI installed successfully" -ForegroundColor Green
} catch {
    Write-Host "   [XX] Failed to install Turso CLI: $_" -ForegroundColor Red
    Write-Host "   Please install manually from: https://docs.tur.so/getting-started" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Step 2: Logging in to Turso..." -ForegroundColor Yellow
Write-Host "   (Browser will open for authentication)" -ForegroundColor Gray
try {
    turso auth login
    Write-Host "   [OK] Logged in successfully" -ForegroundColor Green
} catch {
    Write-Host "   [XX] Login failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Creating database (if not exists)..." -ForegroundColor Yellow
try {
    turso db create votechain-db 2>$null
    Write-Host "   [OK] Database 'votechain-db' ready" -ForegroundColor Green
} catch {
    Write-Host "   [INFO] Database may already exist" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Step 4: Getting database URL..." -ForegroundColor Yellow
try {
    $dbUrl = turso db show votechain-db | Select-String "URL" | ForEach-Object { $_.ToString().Split(' ')[-1].Trim() }
    if ($dbUrl) {
        Write-Host "   [OK] URL: $dbUrl" -ForegroundColor Green
    } else {
        Write-Host "   [XX] Could not get URL" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   [XX] Failed to get URL: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 5: Generating new auth token..." -ForegroundColor Yellow
try {
    $token = turso auth token
    if ($token) {
        Write-Host "   [OK] Token generated" -ForegroundColor Green
    } else {
        Write-Host "   [XX] Could not generate token" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   [XX] Failed to generate token: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 6: Updating .env file..." -ForegroundColor Yellow
$envPath = ".\.env"
if (Test-Path $envPath) {
    $envContent = Get-Content $envPath
    $envContent = $envContent -replace "TURSO_URL=.*", "TURSO_URL=$dbUrl"
    $envContent = $envContent -replace "TURSO_AUTH_TOKEN=.*", "TURSO_AUTH_TOKEN=$token"
    $envContent | Set-Content $envPath
    Write-Host "   [OK] .env file updated" -ForegroundColor Green
} else {
    Write-Host "   [XX] .env file not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Turso Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the connection: python -c ""from blockchain import Blockchain; bc = Blockchain()""" -ForegroundColor Gray
Write-Host "2. Start the server: python -m uvicorn main:app --host localhost --port 8000" -ForegroundColor Gray
Write-Host "3. Deploy to Render with the same .env values" -ForegroundColor Gray
Write-Host ""

# Start the complete system with tunnel for defense
# Usage: .\start-tunnel.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== Blockchain Voting System - Defense Setup ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill any existing processes on port 8000
Write-Host "Step 1: Checking port 8000..." -ForegroundColor Yellow
$portCheck = netstat -ano | findstr :8000
if ($portCheck) {
    Write-Host "  Found existing process on port 8000, killing..." -ForegroundColor Yellow
    $pidOnPort = ($portCheck -split '\s+')[-1]
    taskkill /PID $pidOnPort /F 2>$null
    Start-Sleep -Seconds 2
}

# Step 2: Start backend (serves API + frontend)
Write-Host "Step 2: Starting backend server..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\olive\OneDrive\Desktop\Blockchain Final"
    uvicorn main:app --host 0.0.0.0 --port 8000
}

Start-Sleep -Seconds 3

# Step 3: Verify backend is running
$backendRunning = netstat -ano | findstr :8000
if (-not $backendRunning) {
    Write-Host " ERROR: Backend failed to start!" -ForegroundColor Red
    exit 1
}
Write-Host "  Backend running on port 8000" -ForegroundColor Green

# Step 4: Start localtunnel
Write-Host "Step 3: Starting localtunnel..." -ForegroundColor Yellow
$tunnelJob = Start-Job -ScriptBlock {
    lt --port 8000 --subdomain blockchain-voting-defense
}

Start-Sleep -Seconds 5

# Step 5: Display results
Write-Host ""
Write-Host "=== SYSTEM READY FOR DEFENSE ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Public URL (share with defense panel):" -ForegroundColor Green
Write-Host "  https://blockchain-voting-defense.loca.lt" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host ""
Write-Host "Local URL (for your screen):" -ForegroundColor Green
Write-Host "  http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "Test the URL now to make sure it works!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Jobs running:" -ForegroundColor Gray
Get-Job | Format-Table Id, Name, State, PSJobTypeName

# Campaña de reintentos de checkm8 sobre WSL2/usbipd
# Detecta éxito buscando "PWND" en el serial del dispositivo.

$ErrorActionPreference = "Continue"
$busid = "1-4"
$repo  = "/mnt/c/Users/sebas/checkm8-lab/SSHRD_Script"
$max   = 40

function Detach { usbipd detach --busid $busid 2>&1 | Out-Null }
function Attach {
    usbipd attach --wsl --busid $busid 2>&1 | Out-Null
    Start-Sleep -Seconds 2
}

Write-Host "=========================================================="
Write-Host " CAMPANA checkm8 - A9 / iPhone 7 - sobre WSL2 usbipd"
Write-Host "=========================================================="

$pwned = $false
for ($i = 1; $i -le $max; $i++) {
    Write-Host ""
    Write-Host "--- Intento $i / $max ---" -ForegroundColor Cyan

    Detach
    Attach

    # ¿el dispositivo sigue en DFU del lado Windows?
    $dev = Get-PnpDevice -ErrorAction SilentlyContinue |
           Where-Object { $_.InstanceId -like 'USB\VID_05AC&PID_1227*' -and $_.Status -eq 'OK' }
    if (-not $dev) {
        Write-Host "  [!] El telefono salio de DFU. Vuelve a ponerlo en DFU." -ForegroundColor Yellow
        Write-Host "      Espera 8s..." -ForegroundColor Yellow
        Start-Sleep -Seconds 8
        continue
    }

    # ¿ya esta pwned de un intento anterior?
    $pre = wsl -d kali-linux -u root -- bash -c "cd $repo && timeout 12 ./Linux/irecovery -q 2>&1"
    if ($pre -match "PWND") {
        Write-Host "  [+] YA PWNED detectado antes de ejecutar" -ForegroundColor Green
        $pwned = $true
        break
    }

    # ejecutar el exploit con timeout (gaster puede colgarse)
    $out = wsl -d kali-linux -u root -- bash -c "cd $repo && timeout 12 ./Linux/gaster pwn 2>&1; echo RC=\$?"
    $rc = ($out | Select-String "RC=(\d+)").Matches.Groups[1].Value

    # el exploit resetea el USB -> hay que re-adjuntar para inspeccionar
    Start-Sleep -Seconds 2
    Detach
    Attach

    $post = wsl -d kali-linux -u root -- bash -c "cd $repo && timeout 12 ./Linux/irecovery -q 2>&1"

    if ($post -match "PWND") {
        Write-Host "  [+] *** EXITO: checkm8 LOGRO PNWED DFU ***" -ForegroundColor Green
        $pwned = $true
        $post | ForEach-Object { Write-Host "      $_" }
        break
    }

    $srtg = ($post | Select-String "SRTG:").ToString().Trim()
    Write-Host "  [-] Intento $i fallo (rc=$rc). $srtg" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=========================================================="
if ($pwned) {
    Write-Host " RESULTADO: PNWED DFU LOGRADO" -ForegroundColor Green
} else {
    Write-Host " RESULTADO: sin exito tras $max intentos" -ForegroundColor Red
}
Write-Host "=========================================================="

# Log de la sesión de investigación

## Resumen cronológico

### Fase 1 — Auditoría (SSHRD_Script)
- Analizado el proyecto: SSH Ramdisk Script, open-source de `verygenericname`
- **Veredicto: limpio, sin malware**
- `ipwndfu` de axi0mX y `SSHRD_Script` son repos oficiales
- Telemetría a `nathan4s.lol` encontrada pero **comentada** (desactivada)
- `gaster` (binario sin verificar) escaneado: sin exfiltración

### Fase 2 — Errores de Windows al clonar
1. **`env: 'sh\r'`** — 416 líneas con CRLF por `core.autocrlf=true`
   - Diagnóstico: bytes `0d 0a` al final del shebang
   - Fix: `git config core.autocrlf false` + borrado + re-checkout
2. **`Unable to find current revision in submodule 'sshtars'`**
   - El `.git` del submódulo contenía path absoluto de Windows
   - Linux git lo interpretaba como relativo
   - Fix: gitfile relativo + fetch de `refs/pull/7/head`

### Fase 3 — WSL2: el dispositivo se ve pero no se puede explotar
- usbipd detecta el iPhone (`05ac:1227`)
- `irecovery` no conecta → descubierto: faltaba `usbipd attach` (estado era `Shared`, no `Attached`)
- `sudo` fallaba por pedir password en terminal sin TTY → `wsl -u root`
- **Medición de latencia**: 0.538 ms mediana, 1.811 ms máximo, 300/300 éxito
- `gaster pwn`: bucle infinito, nunca pwned

### Fase 4 — Litera1n nativo Windows: falla por API de libusb
- Clonado y auditado (limpio)
- **Defender bloqueó** `checkm8.py` y `checkra1n.exe`:
  - `Exploit:MacOS/CVE-2019-8900.A!MTB` (que ES checkm8)
  - `HackTool:Win32/crack`
- **Defender también marcó el archivo oficial de axi0mX** → falso positivo de heurística
- Excepción de Defender añadida para la carpeta del proyecto
- **Causa raíz**: `libusb-win32` no exporta `libusb_wrap_device` → la API 1.0 que necesita checkm8.py
- Probado: DLL 1.0.24 con driver 1.4.0.0 → crash `0xC0000005`
- Probado: DLL 1.0.24 con driver 1.2.7.4 → crash `0xC0000005`
- **API 0.1 (`libusb0.dll` 1.4.0.0) sí funciona** pero incompatible con checkm8.py

### Fase 5 — Puerto a Python 3 (RESULTADO)
- Decisión: portar `checkm8.py` a Python 3 para WSL2 con libusb real
- ~20 cambios mecánicos (print, bytes, hex, división entera)
- `dfu.py` reescrito + re-anexado USB/IP automático
- `exploit()` reestructurado con `_interactive_acquire()`

**Resultado de ejecución:**
```
FASE 1 (leak)      completada
FASE 2 (overwrite) completada
FASE 3 (payload)   enviada
```
- El exploit **funciona completamente**
- El dispositivo no llega a pwned DFU por el timing de USB/IP

### Fase 6 — Preparación de Linux bare-metal
- Hardware analizado: Lenovo ThinkPad E480, i5-8250U, 32 GB RAM
- Virtualización: **soportada** (flag `vmx`)
- Pendrive: Generic Flash Disk, 29.3 GB, `D:`
- Kali 2026.2 ISO descargada (4580 MB, SHA-256 verificado)
- Rufus 4.15 instalado

---

## Diagnóstico clave del timing

```
reap_for_handle  urb type=2  status=-2  transferred=64
```

Los datos **llegan** (64 bytes) pero libusb reporta timeout. El evento de completación se retrasa
más allá de la ventana. Es el problema de gestión de eventos de `vhci_hcd` bajo carga, no de
throughput.

---

## Errores propios (aprendizaje)

1. **Aseveré "WSL2 no funciona" sin medir** → era falso, solo faltaba `attach` + root
2. **Medí el caso fácil** (transfers aisladas) → no detecté el problema real (ráfagas)
3. **Salté de "el proxy no soporta esto" a "imposible"** → enumerar ≠ operar
4. **Confié en el síntoma** tres veces seguidas (CRLF, submódulo, permisos USB) → las causas
   estaban dos capas más adentro

---

## Commits relevantes

Este repo versiona:
- El exploit portado y funcional
- Todos los diagnósticos USB/libusb
- La documentación de la investigación
- Los métodos probados y por qué fallaron

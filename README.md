# checkm8-lab

Investigación y port del exploit **checkm8** (CVE-2019-8900) para ejecutar en **WSL2** sobre Windows.

**Dispositivo objetivo:** iPhone 7 GSM (iPhone9,3 / d101ap), chip A9 / t8010, iBoot-2696.0.0.1.33

---

## ⚠️ Aviso legal

checkm8 es un exploit de bootrom real. Este proyecto es **investigación de seguridad** sobre
dispositivos de propiedad propia. Usarlo para evadir Activation Lock o sobre dispositivos ajenos
es ilegal en la mayoría de jurisdicciones.

---

## Estado actual

| Componente | Estado |
|---|---|
| Puerto de exploit Python 2 → Python 3 | ✅ Funciona |
| Las 3 fases del exploit (leak/overwrite/payload) | ✅ Se ejecutan |
| Transfers USB de control (async y sync) | ✅ Verificados |
| Pwned DFUrusbaybado | ❌ No logr��do aún — limitado por timing USB/IP |
| Entorno bare-metal Linux | ⏳ Pendiente |

**El bloqueo no es de software, es de timing.** Ver `docs/INVESTIGATION.md`.

---

## Estructura

```
exploit/          Exploit checkm8 portado a Python 3 (FUNCIONAL)
  bin/            12 shellcodes ARM (checkm8, limera1n, etc.)
diagnostics/      Scripts de diagnóstico USB/libusb developed durante la investigación
tools/            Herramientas originales + tests de latencia
  ipwndfu/        Repo original de axi0mX (referencia, Python 2)
  SSHRD_Script/   SSH Ramdisk Script (para el objetivo final)
docs/             Documentación de la investigación
dumps/            Dumps de SecureROM (pendiente)
logs/             Logs de ejecución
```

---

## Uso rápido (Linux nativo o WSL2)

```bash
# 1. Verificar que el iPhone está en DFU y visible
lsusb | grep 05ac:1227

# 2. Verificar estado (pwned o no)
python3 exploit/check_pwned.py

# 3. Ejecutar el exploit
cd exploit && python3 run_exploit.py
```

⚠️ **El exploit pide reconexión manual del cable** tras cada fase USB reset. En Linux nativo el
dispositivo reaparece solo; en WSL2 hay que desconectar/reconectar el cable físico.

---

## Documentación

- [`docs/INVESTIGATION.md`](docs/INVESTIGATION.md) — Hallazgos técnicos, timings, por qué falló cada método
- [`docs/PORTING_NOTES.md`](docs/PORTING_NOTES.md) — Cambios exactos del puerto Python 2→3
- [`docs/SETUP_WSL.md`](docs/SETUP_WSL.md) — Configuración de WSL2 + usbipd
- [`docs/SETUP_LINUX.md`](docs/SETUP_LINUX.md) — Instalación de Kali Linux en USB

---

## Hardware de referencia

```
Equipo    : Lenovo ThinkPad E480 (20KQS2D500)
CPU       : Intel i5-8250U @ 1.60GHz (4 núcleos / 8 hilos)
RAM       : 31.9 GB
GPU       : Intel UHD 620
Disco     : Kingston SA400S 447 GB (SATA, Windows)
SO        : Windows 11 Pro build 26200
```

---

## Timeline de la investigación

1. **Auditoría de seguridad** del `SSHRD_Script` — limpio, sin malware
2. **WSL2 + usbipd**: el dispositivo se detecta pero `checkm8` falla por timing
3. **Diagnóstico de latencia**: 0.5 ms mediana, 1.8 ms máximo vía USB/IP
4. **Litera1n (nativo Windows)**: falló — `libusb-win32` no exporta `libusb_wrap_device`
5. **Puerto a Python 3 + WSL2**: las 3 fases corren, pero el timing no da
6. **Conclusión**: se requiere Linux bare-metal para el timing nativo del USB

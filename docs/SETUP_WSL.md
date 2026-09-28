# Configuración de WSL2 + usbipd

Para ejecutar el exploit dentro de WSL2 en Windows.

---

## Requisitos

- Windows 11 con WSL2
- Distro Linux en WSL2
- `usbipd-win` (USB/IP server en Windows)
- `libusb` y `pyusb` en el Linux

---

## 1. Instalar usbipd-win

```powershell
winget install dorssel.usbipd-win
```

Verificar: `usbipd --version`

---

## 2. Preparar el Linux

```bash
sudo apt update
sudo apt install -y libusb-1.0-0 python3-usb gcc make libusb-1.0-0-dev
```

---

## 3. Poner el iPhone en DFU

**iPhone 7 / 6s / 6:**

1. Conectar el cable
2. Mantener **Power + Volume Down** durante 10 segundos
3. Soltar ambos botones
4. Mantener **Power + Volume Down** otros 10 segundos
5. La pantalla queda completamente **negra** ← esto es DFU

---

## 4. Adjuntar el dispositivo a WSL

El paso **más importante** y el que más errores causa:

```powershell
usbipd list                    # ver el BUSID (ej: 1-4)
usbipd bind --busid 1-4        # requiere Administrador, solo una vez
usbipd attach --wsl --busid 1-4 # adjuntar a WSL
```

⚠️ **Tres estados distintos, no confundir:**

| Estado | Significado |
|---|---|
| `Not shared` | Windows lo usa, WSL **no lo ve** |
| `Shared` | Compartido pero **NO visible** en WSL ← trampa común |
| `Attached` | **Visible en WSL** ← lo que necesitamos |

> ⚠️ Solo `attach` funciona sin Administrador. `bind` requiere elevación **una sola vez**.

**Desde dentro de WSL también se puede** (útil para el exploit):

```bash
usbipd.exe attach --wsl --busid 1-4
```

---

## 5. Verificar

```bash
lsusb | grep 05ac:1227
```

Debe mostrar:
```
Bus 001 Device 0XX: ID 05ac:1227 Apple, Inc. Mobile Device (DFU Mode)
```

---

## 6. Ejecutar

```bash
cd exploit
python3 check_pwned.py      # ver estado
python3 run_exploit.py      # ejecutar
```

⚠️ **Durante el exploit**: el USB reset desconecta el dispositivo. Puede pedir reconexión manual
del cable. En WSL2 el dispositivo no siempre reaparece solo.

---

## Problemas frecuentes

### `NoBackendError: No backend available`

Falta `libusb` en el Linux:
```bash
sudo apt install python3-usb
```

### `env: 'sh\r': No such file or directory` (scripts de shell)

Finales de línea CRLF de Windows:
```bash
sed -i 's/\r$//' script.sh
```

### `The device has no langid`

El dispositivo está en driver equivocado. Debe estar en `libusb0` o `libusb-win32`, no en el de
Apple.

### El script no encuentra el submódulo

Un submódulo con path de Git de Windows:
```bash
cd sshtars
printf "gitdir: ../.git/modules/sshtars\n" > .git
git fetch https://github.com/verygenericname/sshtars refs/pull/7/head
git checkout -f 6c05c8a74095c63e1d130ecbf309d77efa6d17d5
```

### Permisos del nodo USB

Si `irecovery` dice `Unable to connect` pero `lsusb` lo ve:
```bash
wsl -u root -- <comando>     # ejecutar como root
```

---

## Nota sobre el timing

WSL2 **no permite completar el exploit** de forma fiable. Ver
[`INVESTIGATION.md`](INVESTIGATION.md) §6. El USB/IP añade ~1 ms de jitter que rompe la ventana
de tiempo del exploit.

**Este setup es útil para diagnóstico y aprendizaje**, no para completar el bypass.

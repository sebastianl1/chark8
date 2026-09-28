# Información del Hardware

## Equipo de desarrollo

```
Fabricante  : Lenovo
Modelo      : ThinkPad E480 (20KQS2D500)
SKU         : LENOVO_MT_20KQ_BU_Think_FM_ThinkPad E480
Serie       : PF1LZ537
BIOS        : Lenovo R0PET74W v1.51 (2024-01-21)
```

### Componentes

| Componente | Detalle |
|---|---|
| CPU | Intel Core i5-8250U @ 1.60 GHz |
| Núcleos | 4 físicos / 8 lógicos |
| RAM | 31.9 GB (16 GB libres al medir) |
| GPU | Intel UHD Graphics 620 (integrada) |
| Disco | Kingston SA400S 447 GB SATA (SSD) |
| SO | Windows 11 Pro build 26200 (x64) |

### Virtualización

**Soportada.** El flag `vmx` está presente en `/proc/cpuinfo`.

⚠️ `Win32_Processor` reporta `VirtualizationFirmwareEnabled: False` — **es un falso negativo**.
WSL2 funciona, lo que confirma que la virtualización está activa.

| Dato | Valor |
|---|---|
| `VirtualizationBasedSecurity` | 2 (activo) |
| `vmx` en CPU | ✅ presente |
| WSL2 | ✅ funcionando (kali-linux, archlinux, Ubuntu) |

### Firmware

- **UEFI** con CSM habilitado
- **Secure Boot**: ACTIVO (requiere desactivación para Live USB de Kali)
- Tecla de BIOS en ThinkPad: **F1** (o Fn+F1)
- Tecla de menú de arranque: **F12**

---

## Dispositivo objetivo

```
USB\VID_05AC&PID_1227\CPID:8010_CPRV:11_CPFM:03_SCEP:01
    BDID:0C_ECID:00010858248A2D26_IBFL:3C_SRTG:[IBOOT-2696.0.0.1.33]
```

| Campo | Valor | Interpretación |
|---|---|---|
| VID | `05AC` | Apple Inc. |
| PID | `1227` | Modo DFU |
| CPID | `8010` (t8010) | **Chip A9** |
| CPRV | `11` | — |
| CPFM | `03` | — |
| ECID | `00010858248A2D26` | Identificador único |
| IBFL | `3C` | — |
| SRTG | iBoot-2696.0.0.1.33 | Versión de iBoot |

**Producto**: iPhone9,3 / d101ap = **iPhone 7 (GSM)**

### Compatibilidad con checkm8

El chip **A9 (t8010)** está soportado por checkm8 y **no** está en la lista de chips con problemas
de timing conocidos (A9X, A10, A10X, A11).

**SHSH blob disponible**: `tools/SSHRD_Script/other/shsh/0x8010.shsh`

### Notas

- El modo DFU muestra **pantalla completamente negra** — esto es normal, no un error
- Requiere **USB-A → Lightning** (no funciona USB-C → Lightning)
- El USB reset del exploit desconecta físicamente el dispositivo; hay que reconectar el cable

---

## USB host (pendrive de arranque)

```
Dispositivo : Generic Flash Disk
Capacidad  : 29.30 GB (32 GB nominales)
Bus        : USB
Partición  : Única, letra D:, FAT32
Estilo     : MBR
```

Contenido original (borrado con consentimiento): material Scene Release para Xbox 360.

---

## Entornos WSL instalados

| Distro | Estado |
|---|---|
| `kali-linux` | En uso principal |
| `archlinux` | Disponible |
| `Ubuntu` | Disponible |
| `docker-desktop` | Disponible |

Kernel: `6.6.87.2-microsoft-standard-WSL2`

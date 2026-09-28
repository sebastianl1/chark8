# Instalación de Kali Linux en USB

Para ejecutar el exploit con **timing USB nativo** (requisito para completar el bypass).

---

## Requisitos

- ⚠️ **Secure Boot DESACTIVADO** en el BIOS
- USB de **8 GB o más** (recomendado 16 GB+)
- La ISO de Kali (4.5 GB)

---

## 1. Descargar la ISO

```powershell
# Desde Windows
$url = "https://cdimage.kali.org/kali-2026.2/kali-linux-2026.2-installer-amd64.iso"
Invoke-WebRequest -Uri $url -OutFile kali.iso
```

**Verificar integridad** (práctica de seguridad obligatoria):

```powershell
# Hash local
Get-FileHash kali.iso -Algorithm SHA256
# Comparar con https://cdimage.kali.org/kali-2026.2/SHA256SUMS
```

Hash verificado de `kali-linux-2026.2-installer-amd64.iso`:
```
6dbefacc95e3b556c19c48e8bae39b8b505e2d3a1aba0bfb7ab62b036c3d2ba3
```

> 💡 Alternativa más ligera (~400 MB): `kali-linux-2026.2-installer-netinst-amd64.iso`
> descarga los paquetes durante la instalación. Útil si el USB es pequeño o la conexión lenta.

---

## 2. Grabar con Rufus

1. Descargar Rufus: https://rufus.ie/
2. Abrir Rufus (**como Administrador**)
3. **Dispositivo destino**: ⚠️ **el pendrive, NO el disco interno**
4. **Origen**: `Seleccionar` → la ISO descargada
5. **Esquema**: `GPT`
6. **Sistema de archivos**: el que detecte (ext4)
7. **Iniciar**

> ⚠️ **VERIFICA TRES VECES** cuál es el pendrive. Borrar el disco equivocado pierde todo Windows.

### Modos de Rufus

| Modo | Resultado |
|---|---|
| **ISO Image mode** | Live USB, cambios NO persisten |
| **DD Image mode** | Solo para imágenes .dd |

Para instalar Kali, usa el modo normal ISO.

---

## 3. Instalar Kali

1. Reiniciar el equipo
2. Pulsar **F12** repetidamente (menú de arranque de ThinkPad)
3. Seleccionar el USB (aparece como `UEFI: Generic Flash Disk`)
4. Kali arranca en modo Live
5. Elegir **"Graphical Install"**
6. Seguir el asistente:
   - Idioma: Español
   - Red: conectarse por WiFi
   - ⚠️ **Disco: el PENDRIVE (29 GB), NO el Kingston de 447 GB**
   - Particionado: "Usar todo el disco"
   - Crear usuario
7. Reiniciar cuando termine

> ⚠️ En el paso 6, el instalador muestra los discos por tamaño. **El de 29 GB es el USB.
> El de 447 GB es tu disco de Windows.**

---

## 4. Primer arranque

1. Reiniciar
2. **F12** → seleccionar el USB
3. Entrar con el usuario creado
4. Conectar el iPhone en DFU

---

## 5. Instalar dependencias

```bash
# Sistema
sudo apt update && sudo apt upgrade -y

# Para checkm8
sudo apt install -y python3 python3-usb libusb-1.0-0 libimobiledevice-utils git

# Para desarrollo
sudo apt install -y build-essential curl wget vim
```

---

## 6. Instalar opencode

```bash
curl -fsSL https://opencode.ai/install | bash
```

Alternativas:
```bash
npm install -g opencode-ai
brew install anomalyco/tap/opencode    # si instalaste Homebrew
```

**Requisito**: Node.js debe estar instalado primero.

```bash
# Instalar Node.js (método nvm, recomendado)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
source ~/.bashrc
nvm install --lts
```

---

## 7. Clonar este repositorio

```bash
git clone <URL-DEL-REMOTE> ~/checkm8-lab
cd ~/checkm8-lab
```

---

## 8. Ejecutar el exploit

```bash
# Verificar dispositivo
lsusb | grep 05ac:1227

# Ver estado
cd exploit && python3 check_pwned.py

# Ejecutar
python3 run_exploit.py
```

En Linux nativo el USB reset es instantáneo y el dispositivo reaparece solo.
**El timing nativo es lo que hace que el exploit funcione.**

---

## 9. SSH Ramdisk (objetivo final)

Una vez con pwned DFU, se puede crear una ramdisk con acceso SSH root:

```bash
./sshrd.sh 15.6      # construir el ramdisk
./sshrd.sh boot      # arrancar
./sshrd.sh ssh       # conectar (password: alpine)
```

⚠️ Requiere que el iPhone esté en DFU durante la construcción.

---

## 10. Seguridad de la ramdisk SSH

El ramdisk tiene **SSH con password `alpine` y root completo**. Es solo para un dispositivo en DFU
sin iOS instalado, pero:

- ⚠️ No conectes a redes no confiables
- ⚠️ Elimínalo después de usarlo
- ⚠️ No se restaura nada automáticamente — vuelves a iOS con un restore normal

import os, shutil, ctypes, sys

# Armar un directorio con el shim 1.0.24 + el libusb0.dll 1.2.6.0 que el shim espera
base = r"C:\Users\sebas\AppData\Local\Temp\libusbtest"
repo = r"C:\Users\sebas\checkm8-lab\native\litera1n"
os.makedirs(base, exist_ok=True)

shutil.copy(os.path.join(repo, "libusb", "VS2019", "MS64", "dll", "libusb-1.0.dll"),
            os.path.join(base, "libusb-1.0.dll"))
shutil.copy(os.path.join(repo, "libusb0.dll"), os.path.join(base, "libusb0.dll"))

import usb.backend.libusb1 as libusb1
import usb.core

target = os.path.join(base, "libusb-1.0.dll")
print("shim :", target, flush=True)
print("libusb0.dll junto al shim:", os.path.getsize(os.path.join(base, "libusb0.dll")), "bytes", flush=True)

be = libusb1.get_backend(find_library=lambda x: target)
print("backend:", be, flush=True)

d = usb.core.find(idVendor=0x05AC, idProduct=0x1227, backend=be)
print("dispositivo:", d, flush=True)
if d:
    print("SERIAL:", d.serial_number, flush=True)
    r = d.ctrl_transfer(0xA1, 3, 0, 0, 6, 1000)
    print("DFU GETSTATUS ->", r, list(r), flush=True)
    print(">>> SHIM 1.0 FUNCIONA CON DRIVER 1.4.0.0", flush=True)

import sys, os
# asegurar que se use el pyusb VENDORIZADO del repo, no el de pip
sys.path.insert(0, r"C:\Users\sebas\checkm8-lab\native\litera1n")

import usb
import usb.backend.libusb1 as libusb1
import usb.core
print("usb-core  :", usb.core.__file__, flush=True)
print("backend   :", libusb1.__file__, flush=True)
print("version   :", getattr(usb, "__version__", "(sin atributo)"), flush=True)
print("-" * 50, flush=True)

print("1. import ok", flush=True)
be = libusb1.get_backend()
print("2. get_backend ->", be, flush=True)

d = usb.core.find(idVendor=0x05AC, idProduct=0x1227, backend=be)
print("3. dispositivo:", d, flush=True)
if d is None:
    raise SystemExit("no encontrado")

print("4. SERIAL:", d.serial_number, flush=True)
r = d.ctrl_transfer(0xA1, 3, 0, 0, 6, 1000)
print("5. DFU GETSTATUS ->", r, list(r), flush=True)
print(">>> API 1.0 FUNCIONA: checkm8.py puede correr", flush=True)

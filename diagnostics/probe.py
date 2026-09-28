import usb.backend.libusb1 as libusb1
import usb.core

be = libusb1.get_backend()
print("backend   :", be)

d = usb.core.find(idVendor=0x05AC, idProduct=0x1227, backend=be)
print("dispositivo:", d)

if d is None:
    raise SystemExit("no encontrado")

try:
    print("SERIAL      :", d.serial_number)
    print(">>> strings OK: hay control transfers")
except Exception as e:
    print("SERIAL FALLA:", type(e).__name__, e)

# DFU_GETSTATUS - la peticion base del exploit checkm8
try:
    r = d.ctrl_transfer(0xA1, 3, 0, 0, 6, 1000)
    print("DFU GETSTATUS ->", r, "bytes:", list(r))
    print(">>> EXPLOIT LISTO")
except Exception as e:
    print("GETSTATUS FALLA:", type(e).__name__, e)

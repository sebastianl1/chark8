import usb.backend.libusb0 as libusb0
import usb.core

print("1. import ok", flush=True)
try:
    be = libusb0.get_backend()
    print("2. get_backend ->", be, flush=True)
    if be is None:
        raise SystemExit("backend None: libusb0.dll no carga")
    devs = list(usb.core.find(find_all=True, backend=be))
    print("3. enumerados:", len(devs), flush=True)
    for d in devs:
        try:
            print("   ", hex(d.idVendor), hex(d.idProduct), flush=True)
        except Exception as e:
            print("    (descriptor falla)", e, flush=True)
    t = usb.core.find(idVendor=0x05AC, idProduct=0x1227, backend=be)
    print("4. iPhone DFU:", t, flush=True)
    if t:
        print("   SERIAL:", t.serial_number, flush=True)
        r = t.ctrl_transfer(0xA1, 3, 0, 0, 6, 1000)
        print("   DFU GETSTATUS ->", r, list(r), flush=True)
        print(">>> FUNCIONA CON BACKEND libusb0", flush=True)
except Exception as e:
    print("EXC:", type(e).__name__, e, flush=True)

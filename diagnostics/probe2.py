import sys
import usb.backend.libusb1 as libusb1

print("1. import ok", flush=True)
be = libusb1.get_backend()
print("2. get_backend ->", be, flush=True)

# esto es donde suele crashear
try:
    import usb.core
    devs = list(usb.core.find(find_all=True, backend=be))
    print("3. enumerate ok, dispositivos:", len(devs), flush=True)
    for x in devs:
        print("   ", x, flush=True)
except Exception as e:
    print("3. exception:", type(e).__name__, e, flush=True)

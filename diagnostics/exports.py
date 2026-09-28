import ctypes, ctypes.util, os

dll = r"C:\Users\sebas\AppData\Local\Temp\lw32\libusb-win32-bin-1.4.0.2\bin\amd64\libusb0.dll"
print("cargando:", dll, flush=True)
lib = ctypes.CDLL(dll)

# funciones de la API libusb 1.0 que necesita checkm8
need = [
    "libusb_init", "libusb_get_device_list", "libusb_get_device_descriptor",
    "libusb_open", "libusb_claim_interface", "libusb_alloc_transfer",
    "libusb_submit_transfer", "libusb_cancel_transfer", "libusb_wrap_device",
    "libusb_free_transfer", "libusb_set_option",
]
ok = []
for n in need:
    try:
        getattr(lib, n)
        ok.append(n)
    except AttributeError:
        pass

print(f"API 1.0 disponible: {len(ok)}/{len(need)}", flush=True)
for n in need:
    print(("  OK   " if n in ok else "  FALTA") , n, flush=True)

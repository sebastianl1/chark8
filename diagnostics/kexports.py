import ctypes, glob, os

cands = glob.glob(r"C:\Users\sebas\AppData\Local\Temp\libusbK\**\libusbK.dll", recursive=True)
need = ["libusb_init", "libusb_get_device_list", "libusb_get_device_descriptor",
        "libusb_open", "libusb_claim_interface", "libusb_alloc_transfer",
        "libusb_submit_transfer", "libusb_cancel_transfer", "libusb_wrap_device",
        "libusb_free_transfer", "libusb_get_device"]

for dll in cands:
    try:
        lib = ctypes.CDLL(dll)
    except OSError as e:
        print(f"\n{dll}\n  no cargable: {e}")
        continue
    ok = [n for n in need if hasattr(lib, n)]
    size = os.path.getsize(dll)
    print(f"\n{dll}  ({size} bytes)")
    print(f"  API 1.0: {len(ok)}/{len(need)}")
    for n in need:
        print(("    OK    " if n in ok else "    FALTA "), n)

import os, shutil, subprocess, sys

repo = r"C:\Users\sebas\checkm8-lab\native\litera1n"
shim_src = os.path.join(repo, "libusb", "VS2019", "MS64", "dll", "libusb-1.0.dll")
libusb0_versions = {
    "1.2.6.0": os.path.join(repo, "libusb0.dll"),
    "1.2.7.4": r"C:\Users\sebas\AppData\Local\Temp\lw1274\libusb-win32-bin-1.2.7.4\bin\amd64\libusb0.dll",
}

for ver, src in libusb0_versions.items():
    base = rf"C:\Users\sebas\AppData\Local\Temp\mx_{ver}"
    os.makedirs(base, exist_ok=True)
    shutil.copy(shim_src, os.path.join(base, "libusb-1.0.dll"))
    shutil.copy(src, os.path.join(base, "libusb0.dll"))

    child = r'''
import sys
import usb.backend.libusb1 as libusb1
import usb.core
t = sys.argv[1]
be = libusb1.get_backend(find_library=lambda x: t + r"\\libusb-1.0.dll")
d = usb.core.find(idVendor=0x05AC, idProduct=0x1227, backend=be)
print("SERIAL:", d.serial_number)
print("GETSTATUS:", list(d.ctrl_transfer(0xA1,3,0,0,6,1000)))
print("OK")
'''
    cf = os.path.join(base, "t.py")
    with open(cf, "w") as f:
        f.write(child)

    print(f"\n===== shim 1.0.24 + libusb0.dll {ver} (driver en disco 1.2.7.4) =====", flush=True)
    r = subprocess.run([sys.executable, "-u", cf, base], capture_output=True, text=True, timeout=60)
    if r.returncode == 0:
        print("  FUNCIONA:", r.stdout.strip())
    else:
        print(f"  CRASH exit={r.returncode:#x} ({r.returncode}) stdout={r.stdout.strip()[:120]}")

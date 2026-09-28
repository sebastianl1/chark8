import struct, sys

def arch(path):
    with open(path, "rb") as f:
        f.seek(0x3C)
        off = struct.unpack("<I", f.read(4))[0]
        f.seek(off)
        sig = f.read(4)
        machine = struct.unpack("<H", f.read(2))[0]
    return {0x8664: "x64", 0x14C: "x86", 0xAA64: "ARM64"}.get(machine, hex(machine))

for p in [r"C:\Windows\System32\libusb-1.0.dll",
          r"C:\Windows\System32\libusb0.dll",
          r"C:\Windows\System32\drivers\libusb0.sys",
          r"C:\Windows\System32\python312.dll"]:
    try:
        print(f"{p.split(chr(92))[-1]:<20} {arch(p)}")
    except Exception as e:
        print(f"{p.split(chr(92))[-1]:<20} error {e}")

print()
print("python bits:", struct.calcsize("P") * 8)

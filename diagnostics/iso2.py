import ctypes as C

dll = r"C:\Windows\System32\libusb-1.0.dll"
lib = C.CDLL(dll)

class desc(C.Structure):
    _fields_ = [("bLength", C.c_uint8), ("bDescriptorType", C.c_uint8),
                ("bcdUSB", C.c_uint16), ("bDeviceClass", C.c_uint8),
                ("bDeviceSubClass", C.c_uint8), ("bDeviceProtocol", C.c_uint8),
                ("bMaxPacketSize0", C.c_uint8), ("idVendor", C.c_uint16),
                ("idProduct", C.c_uint16), ("bcdDevice", C.c_uint16),
                ("iManufacturer", C.c_uint8), ("iProduct", C.c_uint8),
                ("iSerialNumber", C.c_uint8), ("bNumConfigurations", C.c_uint8)]

lib.libusb_init.argtypes = [C.c_void_p]; lib.libusb_init.restype = C.c_int
ctx = C.c_void_p()
print("init ->", lib.libusb_init(ctx), flush=True)

# firma correcta: usb_device ***list
lib.libusb_get_device_list.argtypes = [C.c_void_p, C.POINTER(C.POINTER(C.c_void_p))]
lib.libusb_get_device_list.restype = C.c_int
lst = C.POINTER(C.c_void_p)()
n = lib.libusb_get_device_list(ctx, C.byref(lst))
print(f"dispositivos: {n}", flush=True)

lib.libusb_get_device_descriptor.argtypes = [C.c_void_p, C.POINTER(desc)]
lib.libusb_get_device_descriptor.restype = C.c_int

for i in range(n):
    dev = lst[i]
    d = desc()
    print(f"  [{i}] pid_ptr={dev} -> leyendo descriptor...", end=" ", flush=True)
    r = lib.libusb_get_device_descriptor(dev, C.byref(d))
    print(f"ret={r} vid={d.idVendor:#06x} pid={d.idProduct:#06x}", flush=True)

print("FIN ok", flush=True)

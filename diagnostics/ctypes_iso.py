import ctypes, sys

dll = sys.argv[1] if len(sys.argv) > 1 else r"C:\Windows\System32\libusb-1.0.dll"
print("shim:", dll, flush=True)
lib = ctypes.CDLL(dll)

class libusb_device_descriptor(ctypes.Structure):
    _fields_ = [("bLength", ctypes.c_uint8), ("bDescriptorType", ctypes.c_uint8),
                ("bcdUSB", ctypes.c_uint16), ("bDeviceClass", ctypes.c_uint8),
                ("bDeviceSubClass", ctypes.c_uint8), ("bDeviceProtocol", ctypes.c_uint8),
                ("bMaxPacketSize0", ctypes.c_uint8), ("idVendor", ctypes.c_uint16),
                ("idProduct", ctypes.c_uint16), ("bcdDevice", ctypes.c_uint16),
                ("iManufacturer", ctypes.c_uint8), ("iProduct", ctypes.c_uint8),
                ("iSerialNumber", ctypes.c_uint8), ("bNumConfigurations", ctypes.c_uint8)]

lib.libusb_init.argtypes = [ctypes.c_void_p]
lib.libusb_init.restype = ctypes.c_int
ctx = ctypes.c_void_p()
print("1. libusb_init ->", lib.libusb_init(ctx), flush=True)

lib.libusb_get_device_list.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t)]
lib.libusb_get_device_list.restype = ctypes.c_int
n = ctypes.c_size_t()
r = lib.libusb_get_device_list(ctx, ctypes.byref(n))
print(f"2. libusb_get_device_list -> {r} dispositivos", flush=True)

lib.libusb_get_device_descriptor.argtypes = [ctypes.c_void_p, ctypes.POINTER(libusb_device_descriptor)]
lib.libusb_get_device_descriptor.restype = ctypes.c_int

import ctypes as C
arr = (C.c_void_p * max(n.value, 1))()
lib.libusb_get_device_list(ctx, C.byref(n))  # rellena el array
print("3. iterating descriptors...", flush=True)
for i in range(n.value):
    d = libusb_device_descriptor()
    rr = lib.libusb_get_device_descriptor(arr[i], C.byref(d))
    print(f"   [{i}] ret={rr} vid={d.idVendor:#06x} pid={d.idProduct:#06x}", flush=True)
print("4. FIN sin crash", flush=True)

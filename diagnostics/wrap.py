import ctypes as C

lib = C.CDLL(r"C:\Windows\System32\libusb-1.0.dll")

class desc(C.Structure):
    _fields_ = [("bLength", C.c_uint8), ("bDescriptorType", C.c_uint8),
                ("bcdUSB", C.c_uint16), ("bDeviceClass", C.c_uint8),
                ("bDeviceSubClass", C.c_uint8), ("bDeviceProtocol", C.c_uint8),
                ("bMaxPacketSize0", C.c_uint8), ("idVendor", C.c_uint16),
                ("idProduct", C.c_uint16), ("bcdDevice", C.c_uint16),
                ("iManufacturer", C.c_uint8), ("iProduct", C.c_uint8),
                ("iSerialNumber", C.c_uint8), ("bNumConfigurations", C.c_uint8)]

class ctx_t(C.Structure):
    _fields_ = [("usb_bus", C.c_void_p), ("root_dev", C.c_void_p),
                ("devices", C.c_void_p), ("dev_root_next", C.c_void_p),
                ("initial_descriptor", desc), ("last_status", C.c_int),
                ("usb_control_msg", C.c_void_p), ("default_control",
                 C.c_void_p * 3 * 8), ("auto_detach", C.c_int)]

lib.libusb_init.argtypes = [C.c_void_p]; lib.libusb_init.restype = C.c_int
ctx = c = C.c_void_p()
print("1. init ->", lib.libusb_init(ctx), flush=True)

lib.libusb_get_device_list.argtypes = [C.c_void_p, C.POINTER(C.POINTER(C.c_void_p))]
lib.libusb_get_device_list.restype = C.c_int
lst = C.POINTER(C.c_void_p)()
n = lib.libusb_get_device_list(ctx, C.byref(lst))
print(f"2. dispositivos: {n}", flush=True)

# libusb_wrap_device: es lo que usa pyusb para crear cada objeto Device
lib.libusb_wrap_device.argtypes = [C.c_void_p, C.c_void_p]
lib.libusb_wrap_device.restype = C.c_void_p
for i in range(n):
    print(f"3.{i} libusb_wrap_device({lst[i]}) ...", end=" ", flush=True)
    h = lib.libusb_wrap_device(ctx, lst[i])
    print(f"-> handle={h}", flush=True)

print("4. wrap_device OK en todos", flush=True)

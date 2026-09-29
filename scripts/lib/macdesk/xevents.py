"""A single blocking X11 connection; no subprocess watcher and no polling."""
import ctypes as C


class XEvents:
    def __init__(self):
        self.lib = C.CDLL('libX11.so.6')
        signatures = {
            'XOpenDisplay': (C.c_void_p, [C.c_char_p]),
            'XDefaultRootWindow': (C.c_ulong, [C.c_void_p]),
            'XConnectionNumber': (C.c_int, [C.c_void_p]),
            'XSelectInput': (C.c_int, [C.c_void_p, C.c_ulong, C.c_long]),
            'XPending': (C.c_int, [C.c_void_p]),
            'XNextEvent': (C.c_int, [C.c_void_p, C.c_void_p]),
            'XFlush': (C.c_int, [C.c_void_p]),
            'XCloseDisplay': (C.c_int, [C.c_void_p]),
        }
        for name, (restype, argtypes) in signatures.items():
            func = getattr(self.lib, name)
            func.restype, func.argtypes = restype, argtypes
        self.display = self.lib.XOpenDisplay(None)
        if not self.display:
            raise OSError('X11 unavailable')
        self.root = self.lib.XDefaultRootWindow(self.display)
        self.lib.XSelectInput(self.display, self.root, 1 << 17)  # StructureNotify
        self.lib.XFlush(self.display)

    def fileno(self):
        return self.lib.XConnectionNumber(self.display)

    def drain(self):
        changed = False
        event = (C.c_long * 24)()
        while self.lib.XPending(self.display):
            self.lib.XNextEvent(self.display, C.byref(event))
            changed |= C.cast(event, C.POINTER(C.c_int))[0] == 22  # ConfigureNotify
        return changed

    def close(self):
        self.lib.XCloseDisplay(self.display)

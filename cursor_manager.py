import ctypes
import sys
import atexit
import signal

class CursorManager():
    def __init__(self) -> None:
        self.cursors = {}
        self.create()
        atexit.register(self.restore)
        signal.signal(signal.SIGINT, self.restore)
        signal.signal(signal.SIGTERM, self.restore)

    def create(self):
        buffA = bytearray(32*4)
        buffB = bytearray(32*4)

        for i in range(len(buffA)):
            buffA[i]=0xFF
            buffB[i]=0x00

        buffA[0] = 0x00
        buffA[1] = 0x00
        buffB[0] = 0xFF
        buffB[1] = 0xFF

        bA = ctypes.c_ubyte * len(buffA)
        bB = ctypes.c_ubyte * len(buffB)

        for id in [32512, 32513, 32514, 32515, 32516, 32642, 32643, 32644, 32645, 32646, 32648, 32649, 32650]:
            h_cursor = ctypes.windll.user32.LoadCursorA(0,id)
            h_default = ctypes.windll.user32.CopyImage(h_cursor, 2,0,0,0x00000040)
            h_blank = ctypes.windll.user32.CreateCursor(0,0,0,32,32,bA.from_buffer(buffA), bB.from_buffer(buffB))
            self.cursors[id] =  {'default': h_default, 'blank': h_blank}

    def set_cursor_visibility(self, v):
        for id, handles in self.cursors.items():
            h_cursor = ctypes.windll.user32.CopyImage(handles['default'] if v else handles['blank'],2,0,0,0,0x00000040)
            res = ctypes.windll.user32.SetSystemCursor(h_cursor, id)

    def restore(self, *args):
        self.set_cursor_visibility(True)

if __name__ == "__main__":
    cursor_manager = CursorManager()

    import time
    try:
        for i in range(5):
            cursor_manager.set_cursor_visibility(False)
            time.sleep(2)
            cursor_manager.set_cursor_visibility(True)
            time.sleep(2)
    finally:
        cursor_manager.set_cursor_visibility(True)


import global_vars as gv
from cursor_manager import CursorManager
from monitors_manager import MonitorsManager
from mouse_manager import MouseManager


if __name__ == "__main__":
    import time
    import tkinter as tk

    window = tk.Tk()
    gv.cursor_manager = CursorManager()
    gv.monitors_manager = MonitorsManager()
    gv.mouse_manager = MouseManager(window.winfo_id())
    window.withdraw()

    print(str(gv.monitors_manager))

    stop = False
    try:
        while(not stop):
            window.update()
            gv.mouse_manager.master_loop_iter()
            time.sleep(0.01)

            print(gv.mouse_manager.virtual_pos,end="\r")
    finally:
        if(gv.cursor_manager is not None):
            gv.cursor_manager.set_cursor_visibility(True)
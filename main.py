import global_vars as gv
from cursor_manager import CursorManager
from monitors_manager import MonitorsManager
from mouse_manager import MouseManager
from server import start_server_thread
from queue import Queue

if __name__ == "__main__":                                                                                                                                                                                                                                            
    import time
    import tkinter as tk

    window = tk.Tk()
    gv.cursor_manager = CursorManager()
    gv.monitors_manager = MonitorsManager()
    gv.mouse_manager = MouseManager(window.winfo_id())
    gv.command_queues = {}
    window.withdraw()

    print(str(gv.monitors_manager))

    def moved_cb(data):
        ##print("Moved:",data)
        #print("Moved:",len(gv.command_queues))
        if(not data["monitor"].is_distant):
            return
        if(len(gv.command_queues)>0):
            gv.command_queues[list(gv.command_queues.keys())[0]].put({"cmd":"move","pos":data["monitor_pos"]})

    gv.mouse_manager.move_callbacks.append(moved_cb)

    start_server_thread()

    stop = False
    try:
        while(not stop):
            window.update()
            gv.mouse_manager.master_loop_iter()
            time.sleep(0.01)

            #print(gv.mouse_manager.virtual_pos,end="\r")
    finally:
        if(gv.cursor_manager is not None):
            gv.cursor_manager.set_cursor_visibility(True)
import global_vars as gv
from cursor_manager import CursorManager
from devices_manager import DevicesManager
from monitors_manager import MonitorsManager
from server import start_server_thread

if __name__ == "__main__":
    import time
    import tkinter as tk

    window = tk.Tk()
    gv.cursor_manager = CursorManager()
    gv.monitors_manager = MonitorsManager()
    gv.devices_manager = DevicesManager(window.winfo_id())
    gv.command_queues = {}
    window.withdraw()

    print(str(gv.monitors_manager))

    def mouse_cb(data):
        ##print("Moved:",data)
        # print("Moved:",len(gv.command_queues))
        if not data["monitor"].is_distant:
            return
        if len(gv.command_queues) > 0:
            gv.command_queues[list(gv.command_queues.keys())[0]].put({"cmd": data["cmd"], "pos": data["monitor_pos"]})

    def key_cb(data):
        print("Keyboard:", data)
        # if(not data["monitor"].is_distant):
        #     return
        if len(gv.command_queues) > 0:
            gv.command_queues[list(gv.command_queues.keys())[0]].put(
                {"cmd": "key", "key": data["key"], "type": data["type"]}
            )

    gv.devices_manager.mouse_callbacks.append(mouse_cb)
    gv.devices_manager.key_callbacks.append(key_cb)

    start_server_thread()

    stop = False
    try:
        while not stop:
            window.update()
            gv.devices_manager.master_loop_iter()
            time.sleep(0.01)

            # print(gv.devices_manager.virtual_pos,end="\r")
    finally:
        if gv.cursor_manager is not None:
            gv.cursor_manager.set_cursor_visibility(True)

import winrawin
import mouse

from pynput.mouse import Controller as MouseController, Listener as MouseListener
import global_vars as gv

from monitors_manager import MonitorsManager


class MouseManager():
    def __init__(self, hwnd) -> None:
        self.virtual_pos = mouse.get_position()
        self.last_virtual_pos = self.virtual_pos
        
        self.ctrl = MouseController()
        self.listener = MouseListener()
        self.listener.start()

        self.hwnd = hwnd
        winrawin.hook_raw_input_for_window(hwnd, self.handle_event, device_types = ('Pointer', 'Mouse'))

        self.inside = None#gv.monitors_manager.get_monitor(self.virtual_pos)
        self.last_inside = None

        self.move_callbacks = []


    def __del__(self):
        self.listener.stop()
        
    def handle_event(self, e: winrawin.RawInputEvent):
        if e.event_type == 'move':
            #print(f"Mouse move: {e.device.vendor_name} : {e.delta_x},{e.delta_y}")
            self.virtual_pos = (self.virtual_pos[0]+e.delta_x, self.virtual_pos[1]+e.delta_y)
        elif e.event_type == 'down':
            print(f"Pressed {e.name} on {e.device_type} {e.device.handle}")
        else:
            print(e)

    def set_local_mouse(self, p) -> None:
        p = mouse.get_position()
        self.ctrl.move(self.virtual_pos[0]-p[0],self.virtual_pos[1]-p[1])

    def master_loop_iter(self):
        self.inside = gv.monitors_manager.get_monitor(self.virtual_pos)
        
        if(self.inside is None):
            self.virtual_pos, self.inside = gv.monitors_manager.project_to_closest(self.virtual_pos)

        just_changed = (self.inside != self.last_inside)

        if(self.inside is None):
            return

        if(self.inside.is_distant):
            self.listener._suppress = True

            local = gv.monitors_manager.project_to_closest_local(self.virtual_pos)
            self.set_local_mouse(local)
            if(just_changed):
                self.set_local_mouse(self.virtual_pos)
                if(gv.cursor_manager is not None):
                    gv.cursor_manager.set_cursor_visibility(False)
        else:
            self.listener._suppress = False
            if(just_changed):
                self.set_local_mouse(self.virtual_pos)
                if(gv.cursor_manager is not None):
                    gv.cursor_manager.set_cursor_visibility(True)
            self.virtual_pos = mouse.get_position()
        
        if(len(self.move_callbacks) and 
            self.last_virtual_pos[0] != self.virtual_pos[0] or self.last_virtual_pos[1] != self.virtual_pos[1]):

            monitor_pos = (self.virtual_pos[0]-self.inside.x, self.virtual_pos[1]-self.inside.y)
            #print(virtual_pos, " Distant position:", pdist)

            for cb in self.move_callbacks:
                cb({"vpos":self.virtual_pos, "monitor":self.inside, "monitor_pos":monitor_pos})

        self.last_virtual_pos = self.virtual_pos
        self.last_inside = self.inside


if __name__ == "__main__":
    import time
    import tkinter as tk
    from cursor_manager import CursorManager
    window = tk.Tk()
    gv.cursor_manager = CursorManager()
    gv.monitors_manager = MonitorsManager()
    gv.mouse_manager = MouseManager(window.winfo_id())
    window.withdraw()

    print(str(gv.monitors_manager))

    def moved_cb(data):
        print("Moved:",data)

    gv.mouse_manager.move_callbacks.append(moved_cb)

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
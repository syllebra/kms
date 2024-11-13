import ctypes

import mouse
import winrawin
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Controller as MouseController
from pynput.mouse import Listener as MouseListener

import global_vars as gv
from monitors_manager import MonitorsManager


class DevicesManager:
    def __init__(self, hwnd) -> None:
        self.virtual_pos = mouse.get_position()
        self.last_virtual_pos = self.virtual_pos

        self.mouse_controller = MouseController()
        self.mouse_listener = MouseListener()
        self.mouse_listener.start()

        self.keyboard_controller = KeyboardController()
        self.keyboard_listener = KeyboardListener()
        self.keyboard_listener.start()

        self.hwnd = hwnd
        winrawin.hook_raw_input_for_window(
            hwnd, self._handle_event, device_types=("Pointer", "Mouse", "Keyboard", "Keypad")
        )

        self.inside = None  # gv.monitors_manager.get_monitor(self.virtual_pos)
        self.last_inside = None

        self.mouse_callbacks = []
        self.key_callbacks = []

        self.kb_state = {}
        self.mouse_bttn_state = {}

    def __del__(self):
        self.mouse_listener.stop()

    def _handle_event(self, e: winrawin.RawInputEvent):
        if e.device_type in ["mouse", "pointer"]:
            cb_evt = None
            if e.event_type == "move":
                # print(f"Mouse move: {e.device.vendor_name} : {e.delta_x},{e.delta_y}")
                self.virtual_pos = (self.virtual_pos[0] + e.delta_x, self.virtual_pos[1] + e.delta_y)
            elif e.event_type in ["up", "down"]:
                # print(f"{"Released" if e.event_type == "up" else "Pressed"} {e.name} on {e.device_type}
                #   {e.device.vendor_name}")
                previous_state = self.mouse_bttn_state.get(e.name, False)
                current_state = e.event_type == "down"
                if current_state != previous_state:
                    code = e.name[-1] if "thumb" in e.name else e.name[0]
                    cb_evt = f"m{'d' if current_state else 'u'}{code}"
                self.mouse_bttn_state[e.name] = current_state
            elif "wheel" in e.event_type:
                cb_evt = f"mw{'d' if "down" in e.event_type else 'u'}"
            else:
                print("Unhandled Mouse event:", e)

            if cb_evt is not None:
                for cb in self.mouse_callbacks:
                    cb(
                        {
                            "cmd": cb_evt,
                            "vpos": self.virtual_pos,
                            "monitor": self.inside,
                            "monitor_pos": self._monitor_pos(),
                        }
                    )

        elif e.device_type in ["keyboard", "keypad"]:
            if e.event_type in ["up", "down"]:
                key = e.code
                vk = ctypes.windll.user32.MapVirtualKeyW(e.code, 3)
                if vk != 0:
                    key = vk
                if key not in self.kb_state or self.kb_state[key] != e.event_type:
                    # print(e.event_type, e.code, vk)
                    self.kb_state[key] = e.event_type
                    if self.inside is not None and self.inside.is_distant:
                        for cb in self.key_callbacks:
                            cb({"key": key, "type": e.event_type})
            else:
                print("Unhandled Keyboard event:", e)
        else:
            print("Unhandled unknown event:", e)

    def set_local_mouse(self, p) -> None:
        p = mouse.get_position()
        self.mouse_controller.move(self.virtual_pos[0] - p[0], self.virtual_pos[1] - p[1])

    def _monitor_pos(self):
        return (self.virtual_pos[0] - self.inside.x, self.virtual_pos[1] - self.inside.y)

    def master_loop_iter(self):
        self.inside = gv.monitors_manager.get_monitor(self.virtual_pos)

        if self.inside is None:
            self.virtual_pos, self.inside = gv.monitors_manager.project_to_closest(self.virtual_pos)

        just_changed = self.inside != self.last_inside

        if self.inside is None:
            return

        if self.inside.is_distant:
            self.mouse_listener._suppress = True
            self.keyboard_listener._suppress = True

            local = gv.monitors_manager.project_to_closest_local(self.virtual_pos)
            self.set_local_mouse(local)
            if just_changed:
                self.set_local_mouse(self.virtual_pos)
                if gv.cursor_manager is not None:
                    gv.cursor_manager.set_cursor_visibility(False)
        else:
            self.mouse_listener._suppress = False
            self.keyboard_listener._suppress = False
            if just_changed:
                self.set_local_mouse(self.virtual_pos)
                if gv.cursor_manager is not None:
                    gv.cursor_manager.set_cursor_visibility(True)
            self.virtual_pos = mouse.get_position()

        if (
            len(self.mouse_callbacks)
            and self.last_virtual_pos[0] != self.virtual_pos[0]
            or self.last_virtual_pos[1] != self.virtual_pos[1]
        ):

            for cb in self.mouse_callbacks:
                cb(
                    {
                        "cmd": "move",
                        "vpos": self.virtual_pos,
                        "monitor": self.inside,
                        "monitor_pos": self._monitor_pos(),
                    }
                )

        self.last_virtual_pos = self.virtual_pos
        self.last_inside = self.inside


if __name__ == "__main__":
    import time
    import tkinter as tk

    from cursor_manager import CursorManager

    window = tk.Tk()
    gv.cursor_manager = CursorManager()
    gv.monitors_manager = MonitorsManager()
    gv.devices_manager = DevicesManager(window.winfo_id())
    window.withdraw()

    print(str(gv.monitors_manager))

    def mouse_cb(data):
        print("Moved:", data)

    def key_cb(data):
        print("Keyboard:", data)

    gv.devices_manager.mouse_callbacks.append(mouse_cb)
    gv.devices_manager.key_callbacks.append(key_cb)

    stop = False
    try:
        while not stop:
            window.update()
            gv.devices_manager.master_loop_iter()
            time.sleep(0.01)

            # print(gv.mouse_manager.virtual_pos,end="\r")
    finally:
        if gv.cursor_manager is not None:
            gv.cursor_manager.set_cursor_visibility(True)

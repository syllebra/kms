import re
import socket
import sys
import time

import mouse
import pyautogui
from pynput.keyboard import Controller as KBCtrl
from pynput.keyboard import KeyCode
from pynput.mouse import Button, Controller

# Improve performance, pyautogui has a 'fail-safe', where you get 0.1s to move the mouse to 0,0 to exit.
# https://stackoverflow.com/questions/46736652/pyautogui-press-causing-lag-when-called
# Let's remove that for now. May find other ways in the future
pyautogui.PAUSE = 0
# same thing for: https://github.com/asweigart/pyautogui/issues/67, which seems to end up with a Java praise ?!
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
numberBuffer = 0

kb_ctrl = KBCtrl()
mouse_ctrl = Controller()

buttons_map = {"l": Button.left, "r": Button.right, "m": Button.middle, "1": Button.x1, "2": Button.x2}


def perform_according(cmd):
    global numberBuffer

    # keyboard performer -- used by client
    action_key = None
    action = (None,)
    key = None
    try:
        action_key = re.match(r"<<(.*)>>", cmd)[1].split(">><<")[0]
        action, key = action_key.split("-")
    except Exception:
        pass
    # print(action, key, action_key)
    if not action and not key:
        return False
    if action == "d":
        # pyautogui.keyDown(key)
        time.sleep(0.01)
        # keyboard.press(int(key))
        print("Key Down:", int(key))
        kb_ctrl.press(KeyCode.from_vk(int(key)))
    elif action == "u":
        # pyautogui.keyUp(key)
        time.sleep(0.01)
        # keyboard.release(int(key))
        kb_ctrl.release(KeyCode.from_vk(int(key)))
        print("Key Up:", int(key))
    elif action == "move":
        # print(cmd)
        pos = key.split(",")

        p = mouse.get_position()
        mouse_ctrl.move(int(pos[0]) - p[0], int(pos[1]) - p[1])
    elif action[:2] in ["md", "mu"]:
        print(action)
        func = mouse_ctrl.press if action[1] == "d" else mouse_ctrl.release
        if action[2] in buttons_map:
            func(buttons_map[action[2]])
    elif action[:2] == "mw":
        mouse.wheel(1 if action[2] == "u" else -1)
    return True


def parseLastRequest(req):
    print(req)


def waitConnection(host):
    HOST = host
    PORT = 31998
    running = True

    while running:
        try:
            print("Waiting for host...")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.settimeout(10.0)
            s.connect((HOST, PORT))
            print(f"Connected to {HOST}:{PORT}.")

            connected = True
            while connected:
                try:
                    reply = s.recv(4096).decode()
                    result = perform_according(reply)
                    if not result:
                        print("ending Connection")
                        return None
                except socket.error:
                    print(f"Error with communication to {HOST}:{PORT}. Closing connection.")
                    connected = False
        except (ConnectionRefusedError, TimeoutError) as e:
            print(f"Unable to reach to {HOST}:{PORT} ({e})... Retrying")
        finally:
            try:
                s.close()
            except Exception:
                pass


if __name__ == "__main__":
    waitConnection(sys.argv[1] if len(sys.argv) > 1 else "localhost")

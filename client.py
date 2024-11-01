import socket 
import re
import sys
import pyautogui
from pynput.mouse import Controller, Button
import mouse


# Improve performance, pyautogui has a 'fail-safe', where you get 0.1s to move the mouse to 0,0 to exit. https://stackoverflow.com/questions/46736652/pyautogui-press-causing-lag-when-called
# Let's remove that for now. May find other ways in the future
pyautogui.PAUSE=0
# same thing for: https://github.com/asweigart/pyautogui/issues/67, which seems to end up with a Java praise ?!
pyautogui.MINIMUM_DURATION=0
pyautogui.MINIMUM_SLEEP=0
numberBuffer = 0 

mouse_ctrl = Controller()

import keyboard
import time
def perform_according(cmd):
    global numberBuffer

    # keyboard performer -- used by client
    action_key = None
    action = None,
    key = None
    try :
        action_key = re.match(r'<<(.*)>>',cmd)[1].split('>><<')[0]
        action, key = action_key.split('-')
    except:
        pass
    #print(action, key, action_key)
    if not action and not key:
        return False
    if action == 'd':
        #pyautogui.keyDown(key)
        time.sleep(.01)
        keyboard.press(int(key))
        print("Key Down:", int(key))
    elif action == 'u':
        #pyautogui.keyUp(key)
        time.sleep(.01)
        keyboard.release(int(key))
        print("Key Up:", int(key))
    elif action == 'move':
        print(cmd)
        pos = key.split(",")

        p = mouse.get_position()
        mouse_ctrl.move(int(pos[0])-p[0],int(pos[1])-p[1])
        
        # mouse_action = {
        #     'left': [-10,0],
        #     'down': [0,10],
        #     'up': [0,-10],
        #     'right': [10,0],
        #     'lclick': 'lclick',
        #     'rclick': 'rclick',
        # }.get(key)
        # if type(mouse_action) == type([]):
        #     try :
        #         current_position = pyautogui.position()
        #         newX = current_position[0] + mouse_action[0]*(numberBuffer+1)
        #         newY = current_position[1] + mouse_action[1]*(numberBuffer+1)
        #         numberBuffer = 0
        #         print('moving to: ',newX, newY)
        #         pyautogui.moveTo(newX, newY)
        #     except Exception as err:
        #         print('move err: ',err)
        #         pass
        # elif mouse_action == 'lclick':
        #     try :
        #         print('left clicking')
        #         pyautogui.click()
        #     except Exception as err:
        #         print('click left err: ',err)
        #         pass
        # elif mouse_action == 'rclick':
        #     try :
        #         print('right clicking')
        #         pyautogui.click(button='right')
        #     except Exception as err:
        #         print('click right err: ',err)
        #         pass

def parseLastRequest(req) :
    print(req)


def waitConnection(host): 
    HOST = host
    PORT = 31998
    running = True
    
    while(running):
        try:
            print('Waiting for host...')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            s.settimeout(10.0)
            s.connect((HOST, PORT))
            print(f"Connected to {HOST}:{PORT}.")

            connected = True
            while connected:
                try:
                    reply = s.recv(4096).decode()
                    result = perform_according(reply)
                    if result == False: 
                        print('ending Connection')
                        return None
                except socket.error:
                    print(f"Error with communication to {HOST}:{PORT}. Closing connection.")
                    connected = False
        except (ConnectionRefusedError, TimeoutError) as e:
            print(f"Unable to reach to {HOST}:{PORT} ({e})... Retrying")
        finally:
            try:
                s.close()
            except:
                pass
    
if __name__ == "__main__" :
    waitConnection(sys.argv[1] if len(sys.argv) > 1 else 'localhost')

import errno
import socket
import time
import threading 
import keyboard
import global_vars as gv
from queue import Queue

HOST = '0.0.0.0'
PORT = 31998

state = {}

def is_socket_valid(socket_instance):
    """ Return True if this socket is connected. """
    if not socket_instance:
        return False

    try:
        socket_instance.getsockname()
    except socket.error as err:
        err_type = err.args[0]
        if err_type == errno.EBADF:  # 9: Bad file descriptor
            return False

    try:
        socket_instance.getpeername()
    except socket.error as err:
        err_type = err.args[0]
        if err_type in [errno.EBADF, errno.ENOTCONN]:  #   9: Bad file descriptor.
            return False                               # 107: Transport endpoint is not connected

    return True

class InputListenerSocketSend:
    def __init__(self, connection, addr) -> None:
        self.connection = connection
        self.addr = addr
        self.stop = False
        gv.command_queues[addr] = Queue()

    def runloop(self):
        keyboard.hook(self.handle_keys_callback, suppress=True)
        
        #keyboard.wait()
        while(not self.stop):

            if(self.addr in gv.command_queues):
                cmd = gv.command_queues[self.addr].get()
                print("Treating ", cmd)
                if(cmd["cmd"]=="move"):
                    self.connection.send(f'<<{"move"}-{cmd["pos"][0]},{cmd["pos"][1]}>>'.encode())
            #print("loop")
            #time.sleep(0.05)
            pass
        
        keyboard.unhook_all()
        keyboard.unhook_all_hotkeys()
        print(f"Closing connection {self.addr}.")
        if(self.addr in gv.command_queues):
            del gv.command_queues[self.addr]

    def handle_keys_callback(self, e: keyboard.KeyboardEvent):
        try:
            key = e.scan_code#(e.scan_code, e.name, e.is_keypad)
            if(key not in state or state[key] != e.event_type):
                print(e.to_json())
                state[key] = e.event_type
                self.connection.send(f'<<{"d"if e.event_type=="down" else "u"}-{e.scan_code}>>'.encode())

                # if(e.event_type == "down"):
                #     keyboard.press(e.scan_code)
                # else:
                #     keyboard.release(e.scan_code)
        except ConnectionError as ce:
            print(f"Unable to reach client with socket {self.connection} ({ce}). Closing...")
            self.stop = True
        except ConnectionResetError as ce:
            print(f"Connection reset with {self.connection} ({ce}). Closing...")
            self.stop = True
        except Exception as e:
            print(f"Exception ({ce}). Closing...")
            self.stop = True

def accept_client(connection,addr):
    listen = InputListenerSocketSend(connection,addr)
    listen.runloop()

def start_server():
    # socket connection for inter-computer connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    s.settimeout(10.0)
    while True: 
        print("Waiting for client...")
        try:
            connection, addr = s.accept()
            print(f'Client accepted {addr}. Starting listening thread...')
            t = threading.Thread(target = accept_client,args = (connection,addr))
            t.start()
            t.join()
            try:
                connection.close()
            except:
                pass    

        except socket.timeout:
            print("Timeout. Retry...")

def start_server_thread():
    t = threading.Thread(target = start_server, args = ())
    t.start()
    return t

if __name__ == "__main__":
    start_server()
  

    while(True):
        pass


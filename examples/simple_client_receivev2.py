import socket, pickle, time, argparse
import numpy as np

from utils import Cabinet


class SocketClient(object):
    """docstring for Socketer."""

    def __init__(self, identifier, counter, split_at, *args, **kwargs):
        super(SocketClient, self).__init__()
        self.HEADERSIZE = 10
        host = kwargs.get("host")
        port = kwargs.get("port")
        self.host = host
        self.port = port
        self.cabinet = Cabinet()
        self.cabinet.register_values(identifier,counter,split_at)
        self.is_running = False
        self.errors = 0

    def __del__(self):
        self.cabinet.__del__()



    def run_client(self):
        self.is_running = True
        print("Starting a new thread to monitor data lenght")
        self.cabinet.thread_watcher()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            c_time = None
            print("Connection established")
            while self.is_running:
                full_msg = b""
                new_msg = True
                while True:
                    lst = 0
                    msg = s.recv(2048)
                    if new_msg:
                        try:
                            msglen = int(msg[:self.HEADERSIZE])
                            # print("msg len",msglen)
                            new_msg = False
                        except Exception as e:
                            en = e.__class__.__name__
                            if en == "ValueError":
                                self.errors +=1
                                print("errors: %s" % self.errors)
                                time.sleep(0.1)
                                if self.errors >= 70:
                                    self.is_running = False
                                    self.__del__()
                                break
                            else:
                                raise
                    full_msg += msg
                    # print(len(full_msg)-self.HEADERSIZE)
                    if (len(full_msg)-self.HEADERSIZE) == msglen:
                        # print("Full msg received")
                        data = pickle.loads(full_msg[self.HEADERSIZE:])
                        self.cabinet.received_data.append([np.array(data["screen"]), data["output"]])
                        # print(data)
                        s.sendall(b"ok")
                        new_msg = True
                        full_msg = b""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Capture training data, press ctrl+q to stop recording')
    parser.add_argument("identifier", type=str, help='An identifier for training data file')
    parser.add_argument("--r", "--resume", type=int, help="Number of file name to write to")
    parser.add_argument("--sa", "--split-at", type=int,
        help="Number that defines max len for the data, whenever this is reached the file is saved and a new one is created")
    parser.add_argument("--ip", type=str, help="The ip address to connect to")
    parser.add_argument("--port", type=int, help="The port used")
    args = parser.parse_args()
    print(args)
    hst = args.ip or "127.0.0.1"
    prt = args.port or 2890
    counter = args.r or 0
    split_at = args.sa or 1000
    all_values = "\tID: %s\n\thost: %s\n\tport: %s\n\tcounter: %s\n\tsplit: %s" % (args.identifier,hst,prt,counter,split_at)
    print("Initializing client in 3 seconds with values:\n%s" % all_values)
    time.sleep(3.5)
    s = SocketClient(args.identifier, counter, split_at,port=prt,host=hst)
    try:
        print("Opening socket")
        s.run_socket()
    except Exception as e:
        en = e.__class__.__name__
        if en == "KeyboardInterrupt":
            print("Interrupt detected closing socket and file watcher")
        else:
            raise

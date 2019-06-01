import socket, pickle, time, select

from utils import Cabinet, arg_creator

class SocketMaker(object):
    """docstring for SocketMaker."""

    def __init__(self, identifier, counter, split_at, *args, **kwargs):
        super(SocketMaker, self).__init__()
        self.HEADERSIZE = 10
        host = kwargs.get("host")
        port = kwargs.get("port")
        self.host = host
        self.port = port
        self.cabinet = Cabinet()
        self.cabinet.register_values(identifier,counter,split_at)
        self.is_running = False
        self.closed_connection = False
        self.errors = 0

    def __del__(self):
        self.cabinet.__del__()

    def run_socket(self, type):
        self.is_running = True
        if type == "client":
            self.run_client()
        elif type == "server":
            self.run_server()
        else:
            print("Unkownk type: %s" % type)

    def run_client(self):
        print("Starting a new thread to monitor data lenght")
        self.cabinet.thread_watcher()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
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

    def run_server(self):
        print("Starting a new thread to monitor data lenght")
        self.cabinet.thread_watcher()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("Binding server to %s:%i" % (self.host,self.port))
            s.bind((self.host,self.port))
            s.listen(3)
            while self.is_running:
                cs, addr = s.accept()
                with cs:
                    while not self.closed_connection:
                        full_msg = b""
                        new_msg = True
                        while True:
                            msg = cs.recv(2048)
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
                                            print("Closing connection")
                                            self.is_running = False
                                            self.__del()
                                    else:
                                        raise

                            full_msg += msg

                            if (len(full_msg)-self.HEADERSIZE) == msglen:
                                # print("Full msg received")
                                data = pickle.loads(full_msg[self.HEADERSIZE:])
                                self.cabinet.received_data.append([np.array(data["screen"]), data["output"]])
                                cs.sendall(b"ok")
                                new_msg = True
                                full_msg = b""

if __name__ == '__main__':
    args = arg_creator()
    hst = args.ip or "127.0.0.1"
    prt = args.port or 2890
    counter = args.r or 0
    split_at = args.sa or 2000
    all_values = "\tType: %s\n\tID: %s\n\thost: %s\n\tport: %s\n\tcounter: %s\n\tsplit: %s" % (args.socket, args.identifier,hst,prt,counter,split_at)
    print("Initializing client in 3 seconds with values:\n%s" % all_values)
    time.sleep(3.5)
    try:
        SocketMaker(args.identifier, counter,split_at,port=prt,host=hst).run_socket(args.socket)
    except Exception as e:
        raise

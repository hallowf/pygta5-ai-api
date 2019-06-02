import socket, select, pickle, time

from utils import Cabinet, arg_creator

class MultiSocketServer(object):
    """docstring for MultiSocketServer."""

    def __init__(self):
        super(MultiSocketServer, self).__init__()
        self.HEADERSIZE = 10
        self.host = "127.0.0.1"
        self.port = 2890
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sockets_list = [self.server_socket]
        self.clients_list = {}
        self.client_cabinets = {}
        self.is_running = False
        self.bind_interface()


    # Tries to close all sockets
    def __del__(self):
        for sock in self.sockets_list:
            if sock != self.server_socket:
                sock.close()
        self.server_socket.close()

    # Simply binds the interface and listens for connections
    def bind_interface(self):
        self.server_socket.bind((self.host,self.port))
        self.server_socket.listen()

    # Check if the message has been fully received, if not recurse until the lenght matches
    def match_length(self, client_socket, message_length, full_msg):
        # print("Checking length")
        if len(full_msg) != message_length:
            # print("Didn't receive entire message")
            # print("received lenght:", len(full_msg))
            # print("diff:", message_length - len(full_msg))
            full_msg += client_socket.recv(message_length - len(full_msg))
            return self.match_length(client_socket, message_length, full_msg)
        else:
            return full_msg

    # Receives message header with lenght and then calls match_length to check if all data was received
    def receive_msg(self,client_socket):
        full_msg = b""
        try:
            message_header = client_socket.recv(self.HEADERSIZE)
            # print("message_header", message_header)
            # Client closed connection ?
            if not len(message_header):
                return False
            message_header = message_header.decode("utf-8")
            # print("message_header decoded:", message_header)
            # print("len message_header:", len(message_header))
            message_length = int(message_header)
            full_msg = client_socket.recv(message_length)
            full_msg = self.match_length(client_socket, message_length, full_msg)
            if len(full_msg) != message_length:
                print("full_msg:%i msg_length:%i" % (len(full_msg), message_length))
                print("Failed to match length")
                return False
            else:
                return {"header": message_header, "data": full_msg}

        except Exception as e:
            en = e.__class__.__name__
            if en != "ConnectionResetError":
                print("receive_msg error:",e)
                # print(en)
            pass

    def run_server(self):
        self.is_running = True
        while self.is_running:
            # -------------------------------------------  read list,  write list, error sockets
            read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)

            for notified_socket in read_sockets:
                # someone connected accept connection
                if notified_socket == self.server_socket:
                    client_socket, client_address = self.server_socket.accept()
                    user = self.receive_msg(client_socket)

                    if user is False:
                        continue

                    self.sockets_list.append(client_socket)
                    self.clients_list[client_socket] = user
                    self.client_cabinets[client_socket] = Cabinet()

                    user_data = user['data'].decode('utf-8')
                    identifier, counter, split_at = user_data.split(":")
                    print(f"Accepted connection from {client_address[0]}:{client_address[1]} username:{identifier}")
                    print("Registering client cabinet with values: id:%s, counter:%s, split_at: %s" % (identifier,counter,split_at))
                    self.client_cabinets[client_socket].register_values(identifier, counter, split_at)
                    print("Instantiating cabinet thread")
                    self.client_cabinets[client_socket].thread_watcher()

                else:
                    message = self.receive_msg(notified_socket)

                    # sometimes this happens -> message is None
                    if message is False or message is None:
                        print(f"Closed connection from {self.clients_list[notified_socket]['data'].decode('utf-8')}")
                        self.sockets_list.remove(notified_socket)
                        del self.clients_list[notified_socket]
                        del self.client_cabinets[notified_socket]
                        continue

                    user = self.clients_list[notified_socket]
                    user_identifier = user['data'].decode('utf-8')
                    username, _, _ = user_identifier.split(":")
                    print(f"Received message from {username}")
                    # print("final len:",len(message["data"]))
                    received = pickle.loads(message["data"])

                    for client_socket in self.clients_list:
                        # if client is who sent message answer ok
                        if client_socket == notified_socket:
                            client_socket.send(b"ok")


            for notified_socket in exception_sockets:
                self.sockets_list.remove(notified_socket)
                del self.clients_list[notified_socket]
                del self.client_cabinets[notified_socket]



if __name__ == '__main__':
    args = arg_creator("multi_connections_server")
    hst = args.ip or "127.0.0.1"
    prt = args.port or 2890
    all_values = "\thost: %s\n\tport: %s" % (hst,prt)
    print("Initializing server in 3 seconds with values:\n%s" % all_values)
    time.sleep(3.5)
    try:
        MultiSocketServer().run_server()
    except Exception as e:
        raise

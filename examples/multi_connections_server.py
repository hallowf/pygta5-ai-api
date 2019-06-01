import socket
import select

HEADERSIZE = 10
IP = "127.0.0.1"
PORT = 2890

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# allows to reconnect ?
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP,PORT))
server_socket.listen()

sockets_list = [server_socket]
clients_list = {}

def receive_msg(client_socket):
    try:
        message_header = client_socket.recv(HEADERSIZE)
        # Client closed connection ?
        if not len(message_header):
            return False
        # .strip() removes HEADERSIZE space
        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}

    except Exception as e:
        en = e.__class__.__name__
        if en != "ConnectionResetError":
            print(e)
        return False


while True:
    # ---------------------------------------------  read list,  write list, error sockets
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        # someone connected accept connection
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_msg(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)

            clients_list[client_socket] = user

            print(f"Accepted connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")
        else:
            message = receive_msg(notified_socket)

            if message is False:
                print(f"Closed connection from {clients_list[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients_list[notified_socket]
                continue

            user = clients_list[notified_socket]
            print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            for client_socket in clients_list:
                if client_socket != notified_socket:
                    to_send = user['header'] + user['data'] + message['header'] + message['data']
                    client_socket.send(to_send)

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients_list[notified_socket]

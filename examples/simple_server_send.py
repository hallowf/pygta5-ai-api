import socket, pickle, time

HEADERSIZE = 10
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("127.0.0.1", 2890))
    s.listen(5)
    while True:
        lst = time.time()
        cs, addr = s.accept()

        msg = {"time": lst, "potato": 1}
        msg = pickle.dumps(msg)

        msg = bytes(f'{len(msg):<{HEADERSIZE}}', "utf-8") + msg

        cs.send(msg)

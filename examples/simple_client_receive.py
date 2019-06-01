import socket, pickle, time

HEADERSIZE = 10

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(("127.0.0.1", 2890))
    c_time = None
    while True:
        full_msg = b""
        new_msg = True
        while True:
            msg = s.recv(1024)
            if new_msg:
                try:
                    msglen = int(msg[:HEADERSIZE])
                    new_msg = False
                    c_time = time.time()
                except Exception as e:
                    en = e.__class__.__name__
                    if en == "ValueError":
                        break
                    else:
                        raise


            full_msg += msg

            if len(full_msg)-HEADERSIZE == msglen:
                # print("Full msg received")
                d = pickle.loads(full_msg[HEADERSIZE:])
                print(c_time-d["time"])
                new_msg = True
                full_msg = b""

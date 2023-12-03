import sys
import socket
import threading
import datetime

stop = False

def collectInfo():
    pass

def handle_connection(sock, addr):  # New
    with sock:
        print("Connected by", addr)
        
        while not stop:
            # Receive
            try:
                data = sock.recv(1024)

            except ConnectionError:
                print(f"Client suddenly closed while receiving")
                break
            
            print(f"Received: {data} from: {addr}")
            
            if not data:
                break
            
            # Process
            if data == b"CLOSE_CMD":
                break
            
            if data == b"GET_INFO_CMD":
                now = datetime.datetime.now()
                data = now.strftime("%d-%m-%Y %H:%M:%S")
                # data += collectInfo()
            
            # Send
            print(f"Send: {data} to: {addr}")
            
            try:
                sock.sendall(data.encode())
            
            except ConnectionError:
                print(f"Client suddenly closed, cannot send")
                break
        
        print("Disconnected by", addr)

if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            print(f"Usage: {sys.argv[0]} <host> <port>")
            sys.exit(1)

        HOST = sys.argv[1]
        PORT = int(sys.argv[2])
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv_sock:
            serv_sock.bind((HOST, PORT))
            serv_sock.listen(1)
            print("Server started")

            try:
                while True:
                    print("Waiting for connection...")
                    sock, addr = serv_sock.accept()
                    t = threading.Thread(target=handle_connection, args=(sock, addr))  # New
                    t.start()

            except KeyboardInterrupt:
                print("The server was stopped!")

            finally:
                stop = True
                serv_sock.close()

    except OSError:
        print("The server already in use")
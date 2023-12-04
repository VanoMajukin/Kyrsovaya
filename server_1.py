import sys, socket, datetime
from threading import Thread 
from PyQt5 import QtWidgets, QtCore
from server_design import Ui_MainWindow  # импорт сгенерированного файла

stop = False
sock = None
app = None

def collectInfo():
    pass

def handle_connection(sock, addr):  # New
    with sock:
        print("Connected by", addr)
        
        while not stop:
            # Receive
            try:
                data = sock.recv(1024).decode()

            except ConnectionError:
                print(f"Client suddenly closed while receiving")
                break
            
            print(f"Received: {data} from: {addr}")
            
            if not data:
                break
            
            if(data.find(" | ") != -1):
                data = data.split(" | ")
                win_geometry = data[0]
                title = data[1]
                print(f"\nwin_geometry: {win_geometry}\ntitle: {title}\n")

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

class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

class ServerThread(Thread):
    def __init__(self,window): 
        Thread.__init__(self) 
        self.window=window

    def run(self): 
        HOST = "localhost"
        PORT = 2233
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv_sock:
            serv_sock.bind((HOST, PORT))
            serv_sock.listen(1)
            print("Server started")

            try:
                while True:
                    global sock

                    print("Waiting for connection...")
                    sock, addr = serv_sock.accept()
                    t = Thread(target=handle_connection, args=(sock, addr))  # New
                    t.start()

            except KeyboardInterrupt:
                print("The server was stopped!")

            finally:
                stop = True
                serv_sock.close()


if __name__ == '__main__':
    lockfile = QtCore.QLockFile(QtCore.QDir.tempPath() + '/server_1.lock')

    if lockfile.tryLock(100):
        app = QtWidgets.QApplication(sys.argv)
        
        window = mywindow()
        serverThread=ServerThread(window)
        serverThread.start()
        window.show()
        
        sys.exit(app.exec_())
    else:
        print("Server_1 already in use")



import sys, socket
from PyQt5 import QtWidgets
from client_design import Ui_MainWindow  # импорт сгенерированного файла
from threading import Thread 

IS_RECONNECT_ENABLED = False
sock = None

class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.sendToServer_1.clicked.connect(self.server_1_Btn_click)

    # Отправка на сервер
    def server_1_Btn_click(self):
        global sock

        # получение ширины и высоты окна 
        data = str(self.ui.centralwidget.geometry().width())
        data += 'x' + str(self.ui.centralwidget.geometry().height())
        
        if(len(self.ui.lineEdit.text()) > 0):
            data += ' | ' + self.ui.lineEdit.text()
            self.ui.lineEdit.clear()

        sock.sendall(data.encode())

class ClientThread(Thread):
    def __init__(self,window): 
        Thread.__init__(self) 
        self.window=window
 
    def run(self): 
        HOST = "localhost"
        PORT = 2233
        
        is_started = False

        while IS_RECONNECT_ENABLED or not is_started:
            is_started = True
            print("\nCreate client")

            global sock
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((HOST, PORT))
                print("Client connected")
                
                try:
                    while True:                        
                        # Receive
                        data_bytes = sock.recv(1024)
                        data = data_bytes.decode()
                        print("Received:", repr(data))
                        
                        if not data:
                            print("Closed by server")
                            break

                except KeyboardInterrupt:
                    print("Client disconnected")
                
                finally:
                    sock.close()

if __name__ == "__main__":   
    app = QtWidgets.QApplication(sys.argv)
    window = mywindow()
    clientThread=ClientThread(window)
    clientThread.start()
    window.show()
    sys.exit(app.exec_())
    

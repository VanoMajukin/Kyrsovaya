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
        self.ui.sendToServer_2.clicked.connect(self.server_2_Btn_click)

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
        self.ui.listWidget.addItem('Клиент: ' + data)

    def server_2_Btn_click(self):
        data = 'swap'
        sock.sendall(data.encode())
        self.ui.listWidget.addItem('Клиент: ' + data)

    def addItem(self, data):
        self.ui.listWidget.addItem('Сервер: ' + data)

class ClientThread(Thread):
    def __init__(self, window): 
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
                        # Получение ответа от сервера
                        data_bytes = sock.recv(1024)
                        data = data_bytes.decode()
                        print("Received: ", repr(data))
                        
                        if not data:
                            print("Closed by server")
                            break

                        if(data.find(" | ") != -1):
                            data = data.split(" | ")
                            window.addItem(data[0])
                            window.addItem(data[1])
                        else:
                            window.addItem(data)

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
    

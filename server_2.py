import sys, socket, datetime, psutil
from threading import Thread 
from PyQt5 import uic
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from server_design import Ui_MainWindow  # импорт сгенерированного файла

stop = False
sock = None
app = None
BUF_SIZE = 1024

def handle_connection(sock, addr, window):
    with sock:
        answer = f'Клиент {addr} подключен'
        print(answer)
        window.addItem('Сервер: ', answer)
        
        while not stop:
            # Получение сообщения от Клиента
            try:
                data = sock.recv(BUF_SIZE).decode()

            except ConnectionError:
                print("Ошибка! Клиент отключился во время передачи сообщения!")
                break
            
            print(f"Получено: {data} от: {addr}")
            
            if not data:
                break
            
            # Добавление времени в ответное сообщение 
            now = datetime.datetime.now()
            answer = now.strftime("%d-%m-%Y %H:%M:%S")

            # Сбор информации о файле подкачки
            answer += ' размер файла подкачки: ' + str(psutil.swap_memory().total) + ' Б.'
            answer += ' свободно: ' + str(psutil.swap_memory().free) + ' Б.'
            
            # Отправка ответа Клиенту
            print(f"Отправлено: {answer} кому: {addr}")
            
            try:
                sock.sendall(answer.encode())
                window.addItem('Сервер: ', answer)
            
            except ConnectionError:
                print("Ошибка! Клиент отключился во время передачи сообщения!")
                break
        
        answer = f'Клиент {addr} отключился'
        print(answer)
        window.addItem('Сервер: ', answer)


class mywindow(QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Сервер 2")

    def addItem(self, str, data):
        self.ui.listWidget.addItem(str + data)

class ServerThread(Thread):
    def __init__(self, window): 
        Thread.__init__(self) 
        self.window = window

    def run(self): 
        HOST = "localhost"
        PORT = 2234
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv_sock:
            serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
            serv_sock.bind((HOST, PORT))
            serv_sock.listen(1)
            print("Сервер запущен")

            try:
                while True:
                    global sock

                    print("Ожидает подключения...")
                    sock, addr = serv_sock.accept()
                    t = Thread(target=handle_connection, args=(sock, addr, window))  # New
                    t.start()

            except KeyboardInterrupt:
                print("Сервер остановлен!")

            finally:
                stop = True
                serv_sock.close()


if __name__ == '__main__':
    lockfile = QLockFile(QDir.tempPath() + '/server_2.lock')

    if lockfile.tryLock(100):
        app = QApplication(sys.argv)
        
        window = mywindow()
        serverThread=ServerThread(window)
        serverThread.start()
        window.show()
        
        sys.exit(app.exec_())
    else:
        print("Сервер 2 уже запущен!")




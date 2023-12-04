import sys, socket, datetime
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
title =''
changeWinTitleStatus = 0

def handle_connection(sock, addr, window):
    with sock:
        print("Connected by", addr)
        
        while not stop:
            # Получение сообщения от Клиента
            try:
                data = sock.recv(BUF_SIZE).decode()

            except ConnectionError:
                print(f"Client suddenly closed while receiving")
                break
            
            print(f"Received: {data} from: {addr}")
            
            if not data:
                break

            
            # Добавление времени в ответное сообщение 
            now = datetime.datetime.now()
            answer = now.strftime("%d-%m-%Y %H:%M:%S")
            answer += " Ширина и высота окна получены"

            # Если пришел запрос на изменение заголовка
            if(data.find(" | ") != -1):
                data = data.split(" | ")
                window.addItem('Клиент: ', data[0])
                window.addItem('Клиент: ', data[1])

                win_geometry = data[0]
                
                global title
                title = data[1]

                window.changeTitle()
                QThread.msleep(100)

                # Проверка смены заголовка
                if(window.windowTitle() == title):
                    answer += " | Смена заголовка: Успешно"
                else:
                    answer += " | Смена заголовка: Ошибка"
            else:
                win_geometry = data
                window.addItem('Клиент: ', data)

            # Отправка ответа Клиенту
            print(f"Send: {answer} to: {addr}")
            
            try:
                sock.sendall(answer.encode())
                window.addItem('Сервер: ', answer)

            
            except ConnectionError:
                print(f"Client suddenly closed, cannot send")
                break
        
        print("Disconnected by", addr)

# Класс, необходимый для смены заголовка окна сервера
class generate_insert_frame(QThread):
    threadSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        global title

        self.threadSignal.emit(title)
        self.msleep(100)
        self.stop()

    def stop(self):
        self.quit()

class mywindow(QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def changeTitle(self):
    # Механизм сигналов/слотов передает информацию в главный поток из дочернего 
    # так как setWindowTitle() работает только из главного потока
        self.thread = generate_insert_frame() 
        self.thread.threadSignal.connect(self.setWindowTitle)
        self.thread.start()

    def addItem(self, str, data):
        self.ui.listWidget.addItem(str + data)

class ServerThread(Thread):
    def __init__(self, window): 
        Thread.__init__(self) 
        self.window = window

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
                    t = Thread(target=handle_connection, args=(sock, addr, window))  # New
                    t.start()

            except KeyboardInterrupt:
                print("The server was stopped!")

            finally:
                stop = True
                serv_sock.close()


if __name__ == '__main__':
    lockfile = QLockFile(QDir.tempPath() + '/server_1.lock')

    if lockfile.tryLock(100):
        app = QApplication(sys.argv)
        
        window = mywindow()
        serverThread=ServerThread(window)
        serverThread.start()
        window.show()
        
        sys.exit(app.exec_())
    else:
        print("Server_1 already in use")



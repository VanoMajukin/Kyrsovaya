import sys, socket, datetime
from threading import Thread 
from PyQt5 import uic
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from server_design import Ui_MainWindow  # импорт сгенерированного файла

stop = False                    # Флаг остановки дочерних потоков
sock = None                     # Сокет
BUF_SIZE = 1024                 # Размер буфера для получения сообшения
title = ''                      # Заголовок
oldAnswer = []                  # Хранилище информации о последнем запросе информации

# Обработка полученного сообщения
def handle_connection(sock, addr, window):
    global oldAnswer
    isChanged = False
    curr = []

    # Получение предыдущей информации для конкретно этого клиента
    for item in oldAnswer:
        if (item[0] == addr):
            curr = item
            break

    with sock:
        answer = f'Клиент {addr} подключен'
        print(answer)
        window.addItem('Сервер: ', answer)
        
        while not stop:
            print("curr: ", curr)

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
            
            # Если пришёл GPU
            if(data.find("GPU:") != -1):

                answer += " Получено "
                answer += data
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


# Пользовательский интерфейс
class mywindow(QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Сервер 1")


    def addItem(self, str, data):
        self.ui.listWidget.addItem(str + data)

# Класс создания сокета подключения
class ServerThread(Thread):
    def __init__(self, window): 
        Thread.__init__(self) 
        self.window = window

    def run(self): 
        HOST = "192.168.1.7"
        PORT = 2233
        
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
                    oldAnswer.append([addr, 0, 0])
                    t = Thread(target=handle_connection, args=(sock, addr, window))
                    t.start()

            except KeyboardInterrupt:
                print("Сервер остановлен!")

            finally:
                stop = True
                serv_sock.close()


if __name__ == '__main__':
    # Проверка на запушенный экземпляр приложения
    lockfile = QLockFile(QDir.tempPath() + '/server_1.lock')

    if lockfile.tryLock(100):
        app = QApplication(sys.argv)
        
        window = mywindow()
        serverThread=ServerThread(window)
        serverThread.start()
        window.show()
        
        sys.exit(app.exec_())
    else:
        print("Сервер 1 уже запущен!")



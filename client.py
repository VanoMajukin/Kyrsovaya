import sys, socket, time
from PyQt5 import QtWidgets
from client_design import Ui_MainWindow  # импорт сгенерированного файла
from threading import Thread, Lock 
from enum import Enum

class UpdatePeriod(Enum):
    OFF = 0
    ONE_MIN = 1
    FIVE_MIN = 5
    FIFETEEN_MIN = 15
    ONE_HOUR = 60

HOST = "localhost"
PORT = [2233, 2234]

BUF_SIZE = 1024
sock = [None, None]
sockStatus = [0, 0]
IS_RECONNECT_ENABLED = False
updateTimer = UpdatePeriod.ONE_MIN.value

mutex = Lock()

class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Обработка нажатий кнопок
        self.ui.sendToServer_1.clicked.connect(self.server_1_Btn_click)
        self.ui.sendToServer_2.clicked.connect(self.server_2_Btn_click)

        # Обработка нажатий меню выбора таймера обновления
        self.ui.action_1.triggered.connect(self.onAction_1_Clicked)
        self.ui.action_2.triggered.connect(self.onAction_2_Clicked)
        self.ui.action_3.triggered.connect(self.onAction_3_Clicked)
        self.ui.action_4.triggered.connect(self.onAction_4_Clicked)
        self.ui.action_5.triggered.connect(self.onAction_5_Clicked)

    # Отправка на сервер 1
    def server_1_Btn_click(self):
        global sock, sockStatus

        print(f"sockStatus[0]: {sockStatus[0]}")

        # получение ширины и высоты окна 
        data = str(self.ui.centralwidget.geometry().width())
        data += 'x' + str(self.ui.centralwidget.geometry().height())
        
        # Добавление заголовка окна
        if(len(self.ui.lineEdit.text()) > 0):
            data += ' | ' + self.ui.lineEdit.text()
            self.ui.lineEdit.clear()

        # Если сервер уже подключен
        if(sockStatus[0] != 0):
            try:
                # Отправка
                sock[0].sendall(data.encode())
                print(data)
                self.ui.listWidget.addItem('Клиент: ' + data)
            
            except OSError:
                data = 'Ошибка! Сервер 1 не подключен!'
                print(data)
                sockStatus[0] = 0
                self.ui.listWidget.addItem('Клиент: ' + data)

        # Если сервер еще не подключен
        else:
            # Пробуем подключиться
            if(check_server(HOST, PORT[0]) == True):
                clientThread = ClientThread(window, 0)
                clientThread.start()

                time.sleep(0.5)
                self.server_1_Btn_click()

            # Если не удалось подключиться
            else:
                data = 'Ошибка! Сервер 1 не подключен!'
                print(data)

                # Вывод в графический интерфейс
                self.ui.listWidget.addItem('Клиент: ' + data)

    # Отправка на сервер 2
    def server_2_Btn_click(self):
        global sockStatus
        data = 'swap'

        # Если сервер уже подключен
        if(sockStatus[1] != 0):
            try:
                # Отправка
                sock[1].sendall(data.encode())
                print(data)
                self.ui.listWidget_2.addItem('Клиент: ' + data)

            except OSError:
                data = 'Ошибка! Сервер 2 не подключен!'
                print(data)
                sockStatus[1] = 0
                self.ui.listWidget_2.addItem('Клиент: ' + data)

        # Если сервер еще не подключен
        else:
            # Пробуем подключиться
            if(check_server(HOST, PORT[1]) == True):
                clientThread = ClientThread(window, 1)
                clientThread.start()

                time.sleep(0.5)
                self.server_2_Btn_click()

            # Если не удалось подключиться
            else:
                data = 'Ошибка! Сервер 2 не подключен!'
                print(data)

                # Вывод в графический интерфейс
                self.ui.listWidget_2.addItem('Клиент: ' + data)

    # Вывод текста в графический интерфейс
    def addItem(self, serverType, data):
        if(serverType == 0):
            self.ui.listWidget.addItem('Сервер: ' + data)
        else:
            self.ui.listWidget_2.addItem('Сервер: ' + data)

        print(data)

    # Выключить таймер обновления
    def onAction_1_Clicked(self):
        global updateTimer
        updateTimer = UpdatePeriod.OFF
        print(f"Таймер обнавления: {updateTimer.name}")

    # Установить таймер обновления на 1 мин. 
    def onAction_2_Clicked(self):
        global updateTimer
        updateTimer = UpdatePeriod.ONE_MIN
        print(f"Таймер обнавления: {updateTimer.name}")

    # Установить таймер обновления на 5 мин. 
    def onAction_3_Clicked(self):
        global updateTimer
        updateTimer = UpdatePeriod.FIVE_MIN
        print(f"Таймер обнавления: {updateTimer.name}")

    # Установить таймер обновления на 15 мин. 
    def onAction_4_Clicked(self):
        global updateTimer
        updateTimer = UpdatePeriod.FIFETEEN_MIN
        print(f"Таймер обнавления: {updateTimer.name}")

    # Установить таймер обновления на 1 ч. 
    def onAction_5_Clicked(self):
        global updateTimer
        updateTimer = UpdatePeriod.ONE_HOUR
        print(f"Таймер обнавления: {updateTimer.name}")

class ClientThread(Thread):
    def __init__(self, window, serverType): 
        Thread.__init__(self) 
        self.window = window
        self.serverType = serverType
        
    def run(self): 
        global HOST, PORT, sock, sockStatus
        is_started = False

        while IS_RECONNECT_ENABLED or not is_started:
            is_started = True
            print("\nКлиент создан")

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock[self.serverType]:
                sock[self.serverType].connect((HOST, PORT[self.serverType]))
                sockStatus[self.serverType] = 1
                print(f"Сервер {self.serverType + 1} подключен")
                
                try:
                    self.receiveFunc()

                except KeyboardInterrupt:
                    print(f"Сервер {self.serverType + 1} отключен")
                
                finally:
                    sock[self.serverType].close()

    def receiveFunc(self):
        global sock

        while True:
            # Получение ответа от сервера
            data_bytes = sock[self.serverType].recv(BUF_SIZE)
            data = data_bytes.decode()
            
            if not data:
                print("Сервер закрыл соединение")
                break

            if(data.find(" | ") != -1):
                data = data.split(" | ")
                self.window.addItem(self.serverType, data[0])
                self.window.addItem(self.serverType, data[1])
            else:
                self.window.addItem(self.serverType, data)

def checkUpdateTimer():
    global updateTimer, sockStatus, window

    while True:
        if(updateTimer != UpdatePeriod.OFF.value):
            if(sockStatus[0] == 1):
                window.server_1_Btn_click()
            
            if(sockStatus[1] == 1):
                window.server_2_Btn_click()
            
            time.sleep(updateTimer * 60)

def check_server(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()

if __name__ == "__main__":   
    app = QtWidgets.QApplication(sys.argv)
    window = mywindow()

    if(check_server(HOST, PORT[0]) == True):
        clientThread = ClientThread(window, 0)
        clientThread.start()

    if(check_server(HOST, PORT[1]) == True):
        clientThread = ClientThread(window, 1)
        clientThread.start()
    
    time.sleep(0.5)
    t = Thread(target= checkUpdateTimer)  # New
    t.start()

    window.show()
    sys.exit(app.exec_())
    

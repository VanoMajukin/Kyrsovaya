import sys, socket, time
from PyQt5 import QtWidgets
from client_design import Ui_MainWindow  # импорт сгенерированного файла
from threading import Thread 
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
updateTimer = UpdatePeriod.OFF.value

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
        global sock

        if(sockStatus[0] != 0):
            # получение ширины и высоты окна 
            data = str(self.ui.centralwidget.geometry().width())
            data += 'x' + str(self.ui.centralwidget.geometry().height())
            
            # Добавление заголовка окна
            if(len(self.ui.lineEdit.text()) > 0):
                data += ' | ' + self.ui.lineEdit.text()
                self.ui.lineEdit.clear()

            # Отправка
            sock[0].sendall(data.encode())

            # Вывод в графический интерфейс
            self.ui.listWidget.addItem('Клиент: ' + data)
        else:
            data = 'Ошибка! Сервер не подключен!'
            self.ui.listWidget.addItem('Клиент: ' + data)
            print(data)

    # Отправка на сервер 2
    def server_2_Btn_click(self):
        global sock

        if(sockStatus[1] != 0):
            data = 'swap'

            # Отправка
            sock[1].sendall(data.encode())

            # Вывод в графический интерфейс
            self.ui.listWidget_2.addItem('Клиент: ' + data)
        else:
            data = 'Ошибка! Сервер не подключен!'
            self.ui.listWidget_2.addItem('Клиент: ' + data)
            print(data)

    # Вывод текста в графический интерфейс
    def addItem(self, serverType, data):
        if(serverType == 0):
            self.ui.listWidget.addItem('Сервер: ' + data)
        else:
            self.ui.listWidget_2.addItem('Сервер: ' + data)


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
        global HOST, PORT
        is_started = False

        while IS_RECONNECT_ENABLED or not is_started:
            is_started = True
            print("\nCreate client")

            global sock, sockStatus
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock[self.serverType]:
                sock[self.serverType].connect((HOST, PORT[self.serverType]))
                sockStatus[self.serverType] = 1
                print(f"Server {self.serverType + 1} connected")
                
                try:
                    self.receiveFunc()

                except KeyboardInterrupt:
                    print(f"Server {self.serverType + 1} disconnected")
                
                finally:
                    sock[self.serverType].close()

    def receiveFunc(self):
        while True:
            # Получение ответа от сервера
            data_bytes = sock[self.serverType].recv(BUF_SIZE)
            data = data_bytes.decode()
            print("Received: ", repr(data))
            
            if not data:
                print("Closed by server")
                break

            if(data.find(" | ") != -1):
                data = data.split(" | ")
                self.window.addItem(self.serverType, data[0])
                self.window.addItem(self.serverType, data[1])
            else:
                self.window.addItem(self.serverType, data)

def checkUpdateTimer(window):
    global updateTimer

    while True:
        if(updateTimer.name != UpdatePeriod.OFF.name):
            window.server_1_Btn_click()
            window.server_2_Btn_click()
            time.sleep(updateTimer.value)

if __name__ == "__main__":   
    app = QtWidgets.QApplication(sys.argv)
    window = mywindow()

    clientThread = ClientThread(window, 0)
    clientThread.start()

    clientThread = ClientThread(window, 1)
    clientThread.start()
    
    # t = Thread(target= checkUpdateTimer, args= (window))  # New
    # t.start()

    window.show()
    sys.exit(app.exec_())
    

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

sock = None
sockStatus = 0
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

        if(sockStatus != 0):
            # получение ширины и высоты окна 
            data = str(self.ui.centralwidget.geometry().width())
            data += 'x' + str(self.ui.centralwidget.geometry().height())
            
            # Добавление заголовка окна
            if(len(self.ui.lineEdit.text()) > 0):
                data += ' | ' + self.ui.lineEdit.text()
                self.ui.lineEdit.clear()

            # Отправка
            sock.sendall(data.encode())

            # Вывод в графический интерфейс
            self.ui.listWidget.addItem('Клиент: ' + data)
        else:
            data = 'Ошибка! Сервер не подключен!'
            self.ui.listWidget.addItem('Клиент: ' + data)
            print(data)

    # Отправка на сервер 2
    def server_2_Btn_click(self):
        global sock

        if(sockStatus != 0):
            data = 'swap'

            # Отправка
            sock.sendall(data.encode())

            # Вывод в графический интерфейс
            self.ui.listWidget_2.addItem('Клиент: ' + data)
        else:
            data = 'Ошибка! Сервер не подключен!'
            self.ui.listWidget_2.addItem('Клиент: ' + data)
            print(data)

    # Вывод текста в графический интерфейс
    def addItem(self, data):
        self.ui.listWidget.addItem('Сервер: ' + data)

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
    def __init__(self, window): 
        Thread.__init__(self) 
        self.window = window
 
    def run(self): 
        HOST = "localhost"
        PORT = 2233
        
        is_started = False

        while IS_RECONNECT_ENABLED or not is_started:
            is_started = True
            print("\nCreate client")

            global sock, sockStatus
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((HOST, PORT))
                sockStatus = 1
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

    clientThread = ClientThread(window)
    clientThread.start()
    
    t = Thread(target= checkUpdateTimer, args= (window))  # New
    t.start()

    window.show()
    sys.exit(app.exec_())
    

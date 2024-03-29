#!/usr/bin/env python3
import sys, socket, time
from PyQt5 import QtWidgets
from client_design import Ui_MainWindow  # импорт сгенерированного файла
from threading import Thread, Lock 
from enum import Enum
import GPUtil

def get_gpu_info() :
    try:
        # Получение списка доступных устройств GPU
        gpus = GPUtil.getGPUs()

        gpu_info = []
        for gpu in gpus:
            gpu_info.append({
                'ID': gpu.id,
                'Name': gpu.name,
                'Driver': gpu.driver,
                'Memory Total': f"{gpu.memoryTotal} MB",
                'Memory Used': f"{gpu.memoryUsed} MB",
                'Memory Free': f"{gpu.memoryFree} MB"
            })

        return gpu_info

    except Exception as e:
        print(f"Ошибка при получении информации о GPU: {e}")
        return None



class UpdatePeriod(Enum):
    OFF = 0
    ONE_MIN = 1
    FIVE_MIN = 5
    FIFETEEN_MIN = 15
    ONE_HOUR = 60
    
HOST = "192.168.1.7"
PORT = [2233, 2234]

BUF_SIZE = 1024                             # Размер буфера для получения сообшения
sock = [None, None]                         # Сокеты 
sockStatus = [0, 0]                         # Статусы подключения к серверам
IS_RECONNECT_ENABLED = False                # Флаг для переподключения при падении клиента
updateTimer = UpdatePeriod.OFF.value        # Таймер обновления информации

class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Обработка нажатий кнопок
        self.ui.sendToServer_1.clicked.connect(self.server_1_Btn_click)
        self.ui.sendToServer_2.clicked.connect(self.server_2_Btn_click)
        self.ui.sendToServer_3.clicked.connect(self.server_3_Btn_click)
        self.ui.sendToServer_4.clicked.connect(self.server_4_Btn_click)
        # Обработка нажатий меню выбора таймера обновления
        self.ui.action_1.triggered.connect(self.onAction_1_Clicked)
        self.ui.action_2.triggered.connect(self.onAction_2_Clicked)
        self.ui.action_3.triggered.connect(self.onAction_3_Clicked)
        self.ui.action_4.triggered.connect(self.onAction_4_Clicked)
        self.ui.action_5.triggered.connect(self.onAction_5_Clicked)
        self.ui.combo_box.currentIndexChanged.connect(self.on_combobox_changed)
    # Отправка на сервер 1
    def server_1_Btn_click(self):
        global sock, sockStatus

        data = "GPU: "
         # Получение информации о видеоадаптере
        gpu_info = get_gpu_info()
        if gpu_info:
            for gpu in gpu_info:
                data += gpu['Name'] + ";"

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

    def server_3_Btn_click(self):
            global sock, sockStatus

            # получение ширины и высоты окна 
            data = str(self.ui.listWidget.geometry().width())
            data += 'x' + str(self.ui.listWidget.geometry().height())

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
                    self.server_3_Btn_click()

                # Если не удалось подключиться
                else:
                    data = 'Ошибка! Сервер 1 не подключен!'
                    print(data)

                    # Вывод в графический интерфейс
                    self.ui.listWidget.addItem('Клиент: ' + data)
    # Отправка на сервер 2
    
    def server_2_Btn_click(self):
        global sockStatus
        data = 'swap_free'

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

    # свободная память
    def server_4_Btn_click(self):
       
        global sockStatus
        data = self.on_combobox_changed()

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
                self.server_4_Btn_click()

            # Если не удалось подключиться
            else:
                data = 'Ошибка! Сервер 2 не подключен!'
                print(data)

                # Вывод в графический интерфейс
                self.ui.listWidget_2.addItem('Клиент: ' + data)

    def on_combobox_changed(self):
        # Этот метод вызывается при изменении выбранного элемента в QComboBox
        selected_text = self.ui.combo_box.currentText()
        return selected_text
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
        updateTimer = UpdatePeriod.OFF.value

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
            self.window.addItem(self.serverType, data)        

# Проверка автообновления
def checkUpdateTimer():
    global updateTimer, sockStatus, window

    while True:

        if(updateTimer != UpdatePeriod.OFF.value):
            
            if(sockStatus[0] == 1):
                window.server_1_Btn_click()
            
            if(sockStatus[1] == 1):
                window.server_2_Btn_click()
            
            time.sleep(updateTimer.value * 60)

# Проверка доступности сервера
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

    # Подключение к серверу 1
    if(check_server(HOST, PORT[0]) == True):
        clientThread = ClientThread(window, 0)
        clientThread.start()

    # Подключение к серверу 2
    if(check_server(HOST, PORT[1]) == True):
        clientThread = ClientThread(window, 1)
        clientThread.start()
    
    # Отправка периодических запросов к серверу
    time.sleep(0.5)
    t = Thread(target= checkUpdateTimer)
    t.start()

    window.show()
    sys.exit(app.exec_())
    

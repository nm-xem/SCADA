import  socket, time, os, sys, threading
from json import loads as j_loads
from json import dumps as j_dumps
from pickle import loads as p_loads
from pickle import dumps as p_dumps

current_dir = "connect"
main_dir = os.path.dirname(os.path.abspath(__file__))[:-(len(current_dir)+1)]
sys.path.append(f"{main_dir}")

from secondary_functions import protocol_functions as pf

"""
    Возможна отправка неограниченного количества запросов на получение данных
        результат выполнения - словарь с названием системы и словарём данных 
    Возможна отправка ОДНОГО пакета данных dict_data_send по коду code_send
"""
class Connect_gateway ():
    def __init__ (self):
        """
            Конфигурационные переменные
                name_module - название модуля
                ip_gateway - IP Шлюза по умолчанию
                port_gateway - порт Шлюза по умолчанию
                dict_codes_get - словарь названий систем и кодов запросов на получение данных
                code_send - код на отправку данных
                dict_data_get - словарь названий систем и принятых данных
                dict_data_send - словарь названий систем и данных на отправку
                threads_stop - флаг остановки потоков
        """
        self.name_module = 'Connect_gateway'
        self.ip_gateway = '172.16.4.150'
        self.port_gateway = 9002
        self.dict_codes_get = {}
        self.code_send = ''
        self.dict_data_get = {}
        self.dict_data_send = {}
        self.threads_stop = False

    def run (self):
        try:
            threading.Thread (target=self.send_data_to_gateway, daemon=True).start()
            threading.Thread (target=self.get_data_from_gateway, daemon=True).start()
        except:
            self.threads_stop = True
            pf.write_file_log(self.name_module,f'Не удалось запустить основные потоки')
        else:
            pf.write_file_log(self.name_module,f'Все основные потоки запущены')

    # Функция подключения к Шлюзу
    def connect_to_gateway (self):
        try:
            sockToServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            sockToServer.settimeout(5)
            sockToServer.connect((self.ip_gateway, self.port_gateway))
        except:
            print ('Не удалось подключиться к Шлюзу.')
            return 'error'
        else:
            return sockToServer
        
    # Функция отправки пакета на Шлюз
    def send_data_to_gateway (self):
        while True:
            sockToServer = self.connect_to_gateway()
            if sockToServer == 'error':
                time.sleep(0.5)
                continue
            else:
                try:
                    sockToServer.send(p_dumps(j_dumps([
                        '700', self.dict_data_send])))
                    sockToServer.close()
                except:
                    print ('Не удалось отправить данные на Шлюз.')
                    time.sleep(0.5)
                    continue
            time.sleep(1)

    # Функция запроса данных от Шлюза
    """
        Результат выполнения:
            словарь dict_data_get
    """
    def get_data_from_gateway (self):
        while True:
            sockToServer = self.connect_to_gateway()
            if sockToServer == 'error':
                time.sleep(0.5)
                continue
            else:
                try:
                    for name_sistem, code in self.dict_codes_get.items():
                        code_b = bytes(code, 'utf-8')
                        sockToServer.sendall(code_b)
                        self.dict_data_get[name_sistem] = self.get_data(sockToServer)
                    sockToServer.close()
                except:
                    print ('Не удалось отправить запрос на Шлюз для получения данных.')
                    time.sleep(0.5)
                    continue
            time.sleep(1)

    # Функция обработки получаемого пакета
    def get_data (sock):
        result = b''
        while True:
            mes = sock.recv(4098)
            if not mes:
                break
            result += mes
        return j_loads(p_loads(result))
    



            

import os, sys, time, threading, socket
from json import loads as j_loads
from json import dumps as j_dumps
from pickle import loads as p_loads
from pickle import dumps as p_dumps

current_dir = "gateway"
main_dir = os.path.dirname(os.path.abspath(__file__))[:-(len(current_dir)+1)]
sys.path.append(f"{main_dir}")

from secondary_functions import protocol_functions as pf

class Gateway ():
    def __init__(self):
        self.name_module = 'gateway'
        # self.ip = '172.16.4.150'
        self.ip = '127.0.0.0'
        self.port = 9002
        self.simbols = [str(i) for i in range(10)]
        self.path_file_id_parameters = f'{main_dir}/{current_dir}/id_parameters.txt'
        self.time_mod_file_id_parameters = 0
        self.dict_id_parameters = {
            'analog' : {},
            'discrete' : {},
            'olse_code' : {},
        }
        self.list_reference_status_bar = [
                {
                    '0' : "607",
                    '1' : "603",
                    '2' : "604",
                    '9' : "4076",
                    '13': "20",
                    '17': "900016",
                    '18': "900017",
                    '25': "813",
                    '26': "814",
                    '27': "815",
                    '28': "816",
                    '41': "199999",
                    '42': "605",
                    '43': "606",
                    '46': "22",
                },
                {
                    '3' : "603",
                    '4' : "604",
                    '10': "4076",
                    '14': "20",
                    '19': "900016",
                    '20': "900017",
                    '29': "813",
                    '30': "814",
                    '31': "815",
                    '32': "816",
                    '41': "199999",
                    '44': "605",
                    '45': "606",
                    '47': "22",
                },
                {
                    '5' : "8",
                    '6' : "34",
                    '11': "900114",
                    '15': "900001",
                    '21': "900016",
                    '22': "900017",
                    '33': "675",
                    '34': "676",
                    '35': "677",
                    '36': "678",
                    '41': "199999",
                    '48': "1471",
                },
                {
                    '7' : "0",
                    '8' : "14",
                    '12': "8263",
                    '16': "1163",
                    '23': "900016",
                    '24': "900017",
                    '37': "471",
                    '38': "472",
                    '39': "473",
                    '40': "474",
                    '41': "199999",
                    '49': "1164",
                }
            ]
        self.codes_get_data = ['511', '521', '531', '541', '911', '921', '931', '941', '700']
        """
            Структура data_sistems:
                {
                    analog_signals :    [
                                            { словарь аналоговых сигналов 1 блока },
                                            { словарь аналоговых сигналов 2 блока },
                                            { словарь аналоговых сигналов 3 блока },
                                            { словарь аналоговых сигналов 4 блока },
                                        ],
                    discrete_signals :  [
                                            { словарь дискретных сигналов 1 блока },
                                            { словарь дискретных сигналов 2 блока },
                                            { словарь дискретных сигналов 3 блока },
                                            { словарь дискретных сигналов 4 блока },
                                        ],
                        field :         [
                                            { словарь сигналов поля 1 блока },
                                            { словарь сигналов поля 2 блока },
                                            { словарь сигналов поля 3 блока },
                                            { словарь сигналов поля 4 блока },
                                        ],
                    status_bar :        { словарь данных статус-бара },
                    simple_diagnostic : { словарь упрощённой диагностики },
                    full_diagnostic :   {
                                            ""
                                        }


                    
        """
        self.data_sistems = {
            'analog_signals' : [
                {},
                {},
                {},
                {},
            ],
            'discrete_signals' : [
                {},
                {},
                {},
                {},
            ],
            'field' : [
                {},
                {},
                {},
                {},
            ],
            'status_bar' : {},
            'simple_diagnostic' : '',
            'full_diagnostic' : {},
            'time_in_packages' : {}
        }
        self.time_get_packages_from_sistems = {}

        threading.Thread(target=self.check_udate_id_parameters, daemon=True).start()
        self.start_gateway_socket ()


    def accept_cients (self):
        # Функция обработки получаемого пакета
        def get_data (sock):
            result = b''
            while True:
                mes = sock.recv(4098)
                if not mes:
                    break
                result += mes
            if (len(mes) < 10):
                # Нужно ли?
                return result.decode()
            else:
                return j_loads(p_loads(result))
            
        while True:
            try:
                client, addr = self.gateway_socket.accept()
            except:
                pf.write_file_log(self.name_module,f'Клиент не смог подключиться')
                continue
            else:
                result = get_data (client)
                # Запрос данных
                if len(result) < 10:
                    request = result
                    self.sanding_date_by_request (client, request)
                # Приём данных
                else:
                    self.parsing_requests (result)
                client.close()

    # Функция обновления данных статус-бара
    def update_data_status_bar (self):
        while True:
            for num_block in range(4):
                for num_signal_status_bar, num_reference in self.list_reference_status_bar[num_block].items():
                    try:
                        self.data_sistems['status_bar'][num_signal_status_bar] = self.data_sistems['analog_signals'][num_block][num_reference]
                    except:
                        self.data_sistems['status_bar'][num_signal_status_bar] = 0
            time.sleep(1)
                
    # Функция обновления упрощённой диагностики
    def update_simple_diagnostic (self):
        while True:
            time_now = time.time()
            for name_sistem, time_sistem in self.time_get_packages_from_sistems.items():
                if (time_now - time_sistem) < 5:
                    self.data_sistems['simple_diagnostic'][name_sistem] = '0'
                elif (time_now - time_sistem) < 10:
                    self.data_sistems['simple_diagnostic'][name_sistem] = '1'
                else:
                    self.data_sistems['simple_diagnostic'][name_sistem] = '2'
            time.sleep(1)

    # Функция обработки получаемых данных
    def parsing_requests (self, result):
        try:
            code = result[0]
        except:
            pf.write_file_log(self.name_module,f'Ошибка обработки кода приёма данных')
        else:
            """
                Состав пакета:
                    словарь:
                        название системы        : строка
                        аналоговые сигналы      : словарь
                        дискретные сигналы      : словарь
                        специальные данные      : словарь
                        диагностические данные  : словарь
                    
            """
            try:
                if code in self.codes_get_data:
                    name_sistem = result[1]['name_sistem']
                    self.data_sistems['analog_signals'][code[1]-1] = {**self.data_sistems['analog_signals'][code[1]-1], **result[1]['analog_data']}
                    self.data_sistems['discrete_signals'][code[1]-1] = {**self.data_sistems['discrete_signals'][code[1]-1], **result[1]['discrete_data']}
                    self.data_sistems['full_diagnostic'][name_sistem] = {**self.data_sistems['full_diagnostic'][name_sistem],**result[1]['diagnostic']}
                    self.data_sistems['time_in_packages'][name_sistem] = result[1]['diagnostic']['time']
                    self.time_get_packages_from_sistems[name_sistem] = time.time()
                    if code[0] == '9':
                        self.data_sistems['field'][code[1]-1] = {**self.data_sistems['field'][code[1]-1], **result[1]['field']}
                else:
                    pf.write_file_log(self.name_module,f'Запрос приёма данных по незарегистрированному коду "{code}"')
            except:
                pf.write_file_log(self.name_module,f'Ошибка обработки данных по коду "{code}"')

    # Функция отправки данных по коду запроса
    def sanding_date_by_request (self, client, request):
        # Функци подготовки данных по коду запроса
        def preparation_response (list_id_parameters, data):
            response = {}
            for id in list_id_parameters:
                try:
                    response[id] = data[id]
                except:
                    pf.write_file_log(self.name_module,f'Отсутствует параметр "{id}"')
            return response
        try:
            if request[0] == '1' and (request in self.dict_id_parameters['analog'].keys() or request in self.dict_id_parameters['discrete'].keys()):
                # Запрос аналоговых сигналов
                if request[2] == '1':
                    response = preparation_response (self.dict_id_parameters['analog'][request], self.data_sistems['analog_signals'][int(request[1]-1)])
                    client.sendall (p_dumps(j_dumps(response)))
                # Запрос дискретных сигналов
                elif request[2] == '2':
                    response = preparation_response (self.dict_id_parameters['discrete'][request], self.data_sistems['discrete_signals'][int(request[1]-1)])
                    client.sendall (p_dumps(j_dumps(response)))
            # Запрос данных поля
            elif request[0] == '9':
                # Отправка данных поля
                client.sendall (p_dumps(j_dumps(self.data_sistems['field'][int(request[1]-1)])))
            # Прочие запросы данных
            elif request[0] == '7' and request in self.dict_id_parameters['olse_code'].keys():
                response = preparation_response (self.dict_id_parameters['olse_code'][request], self.data_sistems['analog_signals'][int(request[1]-1)])
                client.sendall (p_dumps(j_dumps(response)))
            # Запрос данных статус-бара
            elif request == '0000':
                client.sendall (p_dumps(j_dumps(self.data_sistems['status_bar'])))
            # Запрос данных времени в пакетах
            elif request == '4444':
                client.sendall (p_dumps(j_dumps(self.data_sistems['time_in_packages'])))
            # Запрос данных упрощённой диагностики
            elif request == '5555':
                client.sendall (p_dumps(j_dumps(self.data_sistems['simple_diagnostic'])))
            # Запрос данных полной диагностики
            elif request == 'dddd':
                client.sendall (p_dumps(j_dumps(self.data_sistems['full_diagnostic'])))
            else:
                pf.write_file_log(self.name_module,f'Запрос отправки данных по незарегистрированному коду "{request}"')
        except:
            pf.write_file_log(self.name_module,f'Ошибка обработки кода отправки данных')

    # Функция запуска сервера
    def start_gateway_socket (self):
        pf.write_file_log(self.name_module,f'Запуск сервера')
        try:
            self.gateway_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.gateway_socket.bind ((self.ip, self.port))
        except:
            pf.write_file_log(self.name_module,f'Не удалось запустить сервер')
        else:
            pf.write_file_log(self.name_module,f'Сервер запущен')
            self.gateway_socket.listen(20)
  
    # Функция проверки обновления списка параметров
    def check_udate_id_parameters (self):
        while True:
            if self.time_mod_file_id_parameters != round(os.path.getmtime(self.path_file_id_parameters)):
                self.time_mod_file_id_parameters = round(os.path.getmtime(self.path_file_id_parameters))
                pf.write_file_log(self.name_module,f'Создание списков id параметров')
                self.creat_dict_id_parameters ()
                pf.write_file_log(self.name_module,f'Списки id параметров созданы')
            time.sleep(2)

    # Функция создания словаря id параметров
    """
        Все коды и id являются строками
    """
    def creat_dict_id_parameters(self):
        # Функция сортировки кодов
        def sort_codes (code, ids):
            if code[0] == '1':
                if  code[2] == '1':
                    self.dict_id_parameters['analog'][code] = ids
                if  code[2] == '2':
                    self.dict_id_parameters['discrete'][code] = ids
            else:
                self.dict_id_parameters['olse_code'][code] = ids

        # Функция, разбирающая строку с id
        def string_parssing_ids (line):
            id = ''
            id_range_1 = ''
            id_range_2 = ''
            ids = []
            for ch in line:
                if ch == ':':
                    id_range_1 = id
                    id = ''

                if ch in self.simbols:
                    id += ch
                if ch == ',' or ch == '\n':
                    if id_range_1:
                        id_range_2 = id
                        for i in range(int(id_range_1),int(id_range_2)+1):
                            ids.append(str(i))
                        id_range_1 = ''
                        id_range_2 = ''
                    else:
                        ids.append(id)
                    id = ''
            return ids
            
        with open(f'{main_dir}/{current_dir}/id_parameters.txt', 'r', encoding = 'utf-8') as file_id_parameters:
            for line in file_id_parameters:
                if (line[0] == "*") or (line[0] == "#") or len(line) <= 1:
                    continue
                else:
                    if len(line) <= 6:
                        code = line[:6].rstrip('\n')
                    else:
                        ids = string_parssing_ids (line)
                        sort_codes (code, ids)
            for name_sistem, sistem in self.dict_id_parameters.items():
                print(name_sistem)
                for code, idue in sistem.items():
                    print(code)
                    print(idue)
        
Gateway ()
while True:
    time.sleep(10)
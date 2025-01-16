import  socket, time
from json import loads as j_loads
from pickle import loads as p_loads

class Connect_gateway ():
    def __init__ (self):
        self.ip_gateway = '172.16.4.150'
        self.port_gateway = 9002
        self.dict_codes_get = {
            'IVS_1_analog' : '7000', 
            'IVS_2_analog' : '7001'}
        self.dict_data_get = {}
        

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
        
    def get_data_from_gateway (self):
        while True:
            sockToServer = self.connect_to_gateway()
            if sockToServer == 'error':
                time.sleep(0.5)
            else:
                for name_sistem, code in self.dict_codes_get.items():
                    code_b = bytes(code, 'utf-8')
                    sockToServer.sendall(code_b)
                    data = self.get_data(sockToServer)
                    self.dict_data_get[name_sistem] = j_loads(p_loads(data))
                sockToServer.close()
                time.sleep(1)

    def get_data (sock):
        result = b''
        while True:
            mes = sock.recv(4098)
            if not mes:
                break
            result += mes
        return result

            

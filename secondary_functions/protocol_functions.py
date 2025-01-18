import time, os

def get_time_mes ():
    return time.strftime("%y.%m.%d %H:%M:%S"), time.strftime("%y_%m_%d")

def write_file_log (name_sistem, mes):
    dir = os.path.dirname(os.path.abspath(__file__))[:-20]
    if not os.path.isdir(f"{dir}/logs"):
        os.makedirs(f'{dir}/logs', exist_ok=True)

    time_mes, date = get_time_mes()
    try:
        with open(f'{dir}/logs/{date}_{name_sistem}.txt', 'a', encoding = 'utf-8') as file_log:
            
            file_log.write(f'{time_mes}\t{mes}.\n')
    except:
        print (f'Не удалось сделать запись в файл /logs/{date}_{name_sistem}.txt')

import list_modules as module_lm
from calculation import Calculation
import time, threading, os, importlib, sys

current_dir = "calc"
main_dir = os.path.dirname(os.path.abspath(__file__))[:-(len(current_dir)+1)]
sys.path.append(f"{main_dir}")

from secondary_functions import protocol_functions as pf

# Функция проверки необходимости обновления списка модулей
def check_update_list_modules ():
    while True:
        try:
            time_update_list_modules = os.path.getmtime(f'{main_dir}/{current_dir}/list_modules.py')
        except:
            pf.write_file_log(name_module,'Модуль "list_modules.py" был удалён')
        else:
            if time_update_list_modules > time_import_list_modules or dict_modules == 'error':
                update_list_modules(time_update_list_modules)
        time.sleep(2) 

# Функция обновления списка модулей
def update_list_modules (time_update_list_modules):
    global time_import_list_modules, dict_modules
    importlib.reload(module_lm)
    temp_list_modules = module_lm.create_dict_modules()
    if temp_list_modules == 'error':
        pf.write_file_log(name_module,'Ошибка обновления списка расчётных модулей')
    else:
        time_import_list_modules = time_update_list_modules
        run_new_modules (temp_list_modules)
        stop_removed_modules (temp_list_modules)
        dict_modules = temp_list_modules
        pf.write_file_log(name_module,'Обновлён список расчётных модулей')

# Функция запуска новых модулей
def run_new_modules (temp_lm):
    for name in temp_lm:
        if not name in dict_modules:
            list_examplу_module.append(Calculation(temp_lm[name]['name_ru'], temp_lm[name]['function'], temp_lm[name]['periodicity'], name, temp_lm[name]['autoupdate']))
            list_examplу_module[-1].run()
            dict_signals[name] = temp_lm[name]['list_signals']
            pf.write_file_log(name_module,f'Добавлен модуль "{name}"')

# Функция остановки удалённых модулей
def stop_removed_modules (temp_list_modules):
    for name in dict_modules:
        if not name in temp_list_modules:
            for item in list_examplу_module:
                if item.name_module == name:
                    item.threads_stop = True
                    list_examplу_module.remove(item)
                    pf.write_file_log(name_module,f'Удалён модуль "{name}"')

# Функция проверки необходимости обновления расчётных модулей
def check_update ():
    while True:
        for item in list_examplу_module:
            if item.need_update:
                name_update = item.name_module
                pf.write_file_log(name_module,f'Расчётная функция модуля "{name_update}" нуждается в обновлении')
                if item.autoupdate:
                    update_calc_modules (item, name_update)
        time.sleep(5)

# Функция обновления расчётных модулей
def update_calc_modules (item, name_update):
    dict_modules = module_lm.update_dict_modules ()
    item.func_module = dict_modules[name_update]['function']
    item.periodicity = dict_modules[name_update]['periodicity']
    item.autoupdate = dict_modules[name_update]['autoupdate']
    item.name_module_ru = dict_modules[name_update]['name_ru']
    dict_signals[name] = dict_modules[name_update]['list_signals']
    item.need_update = False
    if item.global_error_module:
        item.global_error_module = False
        item.is_error = False
    item.time_update_module = os.path.getmtime(f'{main_dir}/{current_dir}/modules/{name_update}.py')
    pf.write_file_log(name_module,f'Расчётная функция модуля "{name_update}" обновлена')

# Функция обновления данных, необходимых для расчёта, в модулях 
def update_data_modules ():
    while True:
        for item in list_examplу_module:
            name = item.name_module
            data = {}
            try:
                for tag in dict_signals[name]:
                    data[tag] = dict_data[tag]
            except:
                pf.write_file_log(name_module,f'Не удалось создать словарь данных для модуля {name}')
            item.data = data
        time.sleep(1)


if __name__ == '__main__':
    """
        Служебные переменные
            name_module - название модуля
            list_examplу_module - список экземпляров модулей расчёта
            dict_signals - словарь тэгов, необходимых для расчёта
            dict_modules - словарь модулей и данных о них из list_modules.py
            time_import_list_modules - время импортирования словаря модулей
            dict_data - словарь данных от систем
    """
    name_module = 'main_module'
    list_examplу_module = []
    dict_signals = {}
    time_import_list_modules = os.path.getmtime(f'{main_dir}/{current_dir}/list_modules.py')
    dict_modules = module_lm.create_dict_modules()
    dict_data = {
    '1' : 101,
    '2' : 102,
    '3' : 103,
    '4' : 104,
    '5' : 105,
    '6' : 106,
    '7' : 107,
    '8' : 108,
    '9' : 109,
    '10' : 110,
}

    """
        Заполнение списка модулей и тэгов и запуск
    """
    for name, module in dict_modules.items():
        list_examplу_module.append(Calculation(module['name_ru'], module['function'], module['periodicity'], name, module['autoupdate']))
        dict_signals[name] = module['list_signals']

    for module in list_examplу_module:
        module.run()

    """
        Запуск потоков проверки необходимости обновления списка модулей, обновления расчётных модулей,
        обновления данных, необходимых для расчёта, в модулях 
    """
    threading.Thread (target=check_update_list_modules, daemon=True).start()
    threading.Thread (target=check_update, daemon=True).start()
    threading.Thread (target=update_data_modules, daemon=True).start()
    

    while True:
        time.sleep(10)
import time, threading, os, importlib, sys
import list_modules as module_lm
from calculation import Calculation

current_dir = "calc"
main_dir = os.path.dirname(os.path.abspath(__file__))[:-(len(current_dir)+1)]
sys.path.append(f"{main_dir}")

from secondary_functions import protocol_functions as pf

class Calculation_modules_manager ():
    def __init__ (self):
        """
            Служебные переменные
                name_module - название модуля
                list_examplу_module - список экземпляров модулей расчёта
                dict_signals - словарь тэгов, необходимых для расчёта
                dict_modules - словарь модулей и данных о них из list_modules.py
                time_import_list_modules - время импортирования словаря модулей
                dict_data - словарь данных от систем
        """
        self.main_dir = main_dir
        self.current_dir = current_dir
        self.time_import_dict_modules = os.path.getmtime(f'{main_dir}/{current_dir}/list_modules.py')
        self.dict_modules = module_lm.create_dict_modules()
        self.name_module = 'Calculation_modules_manager'
        self.list_examplу_module = []
        self.dict_signals = {}
        self.dict_data = {
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

        self.create_list_examplу_module ()

        threading.Thread (target=self.check_update, daemon=True).start()
        threading.Thread (target=self.update_data_modules, daemon=True).start()
        threading.Thread (target=self.check_update_dict_modules, daemon=True).start()

    # Функция заполнения списка модулей и тэгов и запуск
    def create_list_examplу_module (self):
        for name, module in self.dict_modules.items():
            self.list_examplу_module.append(Calculation(module['name_ru'], module['function'], module['periodicity'], name, module['autoupdate']))
            self.dict_signals[name] = module['list_signals']
        
        message = f'Запущены все расчётные модули, кроме:'
        errors_run = False
        for module in self.list_examplу_module:
            try:
                module.run()
            except:
                pf.write_file_log(self.name_module,f'Не удалось запустить модуль {module.name_module}')
                message += f'\n\t{module.name_module}'
                errors_run = True
        if not errors_run:
            message = 'Запущены все расчётные модули'
        pf.write_file_log(self.name_module,message)

    # Функция проверки необходимости обновления списка модулей
    def check_update_dict_modules (self):
        print("Запущен модуль")
        while True:
            try:
                time_update_dict_modules = os.path.getmtime(f'{main_dir}/{current_dir}/list_modules.py')
            except:
                pf.write_file_log(self.name_module,'Модуль "list_modules.py" был удалён')
            else:
                if time_update_dict_modules > self.time_import_dict_modules or self.dict_modules == 'error':
                    self.update_list_modules(time_update_dict_modules)
            time.sleep(2) 

    # Функция обновления списка модулей
    def update_list_modules (self, time_update_dict_modules):
        importlib.reload(module_lm)
        temp_list_modules = module_lm.create_dict_modules()
        if temp_list_modules == 'error':
            pf.write_file_log(self.name_module,'Ошибка обновления списка расчётных модулей')
        else:
            self.time_import_dict_modules = time_update_dict_modules
            self.run_new_modules (temp_list_modules)
            self.stop_removed_modules (temp_list_modules)
            self.dict_modules = temp_list_modules
            pf.write_file_log(self.name_module,'Обновлён список расчётных модулей')

    # Функция запуска новых модулей
    def run_new_modules (self, temp_lm):
        for name in temp_lm:
            if not name in self.dict_modules:
                self.list_examplу_module.append(Calculation(temp_lm[name]['name_ru'], temp_lm[name]['function'], temp_lm[name]['periodicity'], name, temp_lm[name]['autoupdate']))
                self.list_examplу_module[-1].run()
                self.dict_signals[name] = temp_lm[name]['list_signals']
                pf.write_file_log(self.name_module,f'Добавлен модуль "{name}"')

    # Функция остановки удалённых модулей
    def stop_removed_modules (self, temp_list_modules):
        for name in self.dict_modules:
            if not name in temp_list_modules:
                for item in self.list_examplу_module:
                    if item.name_module == name:
                        item.threads_stop = True
                        self.list_examplу_module.remove(item)
                        pf.write_file_log(self.name_module,f'Удалён модуль "{name}"')

    # Функция проверки необходимости обновления расчётных модулей
    def check_update (self):
        while True:
            for item in self.list_examplу_module:
                if item.need_update:
                    name_update = item.name_module
                    pf.write_file_log(self.name_module,f'Расчётная функция модуля "{name_update}" нуждается в обновлении')
                    if item.autoupdate:
                        self.update_calc_modules (item, name_update)
            time.sleep(5)

    # Функция обновления расчётных модулей
    def update_calc_modules (self, item, name_update):
        self.dict_modules = module_lm.update_dict_modules ()
        item.func_module = self.dict_modules[name_update]['function']
        item.periodicity = self.dict_modules[name_update]['periodicity']
        item.autoupdate = self.dict_modules[name_update]['autoupdate']
        item.name_module_ru = self.dict_modules[name_update]['name_ru']
        self.dict_signals[name_update] = self.dict_modules[name_update]['list_signals']
        item.need_update = False
        if item.global_error_module:
            item.global_error_module = False
            item.is_error = False
        item.time_update_module = os.path.getmtime(f'{main_dir}/{current_dir}/modules/{name_update}.py')
        pf.write_file_log(self.name_module,f'Расчётная функция модуля "{name_update}" обновлена')

    # Функция обновления данных, необходимых для расчёта, в модулях 
    def update_data_modules (self):
        while True:
            for item in self.list_examplу_module:
                name = item.name_module
                data = {}
                try:
                    for tag in self.dict_signals[name]:
                        data[tag] = self.dict_data[tag]
                except:
                    pf.write_file_log(self.name_module,f'Не удалось создать словарь данных для модуля {name}')
                item.data = data
            time.sleep(1)
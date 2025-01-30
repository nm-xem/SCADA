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
                main_dir - домашняя директория
                current_dir - текущая директория
                time_import_dict_modules - время импортирования словаря модулей
                dict_modules - словарь модулей и данных о них из list_modules.py
                name_module - название модуля
                list_examplу_module - список экземпляров модулей расчёта
                dict_signals - словарь тэгов, необходимых для расчёта
                dict_data - словарь данных от систем
                threads_stop - флаг остановки потоков
        """
        self.main_dir = main_dir
        self.current_dir = current_dir
        self.time_import_dict_modules = os.path.getmtime(f'{main_dir}/{current_dir}/list_modules.py')
        self.dict_modules = module_lm.create_dict_modules()
        self.name_module = 'Calculation_modules_manager'
        self.list_examplу_module = []
        self.dict_signals = {}
        self.dict_data = {}
        self.threads_stop = False
        self.create_list_examplу_module ()
        self.dict_status_daemons = {}
        self.times_daemons = {'check_update' : 0,
                              'update_data_modules' : 0,
                              'check_update_dict_modules' : 0,
                              'diagnostic_threads' : 0}
        self.list_daemons = [threading.Thread (target=self.check_update, daemon=True, name='check_update'),
                             threading.Thread (target=self.update_data_modules, daemon=True, name='update_data_modules'),
                             threading.Thread (target=self.check_update_dict_modules, daemon=True, name='check_update_dict_modules'),
                             threading.Thread (target=self.diagnostic_threads, daemon=True, name='diagnostic_threads')]

    def run (self):
        try:
            for daemon in self.list_daemons:
                if not daemon.is_alive():
                    daemon.start()
        except:
            self.threads_stop = True
            pf.write_file_log(self.name_module,f'Не удалось запустить основные потоки')
        else:
            pf.write_file_log(self.name_module,f'Все основные потоки запущены')

    # Функция заполнения списка модулей и тэгов и запуск
    def create_list_examplу_module (self):
        for name, module in self.dict_modules.items():
            self.list_examplу_module.append(Calculation(module['function'], module['periodicity'], name, module['autoupdate']))
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
        pf.write_file_log(self.name_module,f'Запущен модуль"check_update_dict_modules"')
        while True:
            self.times_daemons['check_update_dict_modules'] = round(time.time())
            self.time_in_check_update_dict_modules = time.time()
            if self.threads_stop:
                pf.write_file_log(self.name_module, f'Поток "check_update_dict_modules" завершён')
                break
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
                self.list_examplу_module.append(Calculation(temp_lm[name]['function'], temp_lm[name]['periodicity'], name, temp_lm[name]['autoupdate']))
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
        pf.write_file_log(self.name_module,f'Запущен модуль"check_update"')
        while True:
            self.times_daemons['check_update'] = round(time.time())
            self.time_in_check_update = time.time()
            if self.threads_stop:
                pf.write_file_log(self.name_module, f'Поток "check_update" завершён')
                break
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
        self.dict_signals[name_update] = self.dict_modules[name_update]['list_signals']
        item.need_update = False
        if item.global_error_module:
            item.global_error_module = False
            item.is_error = False
        item.time_update_module = os.path.getmtime(f'{main_dir}/{current_dir}/modules/{name_update}.py')
        pf.write_file_log(self.name_module,f'Расчётная функция модуля "{name_update}" обновлена')

    # Функция обновления данных, необходимых для расчёта, в модулях 
    def update_data_modules (self):
        pf.write_file_log(self.name_module,f'Запущен модуль"update_data_modules"')
        while True:
            self.times_daemons['update_data_modules'] = round(time.time())
            self.time_in_update_data_modules = time.time()
            if self.threads_stop:
                pf.write_file_log(self.name_module, f'Поток "update_data_modules" завершён')
                break
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

    def diagnostic_threads (self):
        while True:
            self.times_daemons['diagnostic_threads'] = round(time.time())
            if self.threads_stop:
                pf.write_file_log(self.name_module, f'Модуль диагностики "{self.name_module}" завершён')
                break
            for daemon in self.list_daemons:
                daemon_name = daemon.getName()
                daemon_is_alive = daemon.is_alive()
                if daemon_is_alive:
                    if time.time() - self.times_daemons[daemon_name] > 5:
                        status = 'Поток завис'
                    else:
                        status = 'Поток работает'
                else:
                    status = 'Поток нештатно завершил работу'
                self.dict_status_daemons[daemon_name] = {'status' : status, 'time' : time.strftime("%y.%m.%d %H:%M:%S", time.localtime(self.times_daemons[daemon_name]))}
            # print(self.dict_status_daemons)
            time.sleep(1)
import time, threading, os, sys

current_dir = "calc"
main_dir = os.path.dirname(os.path.abspath(__file__))[:-(len(current_dir)+1)]
sys.path.append(f"{main_dir}")

from secondary_functions import protocol_functions as pf

class Calculation:
    def __init__ (self, func_module, periodicity, name, autoupdate):
        """
            Конфигурационные переменные
                name_module - служебное название модуля
                func_module - расчётная функция
                autoupdate - возможность автообновления
                data - данные, необходимые для расчёта
                periodicity - периодичность расчёта, сек
                periodicity_global_error - периодичность опробования запуска расчётной
                    функции при возникновении ошибки, сек.
                max_try_start - максимальное количество попыток старта программы
        """
        self.name_module = name
        self.periodicity = periodicity
        self.func_module = func_module
        self.autoupdate = autoupdate
        self.data = {}
        self.periodicity_global_error = 2
        self.max_try_start = 10
        """
            Переменные отслеживания ошибок
                is_error - наличие ошибки в рассчёте в последнем цикле
                time_last_error - время последней ошибки
                last_error - текст последней ошибки
                dict_status_daemons - словарь состояний потоков
        """
        self.is_error = False
        self.time_last_error = 'Ошибок не было'
        self.last_error = 'Нет'
        self.dict_status_daemons = {}
        """
            Служебные переменные
                current_try_start - текущая попытка старта программы
                result - результат расчёта
                time_update_module - время последнего обновления модуля
                need_update - необходимость обновления модуля
                threads_stop - флаг остановки выполнения работы всех потоков
                calc_thread_stop - флаг остановки выполнения работы потока расчётной функции
                update_thread_stop - флаг остановки выполнения работы потока проверки обновлений
                Переменные названий потоков
                    check_update_module_name
                    calculation_module_name
                    diagnostic_threads_name
                list_daemons - список потоков, которые необходимо запустить
                times_daemons - время в потоках
        """
        self.current_try_start = 0
        self.result = {}
        self.time_update_module = os.path.getmtime(f'{main_dir}/{current_dir}/modules/{self.name_module}.py')
        self.need_update = False
        self.threads_stop = False
        self.calc_thread_stop = False
        self.update_thread_stop = False
        self.check_update_module_name = f'update_{self.name_module}'
        self.calculation_module_name = f'calculation_{self.name_module}'
        self.diagnostic_threads_name = f'diagnostic_threads_{self.name_module}'
        self.list_daemons = [threading.Thread(target=self.calculation, daemon=True, name=self.calculation_module_name),
                             threading.Thread(target=self.check_update_module, daemon=True, name=self.check_update_module_name),
                             threading.Thread(target=self.diagnostic_threads, daemon=True, name=self.diagnostic_threads_name),]
        self.times_daemons = {self.calculation_module_name : 0,
                              self.check_update_module_name : 0,
                              self.diagnostic_threads_name : 0}
        

    # Функция запуска модуля
    """
        Результаты выполнения:
            error - превышение количества попыток запуска
            ok - нормальный запуск
    """
    def run (self):
        self.current_try_start += 1
        if self.current_try_start > self.max_try_start:
            pf.write_file_log(self.name_module,'Превышено допустимое количество попыток старта модуля')
            self.threads_stop = True
            return 'error'
        else:
            pf.write_file_log(self.name_module, f'Запуск модуля "{self.name_module}"')
            try:
                status_start = self.start_daemons()
                if status_start == 'error':
                    self.error_run (f'Ошибка запуска одного или нескольких потоков модуля "{self.name_module}"')
            except:
                self.error_run (f'Ошибка запуска модуля "{self.name_module}"')
            else:
                pf.write_file_log(self.name_module, f'Модуль "{self.name_module}" успешно запущен')
                self.current_try_start = 0
                return 'ok'
            
    # Функция запуска потоков модуля
    """
        Результаты выполнения:
            error - неудачная попытка запуска одного или нескольких модулей
            ok - нормальный запуск
    """
    def start_daemons (self):
        try:
            for daemon in self.list_daemons:
                if not daemon.is_alive():
                    daemon.start()
        except:
            return 'error'
        else:
            return 'ok'
        

    # Функция обработки неудачного запуска модуля
    """
        Рекурсивный вызов функции run()
    """
    def error_run (self, message):
        pf.write_file_log(self.name_module, message)
        pf.write_file_log(self.name_module, f'Следующая попытка запуска модуля "{self.name_module}" через {self.periodicity_global_error} секунд')
        time.sleep(self.periodicity_global_error)
        self.run()

    
    # Функция проверки изменения файла модуля расчёта
    def check_update_module (self):
        while True:
            self.times_daemons[self.check_update_module_name] = time.time()
            if self.threads_stop or self.update_thread_stop:
                pf.write_file_log(self.name_module, f'Модуль обновления "{self.name_module}" завершён')
                break

            if os.path.getmtime(f'{main_dir}/{current_dir}/modules/{self.name_module}.py') != self.time_update_module:
                self.need_update = True
                pf.write_file_log(self.name_module, f'Требуется обновление расчётной функции модуля "{self.name_module}"')
            time.sleep(1)

    # Функция выполнения расчётной функции модуля
    """
        Результат успешного выполнения - изменение переменной result
    """
    def calculation (self):
        while True:
            self.times_daemons[self.calculation_module_name] = time.time()
            if self.threads_stop or self.calc_thread_stop:
                pf.write_file_log(self.name_module, f'Расчётный модуль "{self.name_module}" завершён')
                break
            try:
                self.is_error, error, local_result  = self.func_module(self.data)
                if self.is_error:
                    pf.write_file_log(self.name_module, f'Ошибка расчётного модуля {self.name_module}')
                    self.last_error = error
                    self.time_last_error, date = pf.get_time_mes()
                else:
                    self.result = local_result
            
            except:
                self.is_error = True
                self.time_last_error, date = pf.get_time_mes()
                self.last_error = f'Глобальная ошибка модуля "{self.name_module}".'
                pf.write_file_log(self.name_module, f'Глобальная ошибка расчётного модуля {self.name_module}')
            time.sleep (self.periodicity)

    def diagnostic_threads (self):
        while True:
            self.times_daemons[self.diagnostic_threads_name] = time.time()
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
                self.dict_status_daemons[daemon_name] = status
            print(self.dict_status_daemons)
            time.sleep(1)





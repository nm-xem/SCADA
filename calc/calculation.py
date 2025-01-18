import time, threading, os, sys

current_dir = "calc"
main_dir = os.path.dirname(os.path.abspath(__file__))[:-(len(current_dir)+1)]
sys.path.append(f"{main_dir}")

from secondary_functions import protocol_functions as pf

class Calculation:
    def __init__ (self, name_ru, func_module, periodicity, name, autoupdate):
        """
            Конфигурационные переменные
                name_module - служебное название модуля
                name_module_ru - название модуля для логов и сообщений
                func_module - расчётная функция
                autoupdate - возможность автообновления
                data - данные, необходимые для расчёта
                periodicity - периодичность расчёта, сек
                periodicity_global_error - периодичность опробования запуска расчётной
                    функции при возникновении ошибки, сек. Увеличивается с каждым циклом, пока не
                    достигнет максимального значения. Возвращается к первоначальному значению 
                    при восстановлении работоспособности расчётной функции
                max_periodicity_global_error - максимальная периодичность опробования
                    запуска расчётной функции при возникновении ошибки, сек
                max_errors - максимальное количество ошибок подряд, при котором объявляется
                    глобальная ошибка модуля
                max_try_start - максимальное количество попыток старта программы
        """
        self.name_module = name
        self.name_module_ru = name_ru
        self.periodicity = periodicity
        self.func_module = func_module
        self.autoupdate = autoupdate
        self.data = {}
        self.periodicity_global_error = 2
        self.max_periodicity_global_error = 16
        self.max_errors = 5
        self.max_try_start = 10

        """
            Переменные отслеживания ошибок
                is_error - наличие ошибки в рассчёте в последнем цикле
                global_error_module - наличие глобальной ошибки модуля
                time_last_error - время последней ошибки
                last_error - текст последней ошибки
        """
        self.is_error = False
        self.global_error_module = False
        self.time_last_error = 'Ошибок не было'
        self.last_error = 'Нет'

        """
            Служебные переменные
                current_try_start - текущая попытка старта программы
                result - результат расчёта
                time_update_module - время последнего обновления модуля
                need_update - необходимость обновления модуля
                thread_stop - флаг остановки выполнения работы всех потоков

                Переменные названий потоков
                    check_update_module_name
                    diagnostic_module_name
                    calculation_module_name
        """
        self.current_try_start = 0
        self.result = {}
        self.time_update_module = os.path.getmtime(f'{main_dir}/{current_dir}/modules/{self.name_module}.py')
        self.need_update = False
        self.threads_stop = False
        self.check_update_module_name = f'update_{self.name_module}'
        self.diagnostic_module_name = f'diagnostic_{self.name_module}'
        self.calculation_module_name = f'calculation_{self.name_module}'


        self.is_calc_thread_stop = True
        self.is_diag_thread_stop = True
        self.is_update_thread_stop = True

        self.calc_thread_stop = False
        self.diag_thread_stop = False
        self.update_thread_stop = False

    # Функция запуска модуля
    """
        Результаты выполнения:
            error - превышение количества попыток запуска
            ok - нормальный запуск
    """
    def run (self):
        self.current_try_start += 1
        self.global_error_module = False
        self.threads_stop = False

        if self.current_try_start > self.max_try_start:
            pf.write_file_log(self.name_module,'Превышено допустимое количество попыток старта модуля')
            return 'error'
        else:
            pf.write_file_log(self.name_module, f'Запуск модуля "{self.name_module_ru}"')
            try:
                status_start = self.creation_daemon_module()
                if status_start == 'error':
                    error_run (f'Ошибка запуска одного или нескольких потоков модуля "{self.name_module_ru}"')
            except:
                error_run (f'Ошибка запуска модуля "{self.name_module_ru}"')
            else:
                pf.write_file_log(self.name_module, f'Модуль "{self.name_module_ru}" успешно запущен')
                self.current_try_start = 0
                return 'ok'
        
        # Функция обработки неудачного запуска модуля
        """
            Рекурсивный вызов функции run()
        """
        def error_run (message):
            self.global_error_module = True
            self.threads_stop = True
            pf.write_file_log(self.name_module, message)
            pf.write_file_log(self.name_module, f'Ожидание остановки всех потоков модуля "{self.name_module_ru}"')
            while not (self.is_calc_thread_stop and self.is_update_thread_stop and self.is_diag_thread_stop):
                time.sleep(1)
            if self.periodicity_global_error < self.max_periodicity_global_error:
                self.periodicity_global_error *= 2
            pf.write_file_log(self.name_module, f'Все потоки модуля "{self.name_module_ru}" остановлены.\nСледующая попытка запуска модуля "{self.name_module_ru}" через {self.periodicity_global_error} секунд')
            time.sleep(self.periodicity_global_error)
            self.run()

    # Функция запуска потоков модуля
    """
        Результаты выполнения:
            error - неудачная попытка запуска одного или нескольких модулей
            ok - нормальный запуск
    """
    def creation_daemon_module (self):
        daemons = {self.calculation_module_name : self.calculation, 
                   self.diagnostic_module_name : self.diagnostic, 
                   self.check_update_module_name : self.check_update_module}
        try:
            for name_daemon, function_daemon in daemons.items():
                threading.Thread(target=function_daemon, daemon=True, name=name_daemon).start()
        except:
            self.calc_thread_stop = True
            self.diag_thread_stop = True
            self.update_thread_stop = True
            return 'error'
        else:
            self.is_calc_thread_stop = False
            self.is_diag_thread_stop = False
            self.is_update_thread_stop = False
            return 'ok'

    # Функция выполнения фоновой диагностики
    """
       list_diagnostic - список последних значений is_error 
    """
    def diagnostic (self):
        list_diagnostic = [False for i in range(self.max_errors)]
        while True:
            if self.threads_stop or self.diag_thread_stop:
                self.is_diag_thread_stop = True
                pf.write_file_log(self.name_module, f'Диагностический модуль "{self.name_module_ru}" завершён')
                break

            if not self.global_error_module:
                try:
                    list_diagnostic.pop(0)
                    list_diagnostic.append(self.is_error)
                    for is_error in list_diagnostic:
                        if not is_error:
                            self.global_error_module = False
                            self.periodicity_global_error = 2
                            break
                    else:
                        self.global_error_module = True
                        pf.write_file_log(self.name_module, f'Глобальная ошибка модуля "{self.name_module_ru}"')
                    time.sleep(self.periodicity)
                except:
                    pf.write_file_log(self.name_module, f'Ошибка выполнения диагностики модуля "{self.name_module_ru}"')
            else:
                time.sleep(self.periodicity_global_error)
        
    # Функция проверки изменения файла модуля расчёта
    def check_update_module (self):
        while True:
            if self.threads_stop or self.update_thread_stop:
                self.is_update_thread_stop = True
                pf.write_file_log(self.name_module, f'Модуль обновления "{self.name_module_ru}" завершён')
                break

            if os.path.getmtime(f'{main_dir}/{current_dir}/modules/{self.name_module}.py') != self.time_update_module:
                self.need_update = True
                pf.write_file_log(self.name_module, f'Требуется обновление расчётной функции модуля "{self.name_module_ru}"')
            time.sleep(1)

    # Функция выполнения расчётной функции модуля
    """
        Результат успешного выполнения - изменение переменной result
    """
    def calculation (self):
        while True:
            if self.threads_stop or self.calc_thread_stop:
                pf.write_file_log(self.name_module, f'Расчётный модуль "{self.name_module_ru}" завершён')
                self.is_calc_thread_stop = True
                break

            if not self.global_error_module:
                try:
                    self.is_error, error, local_result  = self.func_module(self.data)
                    if self.is_error:
                        self.last_error = error
                        self.time_last_error = time.time()
                    else:
                        self.result = local_result
                
                except:
                    self.is_error = True
                    self.time_last_error = time.time()
                    self.last_error = f'Глобальная ошибка модуля "{self.name_module_ru}".'
                    self.global_error_module = True
                
                # print (self.is_error, self.time_last_error, self.last_error, self.result)
                time.sleep (self.periodicity)
            else:
                if self.periodicity_global_error < 16:
                    self.periodicity_global_error *= 2
                pf.write_file_log(self.name_module, f'Ожидание исправления ошибки {self.periodicity_global_error} секунд')
                time.sleep(self.periodicity_global_error)


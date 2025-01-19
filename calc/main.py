from calculation_modules_manager import Calculation_modules_manager
import time, os, sys

current_dir = "calc"
main_dir = os.path.dirname(os.path.abspath(__file__))[:-(len(current_dir)+1)]
sys.path.append(f"{main_dir}")

from secondary_functions import protocol_functions as pf
name_module = 'main_module'
error = False

if __name__ == '__main__':
    list_modules = [Calculation_modules_manager()]
    for module in list_modules:
        try:
            module.run()
        except:
            pf.write_file_log(name_module,f'Не удалось запустить модуль "{module.name_module}"')
            for module in list_modules:
                try:
                    module.threads_stop = True
                except: pass
            error = True
            break
    else:
        pf.write_file_log(name_module,f'Все модули успешно запущены')
    while True:
        if error:
            break
        time.sleep(10)
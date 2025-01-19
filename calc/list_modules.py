import importlib, os, sys

current_dir = "calc"
main_dir = os.path.dirname(os.path.abspath(__file__))[:-(len(current_dir)+1)]
sys.path.append(f"{main_dir}")

from secondary_functions import protocol_functions as pf

error = False
list_modules = []
name_module = 'list_modules'
try:
    """
        !!! УКАЗАТЬ НЕОБХОДИМЫЙ ИМПОРТ МОДУЛЕЙ !!!
    """
    from modules import test1
except ImportError:
    pf.write_file_log(name_module,f'Попытка импорта несуществующего модуля')
    error = True
try:
    """
        !!! УКАЗАТЬ СПИСОК ИМПОРТИРОВАННЫХ МОДУЛЕЙ !!!
    """
    list_modules = [test1]
except NameError as ex:
    pf.write_file_log(name_module,f'Модуль "{ex.args[0][6:len(ex.args[0])-16]}" не существует')
    error = True

def update_dict_modules ():
    for module in list_modules:
        try:
            importlib.reload(module)
        except:
            pf.write_file_log(name_module,f'Ошибка в синтаксисе модуля {module.__name__[8:]}')
    result = create_dict_modules ()
    return result

# Функция создания словаря модулей с их описанием и внутренней функцией
def create_dict_modules ():
    dict_modules = {}
    # error, list_modules = import_calculation_modules ()
    if not error:
        try:
            for module in list_modules:
                dict_modules[module.__name__[8:]] = {
                    'function' : module.main,
                    'periodicity' : module.periodicity,
                    'autoupdate' : module.autoupdate,
                    'name_ru' : module.name_ru,
                    'list_signals' : module.list_signals,
                }
        except:
            pf.write_file_log(name_module,f'Ошибка в создании словаря модулей')
            return 'error'
        else:
            return dict_modules
    else:
        return 'error'

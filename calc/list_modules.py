import importlib
# Функция создания списка модулей расчёта и импорта этих модулей
# def import_calculation_modules ():
error = False
list_modules = []
try:
    """
        !!! УКАЗАТЬ НЕОБХОДИМЫЙ ИМПОРТ МОДУЛЕЙ !!!
    """
    from modules import test1, test2
except ImportError:
    print ('Попытка импорта несуществующего модуля')
    error = True
try:
    """
        !!! УКАЗАТЬ СПИСОК ИМПОРТИРОВАННЫХ МОДУЛЕЙ !!!
    """
    list_modules = [test1, test2]
except NameError as ex:
    print (f'Модуль "{ex.args[0][6:len(ex.args[0])-16]}" не существует.')
    error = True
# return error, list_modules

def update_dict_modules ():
    for module in list_modules:
        importlib.reload(module)
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
                }
        except:
            print (f'Ошибка в создании словаря модулей.')
            return 'error'
        else:
            return dict_modules
    else:
        return 'error'

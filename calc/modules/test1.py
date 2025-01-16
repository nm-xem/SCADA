import random
def main (data):
    is_error = False
    error = ''
    result = {}
    a = 0
    b = 0
    print(data)
    try:
        a = 15/(random.random()*14+1)
        b = 32/(random.random()*31+1)
    except:
        is_error = True
        error = 'Ошибка в делении'
    else:
        result['ИВС-1'] = a
        result['ИВС-2'] = b
    return is_error, error, result

name_ru = 'тест 1'
periodicity = 1
autoupdate = True
list_signals = ['1','2','3','4']
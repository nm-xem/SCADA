def main (data):
    is_error = False
    error = ''
    result = 0
    print('!!!!!!!!!')
    try:
        result = 1 + 5
    except:
        is_error = True
        error = 'Ошибка в сложении'
    return is_error, error, result

name_ru = 'тест 2'
periodicity = 2
autoupdate = True
list_signals = ['7','8']
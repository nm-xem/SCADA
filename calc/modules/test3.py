def main ():
    is_error = False
    error = ''
    result = 0
    try:
        result = 1 + 5
    except:
        is_error = True
        error = 'Ошибка в сложении'
    return is_error, error, 100

name_ru = 'тест 3'
periodicity = 1
autoupdate = True
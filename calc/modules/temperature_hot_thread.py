name_ru = 'Температуры горячих ниток'
periodicity = 1
autoupdate = True
dict_signals = {
    'IVS_1_analog' : ['818', '819', '820', '821', '822', '823'],
    'IVS_2_analog' : ['818', '819', '820', '821', '822', '823'],
    }
numbers_block = {'IVS_1_analog' : 1, 'IVS_2_analog' : 2}

def main (data):
    temperature_hot_threads = {}
    is_error = False
    error = ''
    for name_sistem, data_sistem in data.items():
        number_block = numbers_block[name_sistem]
        temperature_hot_threads[name_sistem] = calculation_temperature_hot_thread (data_sistem, number_block)
    return is_error, error, temperature_hot_threads

#Горячие нитки 1 очередь
def calculation_temperature_hot_thread (data, num_block):
    temperature_hot_threads = {}
    list_ref_analog_params = { 
        str(num_block * 100000)     : '818',
        str(num_block * 100000 + 1) : '819',
        str(num_block * 100000 + 2) : '820',
        str(num_block * 100000 + 3) : '821',
        str(num_block * 100000 + 4) : '822',
        str(num_block * 100000 + 5) : '823'
        }
    if data:
        for num_param, num_ref in list_ref_analog_params.items():
            x = data[num_ref]
            temperature_hot_threads[num_param] = round((0.0072069422 + 15.775525*0.07873*x - 0.2261183*(0.07873*x)**2 + 0.0094286756*(0.07873*x)**3 - 0.00035394655*(0.07873*x)**4 + 0.000010050886*(0.07873*x)**5 - 0.00000019323678*(0.07873*x)**6 + 0.0000000023816891*(0.07873*x)**7 - 0.000000000017130654*(0.07873*x)**8 + 0.00000000000005485733*(0.07873*x)**9), 1)
    else:
        for num_param, num_ref in list_ref_analog_params.items():
            temperature_hot_threads[num_param] = 0


    return temperature_hot_threads
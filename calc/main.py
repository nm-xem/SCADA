from calculation_modules_manager import Calculation_modules_manager
import time, os, sys

current_dir = "calc"
main_dir = os.path.dirname(os.path.abspath(__file__))[:-(len(current_dir)+1)]
sys.path.append(f"{main_dir}")

from secondary_functions import protocol_functions as pf
name_module = 'main_module'

if __name__ == '__main__':
    Calc_mm = Calculation_modules_manager()
    while True:
        time.sleep(10)
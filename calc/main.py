from calculation_modules_manager import Calculation_modules_manager
import time, os, sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

current_dir = "calc"
main_dir = os.path.dirname(os.path.abspath(__file__))[:-(len(current_dir)+1)]
sys.path.append(f"{main_dir}")

from secondary_functions import protocol_functions as pf
from secondary_functions.diagnostic_UI import Block_diagnostic as Block
from connect.connect_gateway import Connect_gateway

name_module = 'main_module'
error = False


class MyApp (App):
    def build(self):
        self.main_layout = BoxLayout(orientation='vertical')
        self.Block_diagnostic_calculation_modules = Block('Calculation_modules_manager', list_modules[0].dict_status_daemons)
        # for name_daemon, status_daemon in list_modules[0].dict_status_daemons.items()
        self.main_layout.add_widget(self.Block_diagnostic_calculation_modules.main_layoyt_module)
        self.dict_examplу_modules_calculation = {}
        for calc_module in list_modules[0].list_examplу_module:
            self.dict_examplу_modules_calculation[calc_module.name_module] = calc_module.dict_status_daemons

        self.dict_blocks_diagnostic_calculation = {}
        for name_calc_module, calc_module in self.dict_examplу_modules_calculation.items():
            self.dict_blocks_diagnostic_calculation[name_calc_module] = Block(name_calc_module, calc_module)
        for name_block, block in self.dict_blocks_diagnostic_calculation.items():
            self.main_layout.add_widget(block.main_layoyt_module)
        
        return self.main_layout
    
    def update_layout (self, instance):
        for name_daemon, status_daemon in list_modules[0].dict_status_daemons.items():
            self.Block_diagnostic_calculation_modules.labels_daemons_module[name_daemon]['time'].text = status_daemon['time']
            self.Block_diagnostic_calculation_modules.labels_daemons_module[name_daemon]['status'].text = status_daemon['status']
        for calc_module in list_modules[0].list_examplу_module:
            for name_daemon, status_daemon in calc_module.dict_status_daemons.items():
                self.dict_blocks_diagnostic_calculation[calc_module.name_module].labels_daemons_module[name_daemon]['time'].text = status_daemon['time']
                self.dict_blocks_diagnostic_calculation[calc_module.name_module].labels_daemons_module[name_daemon]['status'].text = status_daemon['status']

        # for name,calc_module in self.label_widgets.items():
        #     for name_thred, diag in calc_module.items():
        #         diag['name'].text = name_thred
        #         diag['status'].text = list_modules[0].list_examplу_module[0].dict_status_daemons[name_thred]['status']
        #         diag['time'].text = list_modules[0].list_examplу_module[0].dict_status_daemons[name_thred]['time']

    def on_start(self):
        Clock.schedule_interval(self.update_layout, 1)


# class MyApp (App):
#     def build(self):
#         self.main_layout = BoxLayout (orientation='vertical')
#         self.dict_modules_layouts = {
#             'connect_gateway' : {
#                 'layout' : BoxLayout (orientation='vertical'),
#                 'header' : Label (text='Клиент шлюза'),
#                 'diagnostic' : BoxLayout (orientation='vertical')
#                 },
#             'calculation_modules_manager' : {
#                 'layout' : BoxLayout (orientation='vertical'),
#                 'header' : Label (text='Менеджер расчётных модулей'),
#                 'diagnostic' : BoxLayout (orientation='vertical')
#                 },
#             'calculation_modules' : {
#                 'layout' : BoxLayout (orientation='vertical'),
#                 'header' : Label (text='Расчётные модули'),
#                 'diagnostic' : BoxLayout (orientation='vertical')
#                 },
                                                          
#         }
#         for name_module, module in self.dict_modules_layouts.items():
#             module['layout'].add_widget (module['header'])
#             module['layout'].add_widget (module['diagnostic'])
#             self.main_layout.add_widget (module['layout'])

#         dict_daemons = {}
#         for name_daemon, status_daemon in list_modules[0].dict_status_daemons.items():
#             dict_daemons[name_daemon] = {
#                 'labels' : {
#                     'name' = Label(text=name_daemon),
#                     'status' = Label(text=status_daemon['status']),
#                     'time_daemon' = Label(text=status_daemon['time']),
#                 },
#                 'daemon_layot' = BoxLayout ()
#             }
            
#             daemon_layot.add_widget(name)
#             daemon_layot.add_widget(status)
#             daemon_layot.add_widget(time_daemon)

#             self.dict_modules_layouts['calculation_modules_manager']['diagnostic'].add_widget (daemon_layot)
            
#         return self.main_layout


        
        # layout = BoxLayout (orientation='vertical')
        # self.label_widgets = {}
        # for calc_module in list_modules[0].list_examplу_module:
        #     self.label_widgets[calc_module.name_module] = {}
        #     for name_thread, dict_diag in calc_module.dict_status_daemons.items():
        #         self.label_widgets[calc_module.name_module][name_thread] = {'name' : Label (text=''),
        #                                                         'status' : Label (text=''),
        #                                                         'time'  : Label (text='')}
        # # print (self.label_widgets)
        # for name,calc_module in self.label_widgets.items():
        #     for name_thred, diag in calc_module.items():
        #         for name_diag, data_diag in diag.items():
        #             layout.add_widget (data_diag)
        # return layout
    
    # def update_layout (self, instance):
    #     for name,calc_module in self.label_widgets.items():
    #         for name_thred, diag in calc_module.items():
    #             diag['name'].text = name_thred
    #             diag['status'].text = list_modules[0].list_examplу_module[0].dict_status_daemons[name_thred]['status']
    #             diag['time'].text = list_modules[0].list_examplу_module[0].dict_status_daemons[name_thred]['time']

    # def on_start(self):
    #     Clock.schedule_interval(self.update_layout, 1)
            
if __name__ == '__main__':
    list_modules = [Calculation_modules_manager(), Connect_gateway()]
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
        
    # while True:
    if not error:
        # break
        # time.sleep(10)
        MyApp().run()
        
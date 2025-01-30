from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class Block_diagnostic ():
    def __init__(self, header, dict_daemons):
        self.header = header

        self.main_layoyt_module = BoxLayout (orientation='vertical')
        self.header_layoyt_module = BoxLayout ()
        self.body_layoyt_module = BoxLayout (orientation='vertical')
        self.dict_daemons = dict_daemons
        self.layouts_daemons_module = {}
        print(self.dict_daemons)

        for name_daemon in self.dict_daemons:
            self.layouts_daemons_module[name_daemon] = BoxLayout()
            # print(self.layouts_daemons_module[name_daemon].canvas.Line)
            # self.layouts_daemons_module[name_daemon].canvas.after.Color.rgba=(0,0,1,1)

        self.labels_daemons_module = {}

        # Заполняем layout header-а модуля
        self.header_label_header_layoyt = Label(text=self.header)
        self.header_layoyt_module.add_widget(self.header_label_header_layoyt)

        for name_daemon in self.layouts_daemons_module:
            self.labels_daemons_module[name_daemon] = {
                'name' : Label(text=name_daemon),
                'time' : Label(text=self.dict_daemons[name_daemon]['time']),
                'status' : Label(text=self.dict_daemons[name_daemon]['status']),
            }
        
        for name_daemon, layout_daemon in self.layouts_daemons_module.items():
            for name_label, label in self.labels_daemons_module[name_daemon].items():
                layout_daemon.add_widget(label)
            self.body_layoyt_module.add_widget(layout_daemon)

        # Добавляем в основной layout layout-ы header-а и boby
        self.main_layoyt_module.add_widget(self.header_layoyt_module)
        self.main_layoyt_module.add_widget(self.body_layoyt_module)
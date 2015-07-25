import kivy
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label

kivy.require('1.8.0') # replace with your current kivy version !

import requests

class AetherButton(Button):
    def __init__(self, **kwargs):
        super(AetherButton, self).__init__(**kwargs)
        self.aether = kwargs.get('aether')

    def on_press(self):
        print "TAXT"
        print self.text
        self.aether.post_program_change(self.text)
    # will provide onpress

class AetherServiceObject(object):
    def __init__(self, host):
        self.host = host
    # will provide methods to access remote LambentAether Installs
    # - poll for current state
    # - on init get avail progs
    # - select prog
    # - error handling when the service drops

    # initialized with a host (ip/port) at the least

    def get_available(self):
        target = self.host + "/progs"
        val = requests.get(target).json()
        return val['available_progs']

    def post_program_change(self, program_string):
        target = self.host + "/set?prog=" + program_string
        print target
        val = requests.get(target)
        print val


class LambentGrid(GridLayout):
    def __init__(self,**kwargs):
        self.aether = kwargs.get("aether")
        super(LambentGrid, self).__init__(**kwargs)
        self.cols = 3
        self.grid_get()

    def grid_clear(self):
        self.clear_widgets()

    def grid_get(self):
        avail = self.aether.get_available()
        for widget in avail:
            self.add_widget(AetherButton(text=widget, aether=self.aether))

    def grid_update(self):
        self.grid_clear()
        self.grid_get()


class LambentTopBarGrid(GridLayout):
    def __init__(self, **kwargs):
        self.aether = kwargs.get("aether")
        self.size_hint_y=None
        self.height=80
        self.cols=2

        super(LambentTopBarGrid, self).__init__(**kwargs)
        self.add_widget(
            Button(
                text='FilterS',
            ))
        self.add_widget(
            Button(
                text='Connection Status',
            ))



class LambentLayout(GridLayout):
    def __init__(self, **kwargs):
        self.aether = kwargs.get('aether')
        super(LambentLayout, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(
            Button(
                text='Settings',
                size_hint_x=None,
                width=80,
                size_hint_y=None,
                height=80
            ))
        self.add_widget(
            LambentTopBarGrid(
                aether=self.aether
            ))
        self.add_widget(
            Button(
                text='Lambent Select',
                size_hint_x=None,
                width=80
            ))
        self.add_widget(
            LambentGrid(
                aether=self.aether
            ))

class MyLambentApp(App):

    def build(self):
        self.title = "Lambent Controller"
        a = AetherServiceObject(host="http://192.168.13.26:8680")
        return LambentLayout(aether=a)
        return LambentGrid(aether=a)


if __name__ == '__main__':
    MyLambentApp().run()


#todo
# figure out a tabbed view
# spawn lambent grids into it, initialized with an AetherServiceObject
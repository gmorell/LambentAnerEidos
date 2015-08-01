import kivy
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.widget import Widget
from kivy.uix.label import Label
import socket
from zeroconf import Zeroconf, ServiceBrowser

kivy.require('1.8.0') # replace with your current kivy version !

import random
import requests


# tiny important objects
class AetherButton(Button):
    def __init__(self, **kwargs):
        super(AetherButton, self).__init__(**kwargs)
        self.aether = kwargs.get('aether')

    def on_press(self):
        self.aether.post_program_change(self.text)

class AetherServiceObject(object):
    def __init__(self, host, name, zcn):
        self.host = host
        self.name = name
        self.zcn = zcn

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


class AetherZeroConf(object):
    def __init__(self, *args, **kwargs):
        self.layout = kwargs.pop("layout")
        
    def remove_service(self, zeroconf, type, name):
        # print "service went bye"
        self.layout.tab_widget.remove(name)

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info and info.server == "lambentaether-autodisc-0.local.":
            full_addr = "%s:%d" % (socket.inet_ntoa(info.address), info.port)
            # print info.type
            # print 'name'
            # print info.properties
            self.layout.tab_widget.insert(host=full_addr, name=info.properties['name'], zcn=name)

# layout objects
class AetherTabbedPanel(TabbedPanel):
    # do_default_tab = False
    # TODO: make the empty thing work okay
    tab_pos = "left_top"

    tab_height = 80
    def __init__(self, **kwargs):
        # self.aether = kwargs.get('aether')
        self.aethers = {}
        super(AetherTabbedPanel, self).__init__(**kwargs)
        # self.add_widget(TabbedPanelHeader(
        #     text='Tab2', # set this to the name
        #     content=LambentGrid(
        #         aether=self.aether
        #     ),
        # ))

    def insert(self, host, name, zcn):
        host_plus_protocol = "http://" + host
        new_aether = AetherServiceObject(host=host_plus_protocol, name=name, zcn=zcn)
        new_grid = LambentGrid(aether=new_aether)
        new_tab = TabbedPanelHeader(
                text=name,
                content = new_grid
            )
        self.aethers[zcn] = [new_aether, new_tab]
        self.add_widget(
            new_tab
        )

    def remove(self, name):
        a = self.aethers.get(name, [])
        if a:
            print a
            self.remove_widget(a[1])

            del a


class LambentGrid(GridLayout):
    def __init__(self,**kwargs):
        self.aether = kwargs.get("aether")
        super(LambentGrid, self).__init__(**kwargs)
        self.cols = 3
        self.service_wait()
        self.grid_get()

    def service_wait(self):
        # groce
        service_found = False
        while not service_found:
            try:
                self.aether.get_available()
                service_found = True
            except requests.ConnectionError:
                pass

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
        self.cols=3

        super(LambentTopBarGrid, self).__init__(**kwargs)
        self.add_widget(
            Button(
                text='Settings',
                size_hint_x=None,
                width=80,
                size_hint_y=None,
                height=80
            ))
        self.add_widget(
            Button(
                text='FilterS',
                size_hint_y=None,
                height=80
            ))
        self.add_widget(
            Button(
                text='Connection Status',
                size_hint_y=None,
                height=80
            ))


class LambentLayout(GridLayout):
    def __init__(self, **kwargs):
        self.aether = kwargs.get('aether')
        super(LambentLayout, self).__init__(**kwargs)
        self.rows = 2
        self.add_widget(
            LambentTopBarGrid(
                aether=self.aether
            ))

        self.tab_widget = AetherTabbedPanel(
            aether=self.aether
        )
        self.add_widget(
            self.tab_widget
        )


class MyLambentApp(App):

    def build(self):
        self.title = "Lambent Controller"
        a = AetherServiceObject(host="http://192.168.13.26:8680", zcn="GCLOSET", name="k")
        layout = LambentLayout(aether=a)
        zclistener = AetherZeroConf(layout=layout)
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, "_http._tcp.local.", zclistener)
        return layout


if __name__ == '__main__':
    MyLambentApp().run()


#todo
# figure out a tabbed view
# spawn lambent grids into it, initialized with an AetherServiceObject
# k
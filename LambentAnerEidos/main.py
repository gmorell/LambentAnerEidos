import kivy
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.widget import Widget
from kivy.uix.label import Label
import socket
from zeroconf import Zeroconf, ServiceBrowser

kivy.require('1.8.0') # replace with your current kivy version !

__version__ = "0.0.1"

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

    def get_status(self):
        target = self.host + "/status"
        val = requests.get(target).json()
        return val['running']

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
            print info.type
            print full_addr
            print info.properties
            self.layout.tab_widget.insert(host=full_addr, name=info.properties['name'], zcn=name)

# layout objects
class AetherTabbedPanel(TabbedPanel):
    do_default_tab = False
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
        self.waiting_widget = TabbedPanelHeader(
            text="Waiting",
            content = Button(text="Waiting For Lambency")
        )
        self.add_widget(self.waiting_widget)
        self.waiting = True

    def insert(self, host, name, zcn):
        host_plus_protocol = "http://" + host
        new_aether = AetherServiceObject(host=host_plus_protocol, name=name, zcn=zcn)
        # get grids
        grid_settings = LambentTopBarInsideTabGrid(aether=new_aether)
        grid_buttons = LambentGrid(aether=new_aether)
        new_grid = LambentGridHolderWithControls(
            aether=new_aether,
            ctlgrid=grid_settings,
            btngrid=grid_buttons
        )
        new_tab = TabbedPanelHeader(
                text=name,
                content = new_grid
            )
        self.aethers[zcn] = [new_aether, new_tab]
        self.add_widget(
            new_tab
        )

        # bit of cleanup
        self.remove_widget(self.waiting_widget)
        self.waiting = False
        if len(self.get_tab_list()) == 1:
            # only if its the only one. its annoying otherwise
            self.switch_to(new_tab)

    def remove(self, name):
        a = self.aethers.get(name, [])
        if a:
            print a
            self.remove_widget(a[1])

            del a

        # add a placeholder
        l = self.get_tab_list()
        if len(l) == 0:
            # add default widget && switch to it
            self.add_widget(self.waiting_widget)
            self.switch_to(self.waiting_widget)
            self.waiting = True

class LambentGridHolderWithControls(GridLayout):
    def __init__(self, **kwargs):
        self.aether = kwargs.get("aether")
        super(LambentGridHolderWithControls, self).__init__(**kwargs)
        self.rows = 2
        self.add_widget(kwargs.get("ctlgrid"))
        self.add_widget(kwargs.get("btngrid"))

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
        # self.cols=3

        self.width=80
        self.cols = 1

        super(LambentTopBarGrid, self).__init__(**kwargs)
        self.add_widget(
            Button(
                text='Settings',
                size_hint_x=None,
                width=80,
                size_hint_y=None,
                height=80
            ))
        # self.add_widget(
        #     Button(
        #         text='FilterS',
        #         size_hint_y=None,
        #         height=80
        #     ))
        # self.add_widget(
        #     Button(
        #         text='Connection Status',
        #         size_hint_y=None,
        #         height=80
        #     ))

class LambentSpeedGrid(GridLayout):
    def __init__(self, **kwargs):
        self.rows=2
        self.size_hint_x=None
        self.width=90
        super(LambentSpeedGrid, self).__init__(**kwargs)
        self.add_widget(
            Button(
                text="+",
                # size_hint_x=None,
                # width=30,
            )
        )
        self.add_widget(
            Button(
                text="-",
                # size_hint_x=None,
                # width=30,
            )
        )
class LambentTopBarInsideTabGrid(GridLayout):
    def __init__(self, **kwargs):
        self.aether = kwargs.get("aether")
        self.size_hint_y=None
        self.height=60
        self.cols=4
        super(LambentTopBarInsideTabGrid, self).__init__(**kwargs)
        self.status_button = Button(
            text='Connection Status Pending',
            size_hint_y=None,
            height=self.height
        )
        self.statusclock = Clock.schedule_interval(self.set_status_button_text, 0.5)
        self.add_widget(
            Button(
                text='FilterS',
                size_hint_y=None,
                height=self.height,
                size_hint_x=None,
                width=100,
            ))
        self.add_widget(
            self.status_button
            )
        self.add_widget(
            Button(
                text='-',
                size_hint_x=None,
                width=60,
            )
        )
        self.add_widget(
            Button(
                text='+',
                size_hint_x=None,
                width=60,
            )
        )

    def set_status_button_text(self, x):
        state = self.aether.get_status()
        self.status_button.text = "Currently Running: %s " % state

class LambentLayout(GridLayout):
    def __init__(self, **kwargs):
        self.aether = kwargs.get('aether')
        super(LambentLayout, self).__init__(**kwargs)
        self.rows = 1
        # self.add_widget(
        #     LambentTopBarGrid(
        #         aether=self.aether
        #     ))

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
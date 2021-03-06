#! /usr/bin/python
import ptxconftools
from ptxconftools import ConfController
from ptxconftools.gtk import MonitorSelector
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3 as appindicator
import os

iconpath = os.path.dirname( ptxconftools.__file__ )+"/iconStyle03_256.png"
APPINDICATOR_ID = "PTXConf"
class PTXConfUI():
    def __init__(self):
        # create systray interface
        self.systray = appindicator.Indicator.new(APPINDICATOR_ID, "testname", appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.systray = appindicator.Indicator.new(APPINDICATOR_ID, iconpath, appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.systray.set_status(appindicator.IndicatorStatus.ACTIVE)

        # construct menu
        menu = gtk.Menu()
        mitem = gtk.MenuItem("configure")
        mitem.connect("activate", self.createConfigWindow)
        menu.append(mitem)
        mitem = gtk.MenuItem("exit")
        mitem.connect("activate", self.exit_program)
        menu.append(mitem)
        menu.show_all()

        # attach menu to out system tray
        # self.systray.set_menu(menu)

        # instantiate confcontroller
        self.myConf = ConfController()

    # def resetAllConfig(self, callback_data=None):
    #    self.myConf.resetAllDeviceConfig()

    def getActiveInput(self):
        a = self.window.ptDropdown.get_active_text()
        b = self.window.ptDropdown.get_active()
        if b > 0:
            return a

    def getSelectedMonitor(self, callback_data=None):
        a = self.window.monitorDropdown.get_active_text()
        b = self.window.monitorDropdown.get_active()
        if b > 0:
            return a

    def mapTabletToMonitor(self, callback_data=None):
        # find ids for the right input device
        pen = self.getActiveInput()
        # get the display width, screen_width and screen_offset for CTMGenerator function to calculate matrix
        monitor = self.getSelectedMonitor()
        # call API with these settings
        self.myConf.setPT2Monitor(pen, monitor)

    def exit_program(self, callback_data=None):
        # This function kills the program PTXConf.
        # Can be called from 2 places, 1 from the appindicator dropdown menu "Exit",
        # another from the config popup window "Exit" button.
        gtk.main_quit()

    def createConfigWindow(self, callback_data=None):
        # first refress all monitor and touch/pen information
        self.myConf.refresh()

        # This creats a popup window for more detailed configuration if user find necessary.
        # Still incomplete at the moment.
        self.window = gtk.Window()
        #self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_border_width(20)
        self.window.set_title("PTXConf")
        self.window.connect("destroy", self.destroyConfigWindow)

        button_apply = gtk.Button("Apply")
        button_close = gtk.Button("Close")

        button_close.connect("clicked", self.destroyConfigWindow)
        vbox = gtk.VBox(spacing=20)
        hbox = gtk.HBox(spacing=20)
        vboxLeft = gtk.VBox(spacing=6)
        vboxRight = gtk.VBox(spacing=6)
        hboxForButtons = gtk.HBox()
        hboxForButtonsLeft = gtk.HBox(spacing=30)
        hboxForButtonsRight = gtk.HBox(spacing=10)
        labelEmptySpace01 = gtk.Label()
        labelEmptySpace02 = gtk.Label()

        label01 = gtk.Label("pointer device")
        label02 = gtk.Label("monitor")
        # create monitor selector widget
        monSelector = MonitorSelector(self.myConf.monitorIds)
        # dropdown menus 1 and 2, users choose what input device map to what monitor.
        # creat and set up dopdownmenu 1: user select from a list of connected pen input deivces.
        ptDropdown = gtk.ComboBoxText()
#        ptDropdown.set_tooltip_text("choose an input device to configure")
        # getting the list of names of the input device
        # set up the dropdown selection for input devices
        ptDropdown.append_text('Select input device:')
        for i in self.myConf.penTouchIds:
            ptDropdown.append_text(i.decode() if isinstance(i, bytes) else i)
        ptDropdown.set_active(0)
        # ptDropdown.connect("changed", self.getActiveInput)
        # creat and set up dopdownmenu 2: user select from a list of connected display/output deivces.
        monitorDropdown = gtk.ComboBoxText()
#        monitorDropdown.set_tooltip_text("choose a monitor to map the input to")
        # getting the list of display names
        # set up the dropdown selection for monitors
        monitorDropdown.append_text('Select a monitor:')
        monitorDropdown.mons = self.myConf.monitorIds.keys()
        for key in monitorDropdown.mons:
            monitorDropdown.append_text(key.decode() if isinstance(key, bytes) else key)
        monitorDropdown.set_active(0)
        monitorDropdown.handler_id_changed = monitorDropdown.connect("changed", self.monDropdownCallback)

        # connect apply button to function
        button_apply.connect("clicked", self.mapTabletToMonitor)

        # inserting all widgets in place
        vboxLeft.pack_start(label01, False, False, True)
        vboxLeft.pack_start(label02, False, False, 0)

        vboxRight.pack_start(ptDropdown, False, False, True)
        vboxRight.pack_start(monitorDropdown, False, False, 0)

        hboxForButtonsLeft.pack_start(button_apply, False, False, 0)
        hboxForButtonsLeft.pack_start(labelEmptySpace01, False, False, 0)
        hboxForButtonsRight.pack_start(labelEmptySpace02, False, False, 0)
        hboxForButtonsRight.pack_start(button_close, False, False, 0)
        hboxForButtons.pack_start(hboxForButtonsLeft, False, False, 0)
        hboxForButtons.pack_start(hboxForButtonsRight, False, False, 0)

        vbox.pack_start(monSelector, False, False, 0)
        hbox.pack_start(vboxLeft, False, False, 0)
        hbox.pack_start(vboxRight, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(hboxForButtons, False, False, 0)
        self.window.add(vbox)
        self.window.show_all()

        # store convenient handle to drop down boxes
        self.window.monitorSelector = monSelector
        self.window.monitorSelector.connect('button-press-event', self.monSelectorCallback)
        self.window.ptDropdown = ptDropdown
        self.window.monitorDropdown = monitorDropdown

    def monDropdownCallback(self, calback_data=None):
        # update MonitorSelector
        mon = self.window.monitorDropdown.get_active_text()
        if mon in self.window.monitorSelector.moninfo:
            self.window.monitorSelector.set_active_mon(mon)

    def monSelectorCallback(self, widget, event):
        # get mon selector selection
        monSelection = self.window.monitorSelector.get_active_mon()
        # if different than drop down, update drop down
        if monSelection != self.window.monitorDropdown.get_active_text():
            # lookup this monitor index in drop down and set it...
            idx = list(self.window.monitorDropdown.mons).index(monSelection)
            # careful to disable dropdown changed callback while doing this
            hid = self.window.monitorDropdown.handler_id_changed
            self.window.monitorDropdown.handler_block(hid)
            self.window.monitorDropdown.set_active(idx+1)
            self.window.monitorDropdown.handler_unblock(hid)

    def destroyConfigWindow(self, callback_data=None):
        # close the popup window, app will still be docked on top menu bar.
        self.window.destroy()

    def main(self):
        gtk.main()


import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
p = PTXConfUI()
p.createConfigWindow()
p.window.connect("destroy", gtk.main_quit)
p.main()

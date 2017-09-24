#!/usr/bin/env python3

# Compact Workspace Switcher applet for Budgie Desktop
# https://github.com/dgaw/budgie-workspaces-compact
# Copyright (C) 2017 Damian Gaweda

# Based on budgie-desktop-examples by Ikey Doherty
# https://github.com/budgie-desktop/budgie-desktop-examples

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import gi.repository
gi.require_version('Budgie', '1.0')
gi.require_version('Wnck', '3.0')
from gi.repository import Budgie, GObject, Wnck, Gtk, Gdk, GdkX11

class WorkspacesCompact(GObject.GObject, Budgie.Plugin):
    """ Note you must always override Object, and implement Plugin. """

    # Good manners, make sure we have unique name in GObject type system
    __gtype_name__ = "WorkspacesCompact"

    def __init__(self):
        GObject.Object.__init__(self)

    def do_get_panel_widget(self, uuid):
        return WorkspacesCompactApplet(uuid)

class WorkspacesCompactApplet(Budgie.Applet):
    wn_screen = None
    label = None
    ev_box = None
    popover = None
    spin_button = None
    manager = None

    def __init__(self, uuid):
        Budgie.Applet.__init__(self)

        # WnckScreen
        self.wn_screen = Wnck.Screen.get_default()
        self.wn_screen.connect_after('active-workspace-changed', self.on_workspace_changed)

        # Main label that displays the workspace number
        self.label = Gtk.Label("") 
        self.label.set_margin_start(6)
        self.label.set_margin_end(6)
        self.label.set_margin_top(6)
        self.label.set_margin_bottom(6)

        # Event box to catch those events
        self.ev_box = Gtk.EventBox()
        self.ev_box.add_events(Gdk.EventMask.SCROLL_MASK)
        self.ev_box.connect('scroll-event', self.on_scroll)
        self.ev_box.connect('button-release-event', self.on_button_release)
        self.ev_box.add(self.label) 
        self.add(self.ev_box)

        # Settings popover
        self.spin_button = Gtk.SpinButton()
        self.spin_button.connect_after('value-changed', self.on_spin_button_changed)

        spin_label = Gtk.Label("Workspaces")
        spin_label.set_margin_end(6)

        box = Gtk.Box(Gtk.Orientation.HORIZONTAL, 1)
        box.set_border_width(6)
        box.pack_start(spin_label, False, False, 0)
        box.pack_start(self.spin_button, False, False, 0)
        box.show_all()

        self.popover = Budgie.Popover.new(self.ev_box)
        self.popover.add(box);

        self.show_all()
        self.update_label()

    def do_update_popovers(self, manager):
        """ Register with Budgie.PopoverManager """
        manager.register_popover(self.ev_box, self.popover)
        self.manager = manager

    def on_spin_button_changed(self, btn, udata=None):
        """ Handle the spin button - change number of workspaces """
        val = int(btn.get_value())
        if val > 0: # argh!
            self.wn_screen.change_workspace_count(val)
            self.update_label(ws_count=val)

    def on_workspace_changed(self, wscr, prev_ws, udata=None):
        """ Handle workspace changes """
        self.update_label()
        self.update_spin_button()

    def update_spin_button(self):
        """ Set the spin button to the current number of workspaces """
        ws_count = self.wn_screen.get_workspace_count()
        if ws_count > 0:
            self.spin_button.set_adjustment(Gtk.Adjustment(ws_count, 1, 10, 1, 10, 0))
        else:
            print ("WorkspacesCompactApplet-WARNING: couldn't get the number of workspaces for the popover!")

    def update_label(self, ws_count=None):
        """ Update the content of the label """
        ws = self.wn_screen.get_active_workspace()

        if ws is not None:
            count = ws_count if ws_count is not None else self.wn_screen.get_workspace_count()
            text = str(ws.get_number()+1) + "/" + str(count)
            self.label.set_label(text)
            self.label.set_tooltip_text(ws.get_name())
        # else:
        #     print ("WorkspacesCompactApplet-WARNING: update_label() - current workspace is None!")

    def on_scroll(self, widget, e):
        """ Handle the scroll wheel """

        if e.direction == Gdk.ScrollDirection.UP:
            # print ("You scrolled up, switch to prev workspace")
            prev_ws = self.get_prev_workspace()
            if prev_ws is not None:
                prev_ws.activate(x11_now())

        elif e.direction == Gdk.ScrollDirection.DOWN:
            # print ("You scrolled down, switch to next workspace")
            next_ws = self.get_next_workspace()
            if next_ws is not None:
                next_ws.activate(x11_now())

    def on_button_release(self, widget, e, udata=None):
        """ Handle mouse button clicks """

        # Left mouse button - switch to the next workspace
        if e.button == 1: 
            next_ws = self.get_next_workspace()
            if next_ws is not None:
                next_ws.activate(x11_now())

        # Right mouse button - shows/hides the popover
        elif e.button == 3: 
            if self.popover.get_visible() == True:
                self.popover.hide()
            else:
                self.manager.show_popover(self.ev_box)

    def get_next_workspace(self, wrap=True):
        """
        Determine and fetch the next workspace
        If "wrap" is true then calling this method on the last workspace
        will wrap around and return the first workspace
        If "wrap" is false then calling on the last workspace will return that workspace
        """
        ws = self.wn_screen.get_active_workspace()

        if ws is not None:
            count = self.wn_screen.get_workspace_count()
            ws_index = ws.get_number()

            if (ws_index + 1) < count:
                return self.wn_screen.get_workspace(ws_index + 1)
            else:
                # Last reached: wrap around to the first workspace if requested
                return ws if not wrap else self.wn_screen.get_workspace(0)
        else:
            return None

    def get_prev_workspace(self, wrap=True):
        """
        Determine and fetch the previous workspace
        If "wrap" is true then calling this method on the first workspace
        will wrap around and return the last workspace
        If "wrap" is false then calling on the first workspace will return that workspace
        """
        ws = self.wn_screen.get_active_workspace()

        if ws is not None:
            count = self.wn_screen.get_workspace_count()
            ws_index = ws.get_number()

            if (ws_index - 1) >= 0:
                return self.wn_screen.get_workspace(ws_index - 1)
            else:
                # First reached: wrap around to the last workspace if requested
                return ws if not wrap else self.wn_screen.get_workspace(count - 1)
        else:
            return None



# Utils

def x11_now():
    """ X11 server timestamp """
    return GdkX11.x11_get_server_time(Gdk.Screen.get_root_window(Gdk.Screen.get_default()))


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
from gi.repository import Budgie, GObject, Wnck, Gtk

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

    def __init__(self, uuid):
        Budgie.Applet.__init__(self)
        self.wn_screen = Wnck.Screen.get_default()

        self.label = Gtk.Label("") 
        self.label.set_margin_start(6)
        self.label.set_margin_end(6)
        self.label.set_margin_top(6)
        self.label.set_margin_bottom(6)
        self.add(self.label) 

        self.show_all()
        self.update_content()

        # Hook up Wnck signals
        self.wn_screen.connect_after('active-workspace-changed', self.on_workspace_changed)

    def update_content(self):
        ws = self.wn_screen.get_active_workspace()

        if ws is not None:
            count = self.wn_screen.get_workspace_count()
            text = str(ws.get_number()+1) + "/" + str(count)
            self.label.set_label(text)
            self.label.set_tooltip_text(ws.get_name())
        # else:
        #     print ("WorkspacesCompactApplet-WARNING: current workspace is None!")

    def on_workspace_changed(self, wscr, prev_ws, udata=None):
        self.update_content()

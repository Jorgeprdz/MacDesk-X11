"""A short card flip rendered by GTK's frame clock, idle between clicks."""
import math
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
try:
    gi.require_foreign('cairo')
    HAS_CAIRO = True
except ImportError:
    HAS_CAIRO = False


class FlipStack(Gtk.Stack):
    DURATION_US = 340000

    def __init__(self):
        super().__init__()
        self.set_transition_type(Gtk.StackTransitionType.NONE)
        self.set_hhomogeneous(True)
        self.set_vhomogeneous(True)
        self.tick_id = 0
        self.progress = 1.0
        self.target = None
        self.connect('destroy', self.stop)

    def flip_to(self, name):
        if self.tick_id or name == self.get_visible_child_name():
            return False
        if not HAS_CAIRO or not self.get_mapped() or not self.get_settings().get_property('gtk-enable-animations'):
            self.set_visible_child_name(name)
            return True
        self.target = name
        self.started = self.get_frame_clock().get_frame_time()
        self.progress = 0.0
        self.tick_id = self.add_tick_callback(self.advance)
        return True

    def advance(self, widget, clock):
        self.progress = min(1.0, (clock.get_frame_time() - self.started) / self.DURATION_US)
        if self.progress >= .5 and self.get_visible_child_name() != self.target:
            self.set_visible_child_name(self.target)
        self.queue_draw()
        if self.progress >= 1.0:
            self.tick_id = 0
            self.target = None
            return False
        return True

    if HAS_CAIRO:
        def do_draw(self, cr):
            if not self.tick_id:
                return Gtk.Stack.do_draw(self, cr)
            eased = .5 - .5 * math.cos(math.pi * self.progress)
            scale = max(.015, abs(math.cos(math.pi * eased)))
            center = self.get_allocated_width() / 2
            cr.save()
            cr.translate(center, 0)
            cr.scale(scale, 1)
            cr.translate(-center, 0)
            result = Gtk.Stack.do_draw(self, cr)
            cr.restore()
            return result

    def stop(self, *args):
        if self.tick_id:
            self.remove_tick_callback(self.tick_id)
            self.tick_id = 0
        self.target = None

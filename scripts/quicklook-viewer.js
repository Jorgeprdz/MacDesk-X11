#!/usr/bin/gjs
// Ephemeral GTK viewer. No WebView, playback daemon, watcher or history graph.
imports.gi.versions.Gtk = '3.0';
const {Gtk, Gdk, GdkPixbuf, GLib} = imports.gi;
const ByteArray = imports.byteArray;
Gtk.init(null);
const [ok, bytes] = GLib.file_get_contents(ARGV[0]);
GLib.unlink(ARGV[0]);
if (!ok) throw new Error('Preview metadata unavailable');
const data = JSON.parse(ByteArray.toString(bytes));
const win = new Gtk.Window({title: data.title, default_width: 780, default_height: 540,
    window_position: Gtk.WindowPosition.CENTER, type_hint: Gdk.WindowTypeHint.DIALOG});
win.connect('destroy', () => Gtk.main_quit());
win.connect('key-press-event', (_w, event) => {
    const key = event.get_keyval()[1];
    if (key === Gdk.KEY_Escape || key === Gdk.KEY_space) { win.destroy(); return true; }
    return false;
});
const box = new Gtk.Box({orientation: Gtk.Orientation.VERTICAL, spacing: 8, margin: 12});
win.add(box);
if (data.image) {
    try {
        const [format, width, height] = GdkPixbuf.Pixbuf.get_file_info(data.image);
        if (!format || width * height > 40000000) throw new Error('Image exceeds 40 megapixel decode budget');
        const pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(data.image, 1000, 700, true);
        box.pack_start(Gtk.Image.new_from_pixbuf(pixbuf), true, true, 0);
    } catch (e) { data.text += '\n' + e.message; }
}
const scroll = new Gtk.ScrolledWindow({hexpand: true, vexpand: true});
const text = new Gtk.TextView({editable: false, cursor_visible: false, monospace: true,
    wrap_mode: Gtk.WrapMode.WORD_CHAR});
text.buffer.set_text(data.text || '', -1);
scroll.add(text);
box.pack_start(scroll, true, true, 0);
win.show_all();
Gtk.main();

#!/usr/bin/gjs
imports.gi.versions.Gtk = '3.0';
const {Gtk, Gdk, Gio} = imports.gi;
Gtk.init(null);
const win = new Gtk.Window({title: 'MacDesk · Window Snap', window_position: Gtk.WindowPosition.CENTER,
    resizable: false, type_hint: Gdk.WindowTypeHint.DIALOG});
win.connect('destroy', () => Gtk.main_quit());
win.connect('key-press-event', (_w, e) => {if (e.get_keyval()[1] === Gdk.KEY_Escape) win.destroy(); return false;});
const grid = new Gtk.Grid({margin: 12, row_spacing: 6, column_spacing: 6});
win.add(grid);
const zones = [['50% left','left'],['50% right','right'],['Maximize','up'],
    ['33% left','third-left'],['33% center','third-center'],['33% right','third-right'],
    ['67% left','two-thirds-left'],['67% right','two-thirds-right'],['Restore','down'],
    ['¼ top left','top-left'],['¼ top right','top-right'],['¼ bottom left','bottom-left'],['¼ bottom right','bottom-right']];
zones.forEach(([label, zone], i) => {
    const button = new Gtk.Button({label});
    button.connect('clicked', () => {
        Gio.Subprocess.new(['python3', ARGV[0], 'snap', zone, '--window', ARGV[1]], Gio.SubprocessFlags.NONE);
        win.destroy();
    });
    grid.attach(button, i%3, Math.floor(i/3), 1, 1);
});
win.show_all();
Gtk.main();

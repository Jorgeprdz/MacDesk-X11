#!/usr/bin/gjs
// Native libraries already installed by Sushi; worker exits after one preview.
const {GLib, Gio, Gdk, GdkPixbuf} = imports.gi;
const path = ARGV[0], output = ARGV[1];
const uri = Gio.File.new_for_path(path).get_uri();
if (/\.(png|jpe?g|webp|gif|svg)$/i.test(path)) {
    const [format, width, height] = GdkPixbuf.Pixbuf.get_file_info(path);
    if (!format || width * height > 40000000) throw new Error('Image exceeds 40 megapixel budget');
    const pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 1280, 1280, true);
    pixbuf.savev(output, 'png', [], []);
    print(JSON.stringify({text: `${width} × ${height}`}));
} else if (path.toLowerCase().endsWith('.pdf')) {
    const Ev = imports.gi.EvinceDocument;
    Ev.init();
    const document = Ev.Document.factory_get_document(uri);
    const [w, h] = document.get_page_size(0);
    const scale = Math.min(1280 / w, 1280 / h, 2);
    const page = document.get_page(0);
    const context = Ev.RenderContext.new(page, 0, scale);
    const surface = document.render(context);
    const pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0, Math.ceil(w*scale), Math.ceil(h*scale));
    pixbuf.savev(output, 'png', [], []);
    print(JSON.stringify({text: `${document.get_n_pages()} pages · preview page 1`}));
} else {
    const {Gst, GstPbutils} = imports.gi;
    Gst.init(null);
    const info = GstPbutils.Discoverer.new(4 * Gst.SECOND).discover_uri(uri);
    let lines = [`Duration: ${(info.get_duration() / Gst.SECOND).toFixed(1)} s`];
    const tags = info.get_tags();
    if (tags) {
        for (const name of ['title', 'artist', 'album']) {
            const [present, value] = tags.get_string(name);
            if (present) lines.push(`${name}: ${value.slice(0, 4096)}`);
        }
    }
    const videos = info.get_video_streams();
    if (videos.length) {
        const video = videos[0];
        const scale = Math.min(960/video.get_width(), 540/video.get_height(), 1);
        const width = Math.max(1, Math.round(video.get_width()*scale));
        const height = Math.max(1, Math.round(video.get_height()*scale));
        lines.push(`${video.get_width()} × ${video.get_height()}`);
        const playbin = Gst.ElementFactory.make('playbin', null);
        const sink = Gst.ElementFactory.make('appsink', null);
        sink.set_property('caps', Gst.Caps.from_string(`video/x-raw,format=RGB,width=${width},height=${height}`));
        sink.set_property('max-buffers', 1);
        sink.set_property('drop', true);
        playbin.set_property('uri', uri);
        playbin.set_property('video-sink', sink);
        playbin.set_property('audio-sink', Gst.ElementFactory.make('fakesink', null));
        try {
            playbin.set_state(Gst.State.PAUSED);
            playbin.get_state(4 * Gst.SECOND);
            const sample = sink.get_property('last-sample');
            if (sample) {
                const buffer = sample.get_buffer();
                const [ok, map] = buffer.map(Gst.MapFlags.READ);
                if (ok) {
                    const stride = Math.floor(map.data.length / height);
                    const pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(new GLib.Bytes(map.data),
                        GdkPixbuf.Colorspace.RGB, false, 8, width, height, stride);
                    pixbuf.savev(output, 'png', [], []);
                    buffer.unmap(map);
                }
            }
        } finally { playbin.set_state(Gst.State.NULL); }
    }
    print(JSON.stringify({text: lines.join('\n')}));
}

"""On-demand GTK3 dock stacks and Android control center."""
import os,subprocess,threading,unicodedata
from pathlib import Path
import gi
gi.require_version('Gtk','3.0');gi.require_version('Gdk','3.0')
from gi.repository import Gtk,Gdk,GdkPixbuf,Gio,GLib,Pango
from macdesk_hub_model import HubModel,atomic_json
from macdesk_android_client import request
from macdesk_appearance import apply_global_dark
from macdesk_flip import FlipStack
from macdesk_notifications import notification_time

CSS='''
#macdesk-hub { background: rgba(233,237,244,.94); border: 1px solid rgba(255,255,255,.72); border-radius: 22px; color: #242a35; }
#macdesk-hub * { font-family: Sans; font-size: 13px; color: #242a35; }
#macdesk-hub .hub-title { font-size: 21px; font-weight: bold; }
#macdesk-hub .hub-subtitle { font-size: 12px; color: #616a79; }
#macdesk-hub button { background: rgba(255,255,255,.45); border: 0; border-radius: 12px; box-shadow: none; padding: 8px 12px; }
#macdesk-hub button:hover { background: rgba(255,255,255,.85); }
#macdesk-hub button:active { background: rgba(50,120,230,.20); }
#macdesk-hub button.hub-tile { padding: 8px; background: transparent; }
#macdesk-hub button.hub-tile:hover { background: rgba(255,255,255,.65); }
#macdesk-hub list, #macdesk-hub row { background: transparent; }
#macdesk-hub flowboxchild { padding: 2px; background: transparent; }
#macdesk-hub entry { background: rgba(255,255,255,.66); border: 0; border-radius: 12px; padding: 9px; color: #242a35; }
#macdesk-hub .hub-card { background: rgba(255,255,255,.48); border-radius: 14px; padding: 12px; }
#macdesk-hub .hub-error { color: #a52630; }
#macdesk-hub .hub-primary { background: #287be9; color: white; }
#macdesk-hub .hub-primary * { color: white; }
#macdesk-hub scrollbar { background: transparent; }
#macdesk-hub checkbutton { padding: 6px; }
#macdesk-hub check { border-radius: 5px; }
#macdesk-hub .notification-card { background: rgba(255,255,255,.82); border-radius: 20px; padding: 14px; }
#macdesk-hub .notification-app { font-size: 12px; font-weight: bold; color: #586176; }
#macdesk-hub .notification-title { font-size: 15px; font-weight: bold; }
#macdesk-hub .notification-body { font-size: 13px; color: #4a5160; }
#macdesk-hub.dark .notification-card { background: rgba(66,72,84,.86); }
#macdesk-hub.dark .notification-app, #macdesk-hub.dark .notification-body { color: #cbd2e0; }
#macdesk-hub.dark { background: rgba(35,39,48,.94); border-color: rgba(255,255,255,.24); }
#macdesk-hub.dark * { color: #f2f4f8; }
#macdesk-hub.dark .hub-subtitle { color: #b6becb; }
#macdesk-hub.dark button,#macdesk-hub.dark .hub-card { background: rgba(255,255,255,.08); }
#macdesk-hub.dark button:hover { background: rgba(255,255,255,.18); }
#macdesk-hub.dark entry { background: rgba(255,255,255,.12); color: #f2f4f8; }
'''

def normalized(text):return ''.join(c for c in unicodedata.normalize('NFKD',text.casefold()) if not unicodedata.combining(c))
def style(widget,name):widget.get_style_context().add_class(name);return widget
def label(text,kind=None):
 w=Gtk.Label(label=text,xalign=0)
 if kind:style(w,kind)
 return w

def image(path=None,name=None,size=48):
 try:
  if path and Path(path).is_file():return Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_scale(str(path),size,size,True))
 except GLib.Error:pass
 w=Gtk.Image.new_from_icon_name(name or 'application-x-executable',Gtk.IconSize.DIALOG);w.set_pixel_size(size);return w

def dock_geometry():
 from Xlib import display,X,error
 d=display.Display();root=d.screen().root;screen=root.get_geometry();dock=None
 try:
  clients=root.get_full_property(d.intern_atom('_NET_CLIENT_LIST'),X.AnyPropertyType)
  for wid in clients.value if clients else []:
   try:
    w=d.create_resource_object('window',int(wid))
    if 'xfce4-panel' not in (w.get_wm_class() or ()):continue
    p=root.translate_coords(w,0,0);g=w.get_geometry()
    if p.y>screen.height//2:dock=(p.x,p.y,g.width,g.height)
   except error.XError:pass
  pointer=root.query_pointer()
  return screen.width,screen.height,dock,pointer.root_x
 finally:d.close()

class HubWindow(Gtk.ApplicationWindow):
 def __init__(self,app,mode):
  super().__init__(application=app);self.hub=app;self.model=app.model;self.mode=mode;self.checks={};self.initializing=True
  self.set_name('macdesk-hub');self.set_title({'apps':'Aplicaciones','downloads':'Descargas','control':'Centro de control','choose':'Elegir apps de Android'}[mode]);self.set_wmclass('macdesk-hub','MacDeskHub')
  self.set_decorated(False);self.set_skip_taskbar_hint(True);self.set_skip_pager_hint(True);self.set_keep_above(True);self.set_type_hint(Gdk.WindowTypeHint.POPUP_MENU)
  visual=self.get_screen().get_rgba_visual()
  if visual:self.set_visual(visual)
  self.connect('key-press-event',self.key);self.connect('focus-out-event',self.blur)
  self.box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=12);self.box.set_border_width(18);self.add(self.box)
  header=Gtk.Box(spacing=8);header.pack_start(label(self.get_title(),'hub-title'),True,True,0);close=Gtk.Button.new_from_icon_name('window-close-symbolic',Gtk.IconSize.BUTTON);close.connect('clicked',lambda b:self.destroy());header.pack_end(close,False,False,0);self.box.pack_start(header,False,False,0)
  self.notice=label('','hub-subtitle');self.notice.set_line_wrap(True);self.notice.set_max_width_chars(58)
  self.refresh_theme()
  if mode=='apps':self.apps_ui()
  elif mode=='downloads':self.downloads_ui()
  elif mode=='choose':self.choose_ui()
  else:self.control_ui()
  self.box.pack_end(self.notice,False,False,0)
  self.set_default_size(600 if mode in ('apps','downloads','choose') else 430,480 if mode!='control' else 530)
  self.show_all();self.initializing=False;GLib.timeout_add(60,self.anchor)
 def refresh_theme(self):
  dark='dark' in self.hub.xfget('xsettings','/Net/ThemeName','Adwaita').lower()
  self.get_style_context().remove_class('dark')
  if dark:self.get_style_context().add_class('dark')
 def key(self,w,event):
  if event.keyval==Gdk.KEY_Escape:self.destroy();return True
  return False
 def blur(self,w,event):
  if not self.initializing and not self.hub.testing:GLib.timeout_add(300,self.close_unfocused)
  return False
 def close_unfocused(self):
  if self.get_visible() and not self.is_active():self.destroy()
  return False
 def anchor(self):
  if not self.get_visible():return False
  sw,sh,dock,pointer=dock_geometry();width,height=self.get_size();self.resize(min(width,sw-32),min(height,sh-100))
  if self.mode=='choose':x=(sw-width)//2;y=max(30,(sh-height)//2)
  else:
   x=max(16,min(pointer-width//2,sw-width-16));y=max(24,(dock[1] if dock else sh-100)-height-10)
  self.move(x,y);return False
 def status(self,text,error=False):
  if not self.get_visible():return False
  self.notice.set_text(text)
  context=self.notice.get_style_context();context.remove_class('hub-error')
  if error:context.add_class('hub-error')
  return False
 def async_android(self,payload,done=None,failed=None):
  self.status('Conectando con Android…')
  def worker():
   try:
    response=request(payload,timeout=100 if payload['action']=='catalog' else 45 if payload['action']=='notifications' else 25,model=self.model)
    def complete():
     if not self.get_visible():return False
     self.status('')
     if done:done(response)
     return False
    GLib.idle_add(complete)
   except Exception as error:
    GLib.idle_add(self.status,str(error),True)
    if failed:GLib.idle_add(failed)
  threading.Thread(target=worker,daemon=True).start()
 def button(self,text,callback,icon=None):
  button=Gtk.Button();row=Gtk.Box(spacing=8)
  if icon:row.pack_start(image(name=icon,size=20),False,False,0)
  row.pack_start(label(text),True,True,0);button.add(row);button.connect('clicked',callback);return button
 def scroller(self,height=300):
  scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC);scroll.set_min_content_height(height);scroll.set_max_content_height(height);self.box.pack_start(scroll,True,True,0);return scroll
 def grid(self,scroll):
  flow=Gtk.FlowBox();flow.set_selection_mode(Gtk.SelectionMode.NONE);flow.set_min_children_per_line(4);flow.set_max_children_per_line(4);flow.set_row_spacing(4);flow.set_column_spacing(4);scroll.add(flow);return flow
 def tile(self,flow,text,callback,path=None,icon=None,badge='',tooltip=''):
  button=style(Gtk.Button(),'hub-tile');column=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6);column.set_size_request(116,108);column.pack_start(image(path,icon,52),False,False,0)
  name=Gtk.Label(label=text);name.set_line_wrap(True);name.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR);name.set_ellipsize(Pango.EllipsizeMode.END);name.set_max_width_chars(15);name.set_lines(2);name.set_justify(Gtk.Justification.CENTER);column.pack_start(name,False,False,0)
  if badge:column.pack_start(label(badge,'hub-subtitle'),False,False,0)
  button.add(column);button.set_tooltip_text(tooltip or text);button.connect('clicked',callback);button._search=normalized(text+' '+tooltip);flow.add(button);return button
 def add_search(self,placeholder):
  search=Gtk.SearchEntry();search.set_placeholder_text(placeholder);self.box.pack_start(search,False,False,0);return search
 def bind_search(self,search,flow):
  flow.set_filter_func(lambda child:normalized(search.get_text()) in child.get_child()._search);search.connect('search-changed',lambda s:flow.invalidate_filter())
 def android_launch(self,component):self.async_android({'action':'launch','component':component},lambda r:self.destroy())
 def desktop_launch(self,filename):
  info=Gio.DesktopAppInfo.new_from_filename(str(Path.home()/'.local/share/applications'/filename))
  try:
   if not info:raise RuntimeError('Acceso no disponible')
   info.launch([],None);self.destroy()
  except Exception as error:self.status(str(error),True)
 def apps_ui(self):
  self.box.pack_start(label('Ctrl+Alt+Espacio · Tus apps de Android y MacDesk','hub-subtitle'),False,False,0)
  search=self.add_search('Buscar aplicaciones…');flow=self.grid(self.scroller(270))
  for a in self.model.selected_apps():self.tile(flow,a['label'],lambda b,c=a['component']:self.android_launch(c),path=self.model.icon_path(a),badge='Android',tooltip=a['package'])
  for file in ('macdesk-nautilus.desktop','20-firefox.desktop','80-lineaindividual.desktop','onlyoffice-desktopeditors.desktop','40-terminal.desktop'):
   info=Gio.DesktopAppInfo.new_from_filename(str(Path.home()/'.local/share/applications'/file))
   if info:
    icon=info.get_string('Icon') or '';self.tile(flow,info.get_name(),lambda b,f=file:self.desktop_launch(f),path=icon if icon.startswith('/') else None,icon=icon,badge='MacDesk')
  self.bind_search(search,flow)
  self.box.pack_start(self.button('Elegir apps de Android',lambda b:self.hub.show_mode('choose'),'emblem-system-symbolic'),False,False,0)
 def choose_ui(self):
  self.box.pack_start(label('Marca solo las apps que quieres en Aplicaciones.','hub-subtitle'),False,False,0)
  search=self.add_search('Buscar por nombre o paquete…');scroll=self.scroller(330);listbox=Gtk.ListBox();listbox.set_selection_mode(Gtk.SelectionMode.NONE);scroll.add(listbox);selected=set(self.hub.pending_selection if self.hub.pending_selection is not None else self.model.selected_packages());self.hub.pending_selection=None
  for app in self.model.catalog():
   row=Gtk.ListBoxRow();row._search=normalized(app['label']+' '+app['package']);box=Gtk.Box(spacing=10);box.set_border_width(3);box.pack_start(image(self.model.icon_path(app),size=34),False,False,0);texts=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=1);texts.pack_start(label(app['label']),False,False,0);texts.pack_start(label(app['package'],'hub-subtitle'),False,False,0);box.pack_start(texts,True,True,0);check=Gtk.CheckButton();check.set_active(app['package'] in selected);box.pack_end(check,False,False,0);self.checks[app['package']]=check;row.add(box);listbox.add(row)
  listbox.connect('row-activated',lambda box,row:row.get_child().get_children()[-1].set_active(not row.get_child().get_children()[-1].get_active()))
  listbox.set_filter_func(lambda row:normalized(search.get_text()) in row._search);search.connect('search-changed',lambda s:listbox.invalidate_filter())
  self.count=label('','hub-subtitle');self.box.pack_start(self.count,False,False,0)
  for check in self.checks.values():check.connect('toggled',lambda c:self.selection_count())
  self.selection_count();actions=Gtk.Box(spacing=8);actions.pack_start(self.button('Actualizar lista',self.refresh_catalog,'view-refresh-symbolic'),False,False,0)
  actions.pack_start(self.button('Quitar todas',lambda b:[c.set_active(False) for c in self.checks.values()]),False,False,0)
  save=style(self.button('Guardar',self.save_selection),'hub-primary');actions.pack_end(save,False,False,0);self.box.pack_start(actions,False,False,0)
 def selection_count(self):self.count.set_text(f'{sum(c.get_active() for c in self.checks.values())} apps seleccionadas · las demás quedan fuera de la carpeta')
 def save_selection(self,button):
  self.model.save_selection([package for package,check in self.checks.items() if check.get_active()]);self.model.sync_launchers();self.hub.show_mode('apps')
 def refresh_catalog(self,button):
  button.set_sensitive(False)
  pending=[package for package,check in self.checks.items() if check.get_active()]
  def updated(response):
   self.hub.pending_selection=pending;self.hub.show_mode('choose')
  self.async_android({'action':'catalog'},updated,lambda:button.set_sensitive(True))
 def downloads_ui(self):
  self.box.pack_start(label('Descargas del teléfono · más recientes primero','hub-subtitle'),False,False,0)
  search=self.add_search('Buscar en Descargas…');flow=self.grid(self.scroller(270));entries=self.model.recent_downloads()
  for path in entries:
   info=Gio.File.new_for_path(str(path)).query_info('standard::icon',Gio.FileQueryInfoFlags.NONE,None);gicon=info.get_icon();names=gicon.get_names() if isinstance(gicon,Gio.ThemedIcon) else [];icon=names[0] if names else 'text-x-generic'
   thumb=path if path.suffix.lower() in ('.png','.jpg','.jpeg','.webp') and path.is_file() and path.stat().st_size<20*1024*1024 else None
   self.tile(flow,path.name,lambda b,p=path:self.open_download(p),path=thumb,icon='folder' if path.is_dir() else icon,tooltip=path.name)
  self.bind_search(search,flow)
  if not entries:self.status('No hay archivos en Descargas.')
  actions=Gtk.Box(spacing=8);actions.pack_start(self.button('Abrir carpeta',lambda b:self.open_folder(self.model.downloads),'folder-open-symbolic'),True,True,0);actions.pack_end(self.button('Actualizar',lambda b:self.hub.show_mode('downloads'),'view-refresh-symbolic'),False,False,0);self.box.pack_start(actions,False,False,0)
 def open_folder(self,path):subprocess.Popen(['/usr/local/bin/macdesk-nautilus',str(path)],start_new_session=True);self.destroy()
 def open_download(self,path):
  if path.is_dir():self.open_folder(path);return
  try:self.async_android({'action':'open','path':self.model.android_download_path(path)},lambda r:self.destroy())
  except Exception as error:self.status(str(error),True)
 def control_ui(self):
  self.faces=FlipStack();self.box.pack_start(self.faces,True,True,0)
  self.control_front=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=12)
  self.faces.add_named(self.control_front,'controls');self.notifications_ui()
  self.faces.set_visible_child_name('controls')
  self.control_front.pack_start(self.button('Notificaciones',self.show_notifications,'preferences-system-notifications-symbolic'),False,False,0)
  self.battery=label('Consultando Android…','hub-subtitle');self.control_front.pack_start(self.battery,False,False,0)
  tiles=Gtk.Grid(column_spacing=8,row_spacing=8)
  for index,(title,icon,page) in enumerate([('Wi-Fi','network-wireless-symbolic','wifi'),('Bluetooth','bluetooth-symbolic','bluetooth'),('Sonido','audio-volume-high-symbolic','sound'),('Pantalla Android','display-brightness-symbolic','display')]):
   b=self.button(title,lambda b,p=page:self.async_android({'action':'settings','page':p},lambda r:self.destroy()),icon);b.set_hexpand(True);tiles.attach(b,index%2,index//2,1,1)
  self.control_front.pack_start(tiles,False,False,0);self.sliders={};self.slider_pending={};self.loading_sliders=True
  for title,action,icon in [('Volumen multimedia','volume','audio-volume-high-symbolic'),('Brillo del teléfono','brightness','display-brightness-symbolic')]:
   card=style(Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5),'hub-card');head=Gtk.Box(spacing=8);head.pack_start(image(name=icon,size=20),False,False,0);head.pack_start(label(title),True,True,0);card.pack_start(head,False,False,0);slider=Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,0,100,1);slider.set_value_pos(Gtk.PositionType.RIGHT);slider.set_digits(0);slider.set_sensitive(False);card.pack_start(slider,False,False,0);self.sliders[action]=slider;slider.connect('value-changed',lambda s,a=action:self.slider_changed(a,s));self.control_front.pack_start(card,False,False,0)
  appearance=Gtk.Box(spacing=8);appearance.pack_start(label('Modo oscuro · MacDesk y Android'),True,True,0);self.loading_theme=True;self.dark_switch=Gtk.Switch();self.dark_switch.set_active('dark' in self.hub.xfget('xsettings','/Net/ThemeName','').lower());self.dark_switch.set_sensitive(False);self.dark_switch.connect('notify::active',self.set_dark);appearance.pack_end(self.dark_switch,False,False,0);self.loading_theme=False;self.control_front.pack_start(appearance,False,False,0)
  actions=Gtk.Box(spacing=8);actions.pack_start(self.button('Apps Android',lambda b:self.hub.show_mode('choose'),'view-app-grid-symbolic'),True,True,0);actions.pack_start(self.button('Dock',lambda b:self.desktop_command(['xfce4-panel','--preferences=2']),'emblem-system-symbolic'),False,False,0);actions.pack_end(self.button('Pantalla',lambda b:self.desktop_command(['xfce4-display-settings']),'video-display-symbolic'),False,False,0);self.control_front.pack_start(actions,False,False,0)
  self.theme_detail=label('Consultando apariencia de Android…','hub-subtitle');self.control_front.pack_start(self.theme_detail,False,False,0)
  self.async_android({'action':'status'},self.got_status)
 def got_status(self,response):
  battery=response.get('battery');self.battery.set_text(f'Android · Batería {battery}%' + (' · Cargando' if response.get('charging') else '') if battery is not None else 'Android conectado')
  self.loading_sliders=True
  for action,slider in self.sliders.items():
   if response.get(action) is not None:slider.set_value(response[action]);slider.set_sensitive(True)
  self.loading_sliders=False
  if 'dark' in response:
   self.dark_switch.set_sensitive(True)
   local='dark' in self.hub.xfget('xsettings','/Net/ThemeName','').lower()
   self.theme_detail.set_text('MacDesk: '+('oscuro' if local else 'claro')+' · Android: '+('oscuro' if response['dark'] else 'claro'))
  else:self.theme_detail.set_text('Android no informó su apariencia; reconecta el puente.')
 def slider_changed(self,action,slider):
  if self.loading_sliders:return
  if action in self.slider_pending:GLib.source_remove(self.slider_pending.pop(action))
  def apply():
   self.slider_pending.pop(action,None)
   if self.get_visible():
    def applied(response):
     if response.get(action) is not None:
      self.loading_sliders=True;slider.set_value(response[action]);self.loading_sliders=False
    self.async_android({'action':action,'value':round(slider.get_value())},applied)
   return False
  self.slider_pending[action]=GLib.timeout_add(400,apply)
 def set_dark(self,switch,prop):
  if self.loading_theme:return
  dark=switch.get_active();switch.set_sensitive(False);self.status('Cambiando apariencia en MacDesk y Android…')
  def worker():
   error=None
   try:
    apply_global_dark(dark,lambda p:request(p,model=self.model),self.hub.xfget,self.hub.xfset,lambda value:atomic_json(self.model.root/'state/desktop-hub.json',value))
   except Exception as failure:error=str(failure)
   def complete():
    if not self.get_visible():return False
    self.loading_theme=True;switch.set_active('dark' in self.hub.xfget('xsettings','/Net/ThemeName','').lower());self.loading_theme=False;switch.set_sensitive(True);self.refresh_theme()
    self.theme_detail.set_text('MacDesk y Android: '+('oscuro' if dark else 'claro') if not error else 'No se pudo completar el cambio global.')
    self.status(error or '',bool(error));return False
   GLib.idle_add(complete)
  threading.Thread(target=worker,daemon=True).start()
 def notifications_ui(self):
  back=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=12);self.faces.add_named(back,'notifications')
  head=Gtk.Box(spacing=8);head.pack_start(self.button('Controles',self.show_controls,'go-previous-symbolic'),False,False,0);self.notification_refresh=self.button('Actualizar',self.load_notifications,'view-refresh-symbolic');head.pack_end(self.notification_refresh,False,False,0);back.pack_start(head,False,False,0)
  back.pack_start(label('Notificaciones','hub-title'),False,False,0)
  self.notification_count=label('Al abrir se consultan las notificaciones de Android.','hub-subtitle');self.notification_count.set_line_wrap(True);back.pack_start(self.notification_count,False,False,0)
  scroll=Gtk.ScrolledWindow();scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC);scroll.set_min_content_height(310);scroll.set_max_content_height(360);scroll.set_vexpand(True);back.pack_start(scroll,True,True,0)
  self.notification_items=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10);scroll.add(self.notification_items)
  self.notification_busy=False
 def show_notifications(self,button):
  if self.faces.flip_to('notifications'):self.load_notifications(None)
 def show_controls(self,button):self.faces.flip_to('controls')
 def load_notifications(self,button):
  if self.notification_busy:return
  self.notification_busy=True;self.notification_refresh.set_sensitive(False);self.notification_count.set_text('Consultando Android…')
  def failed():
   if self.get_visible():
    self.notification_busy=False;self.notification_refresh.set_sensitive(True);self.notification_count.set_text('No se pudo actualizar. Reconecta Android y pulsa Actualizar.')
   return False
  self.async_android({'action':'notifications'},self.got_notifications,failed)
 def got_notifications(self,response):
  self.notification_busy=False;self.notification_refresh.set_sensitive(True)
  for child in self.notification_items.get_children():child.destroy()
  apps={a['package']:a for a in self.model.catalog()};items=response.get('notifications',[])
  for item in items:
   app=apps.get(item['package']);card=style(Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6),'notification-card')
   head=Gtk.Box(spacing=8);head.pack_start(image(self.model.icon_path(app) if app else None,name='preferences-system-notifications-symbolic',size=24),False,False,0);head.pack_start(label(app['label'] if app else item['package'],'notification-app'),True,True,0)
   try:stamp=notification_time(item.get('timestamp'))
   except (ValueError,OverflowError,OSError):stamp=''
   head.pack_end(label(stamp,'hub-subtitle'),False,False,0);card.pack_start(head,False,False,0)
   for text,kind,lines in [(item.get('title',''),'notification-title',2),(item.get('text',''),'notification-body',5)]:
    if text:
     content=label(text,kind);content.set_line_wrap(True);content.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR);content.set_max_width_chars(38);content.set_ellipsize(Pango.EllipsizeMode.END);content.set_lines(lines);content.set_tooltip_text(text);card.pack_start(content,False,False,0)
   if app:
    open_button=self.button('Abrir app',lambda b,c=app['component']:self.android_launch(c),'go-next-symbolic');card.pack_start(open_button,False,False,0)
   self.notification_items.pack_start(card,False,False,0)
  if not items:self.notification_items.pack_start(label('No tienes notificaciones.','hub-subtitle'),False,False,0)
  summary=f'{len(items)} notificación'+('es' if len(items)!=1 else '')+' · Android'
  if response.get('truncated'):summary+=' · vista parcial; pulsa Actualizar'
  if response.get('unavailable'):summary+=' · algunas cambiaron mientras se consultaban'
  self.notification_count.set_text(summary);self.notification_items.show_all()
 def desktop_command(self,args):subprocess.Popen(args,start_new_session=True);self.destroy()

class HubApplication(Gtk.Application):
 def __init__(self,testing=False):
  super().__init__(application_id='org.macdesk.DesktopHub',flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE);self.model=HubModel();self.testing=testing;self.pending_selection=None
 def do_startup(self):
  Gtk.Application.do_startup(self);provider=Gtk.CssProvider();provider.load_from_data(CSS.encode());Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION+10)
 def do_command_line(self,command):
  args=command.get_arguments();mode=args[1] if len(args)>1 else 'apps'
  if mode not in ('apps','downloads','choose','control'):return 2
  if self.get_windows() and self.get_windows()[0].mode==mode:
   self.get_windows()[0].destroy();return 0
  self.show_mode(mode);return 0
 def show_mode(self,mode):
  for window in self.get_windows():window.destroy()
  window=HubWindow(self,mode);window.present()
 def xfget(self,channel,prop,default):
  if channel=='gnome':
   settings=Gio.Settings.new('org.gnome.desktop.interface');return settings.get_string(prop)
  p=subprocess.run(['xfconf-query','-c',channel,'-p',prop],text=True,capture_output=True)
  return p.stdout.strip() if p.returncode==0 else default
 def xfset(self,channel,prop,kind,value):
  if channel=='gnome':
   settings=Gio.Settings.new('org.gnome.desktop.interface')
   if not settings.set_string(prop,str(value)):raise RuntimeError('No se pudo cambiar la apariencia GTK')
   Gio.Settings.sync();return
  subprocess.run(['xfconf-query','-c',channel,'-p',prop,'-n','-t',kind,'-s',str(value)],check=True)

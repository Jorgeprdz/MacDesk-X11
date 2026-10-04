"""Shared data and validated Android bridge requests; no desktop dependencies."""
import hashlib,json,os,re,tempfile
from pathlib import Path

SETTINGS_PAGES={'wifi':'android.settings.WIFI_SETTINGS','bluetooth':'android.settings.BLUETOOTH_SETTINGS','sound':'android.settings.SOUND_SETTINGS','display':'android.settings.DISPLAY_SETTINGS','battery':'android.settings.BATTERY_SAVER_SETTINGS','settings':'android.settings.SETTINGS'}
DEFAULT_PACKAGES=['com.whatsapp','com.google.android.gm','com.android.chrome','com.google.android.apps.maps','com.sec.android.gallery3d','com.canva.editor','com.openai.chatgpt']

def atomic_json(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 fd,temp=tempfile.mkstemp(prefix=path.name+'.',dir=path.parent)
 try:
  with os.fdopen(fd,'w') as out:json.dump(value,out,ensure_ascii=False)
  os.replace(temp,path)
 finally:
  if os.path.exists(temp):os.unlink(temp)

def validate_request(request,catalog):
 if not isinstance(request,dict):raise ValueError('Solicitud inválida')
 action=request.get('action')
 if action=='launch':
  if request.get('component') not in {a['component'] for a in catalog}:raise ValueError('Aplicación no disponible; actualiza la lista')
 elif action=='settings':
  if request.get('page') not in SETTINGS_PAGES:raise ValueError('Ajuste desconocido')
 elif action in ('volume','brightness'):
  value=request.get('value')
  if not isinstance(value,int) or isinstance(value,bool) or not 0<=value<=100:raise ValueError('El valor debe estar entre 0 y 100')
 elif action=='open':
  name=request.get('path','')
  root=Path('/sdcard/Download')
  if not isinstance(name,str) or '\x00' in name or '\n' in name:raise ValueError('Ruta inválida')
  try:Path(name).relative_to(root)
  except ValueError:raise ValueError('Solo se pueden abrir archivos de Descargas')
  if '..' in Path(name).parts:raise ValueError('Ruta inválida')
 elif action=='dark_mode':
  has_enabled='enabled' in request;has_mode='mode' in request
  if has_enabled==has_mode:raise ValueError('Selecciona un solo modo de apariencia')
  if has_enabled and not isinstance(request['enabled'],bool):raise ValueError('Modo oscuro inválido')
  if has_mode and request['mode'] not in ('yes','no','auto','custom_schedule','custom_bedtime'):raise ValueError('Modo Android inválido')
 elif action not in ('catalog','status','notifications'):raise ValueError('Acción desconocida')
 return request

class HubModel:
 def __init__(self,root=None,applications_dir=None,downloads=None):
  self.root=Path(root or os.environ.get('MACDESK_ROOT',Path.home()/'MacDesk-V6'))
  self.state=self.root/'state/android-apps'
  self.applications=Path(applications_dir or Path.home()/'.local/share/applications')
  self.downloads=Path(downloads or '/mnt/s25/Download')
 def catalog(self):
  try:return sorted(json.loads((self.state/'catalog.json').read_text())['apps'],key=lambda a:a['label'].casefold())
  except (FileNotFoundError,ValueError,KeyError):return []
 def selected_packages(self):
  try:return json.loads((self.state/'selected.json').read_text())['packages']
  except (FileNotFoundError,ValueError,KeyError):
   available={a['package'] for a in self.catalog()}
   return [p for p in DEFAULT_PACKAGES if p in available][:6]
 def save_selection(self,packages):
  known={a['package'] for a in self.catalog()};packages=list(dict.fromkeys(packages))
  if not set(packages)<=known:raise ValueError('Hay aplicaciones desconocidas en la selección')
  atomic_json(self.state/'selected.json',{'version':1,'packages':packages})
 def selected_apps(self):
  selected=set(self.selected_packages());return [a for a in self.catalog() if a['package'] in selected]
 def icon_path(self,app):
  path=(self.state/app['icon']).resolve()
  if not path.is_relative_to((self.state/'icons').resolve()):raise ValueError('Icono fuera del catálogo')
  return path
 def sync_launchers(self):
  self.applications.mkdir(parents=True,exist_ok=True);keep=set()
  for app in self.selected_apps():
   key=hashlib.sha256(app['component'].encode()).hexdigest()[:16];name='macdesk-android-'+key+'.desktop';keep.add(name)
   label=app['label'].replace('\n',' ').replace('\r',' ')
   component=app['component']
   if not re.fullmatch(r'[A-Za-z0-9_.$]+/[A-Za-z0-9_.$]+',component):continue
   text=f'[Desktop Entry]\nType=Application\nName={label} (Android)\nComment=Abrir en Android\nExec={self.root}/scripts/macdesk-desktop-hub launch {component}\nIcon={self.icon_path(app)}\nTerminal=false\nStartupNotify=false\nCategories=Utility;\n'
   (self.applications/name).write_text(text)
  for file in self.applications.glob('macdesk-android-*.desktop'):
   if file.name not in keep:file.unlink()
 def recent_downloads(self,limit=120):
  try:
   entries=[];base=self.downloads.resolve()
   for path in self.downloads.iterdir():
    try:
     if not path.name.startswith('.') and path.resolve().is_relative_to(base):entries.append((path.stat().st_mtime,path))
    except OSError:continue
   return [p for stamp,p in sorted(entries,key=lambda item:item[0],reverse=True)[:limit]]
  except OSError:return []
 def android_download_path(self,path):
  path=Path(path).resolve();base=self.downloads.resolve()
  if not path.is_relative_to(base) or not path.exists():raise ValueError('El archivo ya no está disponible en Descargas')
  return str(Path('/sdcard/Download')/path.relative_to(base))

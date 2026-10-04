"""Run under Xvfb or a disposable desktop. Uses synthetic notification content."""
import json,sys,tempfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/lib'))
import macdesk_hub as hub
from macdesk_hub_model import HubModel
from gi.repository import Gtk,GLib

calls=[]
def android(payload,**kwargs):
 calls.append(payload)
 if payload['action']=='notifications':return {'ok':True,'notifications':[{'package':'com.example','title':'Mensaje <literal>','text':'Contenido de prueba','timestamp':1700000000000}],'total':1,'unavailable':0,'truncated':False}
 if payload['action']=='dark_mode':return {'ok':True,'dark':payload.get('enabled',False),'night_mode':'yes' if payload.get('enabled') else 'no','previous_mode':'auto'}
 return {'ok':True,'volume':45,'brightness':60,'battery':50,'dark':False,'night_mode':'auto'}
hub.request=android

def flush(seconds=.15):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  while GLib.MainContext.default().pending():GLib.MainContext.default().iteration(False)
  time.sleep(.005)

with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);state=root/'state/android-apps';state.mkdir(parents=True)
 (state/'catalog.json').write_text(json.dumps({'apps':[]}))
 app=hub.HubApplication(testing=True);app.set_application_id('org.macdesk.FlipVerification');app.model=HubModel(root,root/'launchers',root/'Downloads')
 values={('xsettings','/Net/ThemeName'):'GoldenGate-Light',('xsettings','/Net/IconThemeName'):'BigSur',('xfwm4','/general/theme'):'GoldenGate-Light'}
 app.xfget=lambda c,p,d:values.get((c,p),d)
 app.xfset=lambda c,p,t,v:values.__setitem__((c,p),v)
 app.register(None);app.show_mode('control');flush(.3);w=app.get_windows()[0]
 assert hasattr(w,'faces'),'control center does not have flip faces'
 assert w.faces.get_visible_child_name()=='controls'
 w.show_notifications(None);flush(.1);assert w.faces.tick_id,'flip animation never started'
 flush(.5);assert w.faces.get_visible_child_name()=='notifications';assert w.faces.tick_id==0,'animation keeps running at rest'
 assert len(w.notification_items.get_children())>=1
 assert w.notification_count.get_text().startswith('1 ')
 assert calls.count({'action':'notifications'})==1
 w.show_controls(None);flush(.5);assert w.faces.get_visible_child_name()=='controls'
 w.dark_switch.set_active(True);flush(.4)
 assert {'action':'dark_mode','enabled':True} in calls
 assert values['xsettings','/Net/ThemeName']=='GoldenGate-Dark'
 assert w.get_style_context().has_class('dark')
 w.show_notifications(None);w.destroy();flush(.5)
 assert w.faces.tick_id==0,'closing during flip leaves frame callback alive'
 print('PASS: flip/back, actual animation stops, notification cards, global switch, close during animation')

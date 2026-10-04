import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/lib'))
try:
 from macdesk_appearance import apply_global_dark
except ImportError:apply_global_dark=None

class AppearanceTests(unittest.TestCase):
 def setup_callbacks(self,fail=None):
  self.desktop={('xsettings','/Net/ThemeName'):'GoldenGate-Light',('xsettings','/Net/IconThemeName'):'BigSur',('xfwm4','/general/theme'):'GoldenGate-Light',('gnome','color-scheme'):'default',('gnome','gtk-theme'):'GoldenGate-Light'}
  self.android_mode='auto';self.saved=None;self.fail_property=fail
  def android(payload):
   previous=self.android_mode;self.android_mode=payload.get('mode','yes' if payload.get('enabled') else 'no')
   return {'previous_mode':previous,'dark':self.android_mode=='yes','night_mode':self.android_mode}
  def get(c,p,default):return self.desktop.get((c,p),default)
  def set_value(c,p,t,v):
   if self.fail_property==(c,p):self.fail_property=None;raise RuntimeError('desktop write failed')
   self.desktop[c,p]=v
  def save(value):self.saved=value
  return android,get,set_value,save
 def test_desktop_icon_family_survives_dark_mode(self):
  from macdesk_appearance import desktop_values
  for dark,current,expected in [(True,"MacDesk-Desktop","MacDesk-Desktop-dark"),(False,"MacDesk-Desktop-dark","MacDesk-Desktop")]:
   self.assertIn(("xsettings","/Net/IconThemeName",expected),desktop_values(dark,current))
 def test_both_systems_and_macos_theme_family(self):
  self.assertIsNotNone(apply_global_dark,'global appearance missing')
  cb=self.setup_callbacks();apply_global_dark(True,*cb)
  self.assertEqual(self.desktop['gnome','color-scheme'],'prefer-dark');self.assertEqual(self.android_mode,'yes');self.assertEqual(self.desktop['xsettings','/Net/ThemeName'],'GoldenGate-Dark')
  self.assertEqual(self.desktop['xfwm4','/general/theme'],'GoldenGate-Dark');self.assertEqual(self.saved,{'dark':True})
  apply_global_dark(False,*cb);self.assertEqual(self.android_mode,'no');self.assertEqual(self.desktop['xsettings','/Net/IconThemeName'],'BigSur')
 def test_local_failure_restores_android_auto_schedule(self):
  self.assertIsNotNone(apply_global_dark,'global appearance missing')
  cb=self.setup_callbacks(('xfwm4','/general/theme'));before=dict(self.desktop)
  with self.assertRaisesRegex(RuntimeError,'desktop write failed'):apply_global_dark(True,*cb)
  self.assertEqual(self.android_mode,'auto');self.assertEqual(self.desktop,before);self.assertIsNone(self.saved)
 def test_android_failure_does_not_change_desktop(self):
  self.assertIsNotNone(apply_global_dark,'global appearance missing')
  cb=self.setup_callbacks();before=dict(self.desktop)
  def unavailable(payload):raise RuntimeError('Android desconectado')
  with self.assertRaisesRegex(RuntimeError,'desconectado'):apply_global_dark(True,unavailable,*cb[1:])
  self.assertEqual(self.desktop,before);self.assertIsNone(self.saved)
class AndroidVerificationTests(unittest.TestCase):
 def test_verification_failure_restores_previous_android_mode(self):
  try:
   from macdesk_appearance import change_android_mode
  except ImportError:change_android_mode=None
  self.assertIsNotNone(change_android_mode,'verified Android change missing')
  state={'mode':'auto','reads':0}
  def read():
   state['reads']+=1
   if state['reads']==2:raise RuntimeError('verification unavailable')
   return {'dark':False,'night_mode':state['mode']}
  def write(mode):state['mode']=mode
  with self.assertRaisesRegex(RuntimeError,'verification unavailable'):change_android_mode('yes',read,write)
  self.assertEqual(state['mode'],'auto')
if __name__=='__main__':unittest.main()

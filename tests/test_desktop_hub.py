import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/lib'))
from macdesk_hub_model import HubModel, validate_request
class HubTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.apps=self.root/'launchers';self.downloads=self.root/'Downloads';self.downloads.mkdir()
  state=self.root/'state/android-apps';state.mkdir(parents=True)
  (state/'catalog.json').write_text(json.dumps({'apps':[{'package':'com.whatsapp','component':'com.whatsapp/.Main','label':'WhatsApp','icon':'icons/w.png'},{'package':'com.hidden','component':'com.hidden/.Main','label':'Otra','icon':'icons/o.png'}]}))
  self.model=HubModel(self.root,self.apps,self.downloads)
 def tearDown(self):self.temp.cleanup()
 def test_selection_saved_and_only_selected_launchers_generated(self):
  self.model.save_selection(['com.whatsapp']);self.assertEqual(self.model.selected_packages(),['com.whatsapp'])
  self.model.sync_launchers();files=list(self.apps.glob('macdesk-android-*.desktop'));self.assertEqual(len(files),1);self.assertIn('com.whatsapp/.Main',files[0].read_text())
  self.model.save_selection([]);self.model.sync_launchers();self.assertEqual(list(self.apps.glob('macdesk-android-*.desktop')),[])
 def test_unknown_packages_rejected_and_empty_selection_survives_reload(self):
  with self.assertRaises(ValueError):self.model.save_selection(['com.fake'])
  self.model.save_selection([]);self.assertEqual(HubModel(self.root,self.apps,self.downloads).selected_packages(),[])
 def test_downloads_recent_order_and_hidden_files(self):
  import os
  for name,stamp in [('old.pdf',10),('new.jpg',20),('.hidden',30)]:
   p=self.downloads/name;p.write_text('test');os.utime(p,(stamp,stamp))
  self.assertEqual([p.name for p in self.model.recent_downloads()],['new.jpg','old.pdf'])
 def test_only_download_files_can_be_sent_to_android(self):
  good=self.downloads/'quote with spaces.pdf';good.write_text('file');self.assertEqual(self.model.android_download_path(good),'/sdcard/Download/quote with spaces.pdf')
  with self.assertRaises(ValueError):self.model.android_download_path(self.root/'secret')
  outside=self.root/'private';outside.write_text('secret');(self.downloads/'escape').symlink_to(outside)
  with self.assertRaises(ValueError):self.model.android_download_path(self.downloads/'escape')
 def test_requests_validate_component_and_control_ranges(self):
  catalog=self.model.catalog()
  validate_request({'action':'launch','component':'com.whatsapp/.Main'},catalog)
  for bad in [{'action':'launch','component':'evil/;sh'},{'action':'settings','page':'arbitrary'},{'action':'volume','value':101},{'action':'brightness','value':-1},{'action':'exec','command':'rm'}]:
   with self.assertRaises(ValueError):validate_request(bad,catalog)
if __name__=='__main__':unittest.main()

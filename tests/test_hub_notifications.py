import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/lib'))
from macdesk_hub_model import validate_request
try:
 from macdesk_notifications import parse_notification, notification_snapshot
except ImportError:
 parse_notification=notification_snapshot=None

DUMP='''NotificationRecord(0x123: pkg=com.example)
  key=0|com.example|4|null|12345
  flags=ONGOING_EVENT
  groupKey=0|com.example|g:messages
    when=1700000000000/1700000000000
    extras={
        android.title=String (Aviso <sin markup>)
        android.text=String (Vista corta)
        android.bigText=String (Texto largo\nsegunda línea (detalle))
    }
  mUpdateTimeMs=1700000005000(2023-11-14)
  mSensitiveContent=false
'''
class NotificationTests(unittest.TestCase):
 def test_reads_multiline_text_and_preserves_literal_markup(self):
  self.assertIsNotNone(parse_notification,'notification parser missing')
  n=parse_notification('0|com.example|4|null|12345',DUMP)
  self.assertEqual(n['title'],'Aviso <sin markup>')
  self.assertEqual(n['text'],'Texto largo\nsegunda línea (detalle)')
  self.assertEqual(n['timestamp'],1700000005000)
 def test_sensitive_content_is_not_exposed(self):
  self.assertIsNotNone(parse_notification,'notification parser missing')
  n=parse_notification('0|com.example|4|null|12345',DUMP.replace('mSensitiveContent=false','mSensitiveContent=true'))
  self.assertNotIn('Texto largo',n['text']);self.assertIn('protegido',n['text'])
 def test_disappearing_notification_and_other_profiles(self):
  self.assertIsNotNone(notification_snapshot,'notification reader missing')
  keys='0|com.example|4|null|12345\n10|com.work|5|null|12346\n0|com.gone|6|null|12347\n'
  def read(key):return DUMP if 'com.example' in key else 'No notification matching'
  r=notification_snapshot(keys,read,user_id=0)
  self.assertEqual(len(r['notifications']),1);self.assertEqual(r['unavailable'],1)
 def test_new_requests_validate_boolean_and_restore_mode(self):
  for p in [{'action':'notifications'},{'action':'dark_mode','enabled':True},{'action':'dark_mode','mode':'auto'}]:
   try:validate_request(p,[])
   except ValueError as e:self.fail(str(e))
  for p in [{'action':'dark_mode','enabled':'yes'},{'action':'dark_mode','mode':'evil;cmd'},{'action':'dark_mode','enabled':True,'mode':'auto'}]:
   with self.assertRaises(ValueError):validate_request(p,[])
class ResponseExpiryTests(unittest.TestCase):
 def test_unconsumed_response_is_deleted(self):
  import tempfile
  try:
   from macdesk_notifications import expire_response
  except ImportError:expire_response=None
  self.assertIsNotNone(expire_response,'response expiry missing')
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'response.json';path.write_text('private synthetic notification')
   expire_response(path,delay=0)
   self.assertFalse(path.exists())
 def test_consumed_response_can_expire_without_error(self):
  import tempfile
  try:
   from macdesk_notifications import expire_response
  except ImportError:expire_response=None
  self.assertIsNotNone(expire_response,'response expiry missing')
  with tempfile.TemporaryDirectory() as tmp:expire_response(Path(tmp)/'already-read.json',delay=0)
if __name__=='__main__':unittest.main()

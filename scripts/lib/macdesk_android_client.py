import base64,json,os,time,uuid
from pathlib import Path
from macdesk_hub_model import HubModel,validate_request

def request(payload,timeout=20,model=None):
 model=model or HubModel();validate_request(payload,model.catalog())
 request_id=uuid.uuid4().hex
 message=('ANDROID\t'+request_id+'\t'+base64.b64encode(json.dumps(payload).encode()).decode()+'\n').encode()
 if len(message)>4096:raise ValueError('Solicitud demasiado grande')
 try:
  fd=os.open(model.root/'state/host-app.fifo',os.O_WRONLY|os.O_NONBLOCK)
  try:
   if os.write(fd,message)!=len(message):raise RuntimeError('No se pudo enviar la solicitud completa')
  finally:os.close(fd)
 except OSError as e:raise RuntimeError('El puente Android no está activo. Reinicia MacDesk.') from e
 result=model.state/'responses'/(request_id+'.json');deadline=time.monotonic()+timeout
 while time.monotonic()<deadline:
  try:
   response=json.loads(result.read_text());result.unlink()
   if not response.get('ok'):raise RuntimeError(response.get('error','Android no respondió'))
   return response
  except FileNotFoundError:time.sleep(.08)
 raise RuntimeError('Android tardó demasiado en responder; inténtalo de nuevo.')

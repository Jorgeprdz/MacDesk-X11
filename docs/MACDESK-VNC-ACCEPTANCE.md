# MacDesk V6 VNC — evidencia de aceptación

Fecha: 2026-08-22

## Resultado servidor

```text
DISPLAY=:2
VNC_IMPLEMENTATION=X0tigervnc
HOST=100.108.132.112
PORT=5902
SECURITY=VncAuth
PASSWORD_FILE=/root/.vnc/passwd
PASSWORD_MODE=0600
TAILSCALE_BIND=PASS
LAN_WILDCARD=NO
SECOND_X_SERVER_CREATED=NO
SECOND_XFCE_CREATED=NO
READY_FOR_AVNC=YES
```

## Evidencia ejecutada

- `x0vncserver` sin `-fg` reprodujo el fallo: anunció el puerto 5904, terminó
  con código 0 y después no quedaron proceso ni listener.
- `x0vncserver -fg` mantuvo proceso y listener temporal en localhost:5904.
  La prueba se cerró limpiamente.
- El servicio definitivo usa el motor `X0tigervnc` en foreground dentro del
  PRoot persistente y enlaza exclusivamente `100.108.132.112:5902`.
- La negociación RFB devolvió versión 3.8 y únicamente el security type 2
  (`VncAuth`). No se envió ni registró la contraseña.
- `127.0.0.1:5902` y la dirección Wi-Fi del S25 rechazaron conexiones.
- Un segundo `macdesk-vnc-start` conservó un único proceso VNC.
- `macdesk-vnc-stop` retiró proceso y puerto sin cambiar los PID existentes de
  Termux:X11, XFCE, XFWM o Plank; el arranque posterior pasó de nuevo.
- Tras la espera de estabilidad, proceso, listener y sesión `:2` continuaron
  sanos.
- AVNC mostró y controló las mismas ventanas, XFCE y Plank antes y después de
  un ciclo remoto stop/start.
- Con el monitor externo desconectado físicamente, Android dejó de publicar el
  display externo, pero Termux:X11, `:2`, XFCE, XFWM, Plank y X0tigervnc
  conservaron una sola instancia y sus PID.
- La Galaxy Tab siguió conectada mediante Tailscale y mostró el mismo
  framebuffer 1920x1080 sin monitor.
- El teclado AVNC funcionó globalmente. WhatsApp y ChatGPT requirieron bridges
  XTEST exclusivos del modo remoto; ambos pasaron la prueba manual antes y
  después de un ciclo stop/start. Los bridges locales permanecieron activos.

## Resultado monitorless

```text
EXTERNAL_MONITOR_PRESENT=NO
MONITORLESS_DESKTOP=PASS
SAME_X_DISPLAY=PASS
SAME_XFCE_SESSION=PASS
SAME_WINDOWS=PASS
BIDIRECTIONAL_CONTROL=PASS
WHATSAPP_VNC_INPUT=PASS
CHATGPT_VNC_INPUT=PASS
SECOND_X_SERVER_CREATED=NO
SECOND_XFCE_CREATED=NO
LAN_WILDCARD=NO
PHASE_5=PASS
```

La pantalla apagada del S25, clipboard y combinaciones remotas Alt+Tab/Super
no formaron parte de esta fase y permanecen sin certificar.

## Operación

```text
/data/data/com.termux/files/home/MacDesk-V6/scripts/macdesk-vnc-start
/data/data/com.termux/files/home/MacDesk-V6/scripts/macdesk-vnc-status
/data/data/com.termux/files/home/MacDesk-V6/scripts/macdesk-vnc-stop
```

La validación visual desde AVNC fue completada por el usuario. El servidor
queda activo sobre el mismo escritorio MacDesk.

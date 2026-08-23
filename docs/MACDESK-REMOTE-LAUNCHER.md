# MacDesk Remote — Android launcher

Fecha de validación: 2026-08-22

## Arquitectura

`com.macdesk.remote` es una aplicación Android independiente de MacDesk y de
Termux:X11. Usa el servicio oficial `com.termux.RUN_COMMAND` para ejecutar:

- `scripts/macdesk-remote-app-control start`
- `scripts/macdesk-remote-app-control stop`

El controlador reutiliza los entrypoints VNC existentes. No modifica ni
reemplaza `macdesk`, `macdesk-stop` o el APK de Termux:X11.

## Comportamiento

- Al tocar el icono, comprueba `100.108.132.112:5902`.
- Si Remote está apagado, inicia MacDesk mediante su entrypoint normal sólo
  cuando la sesión realmente no existe y después inicia Remote Sharing.
- Si Remote está activo, muestra el estado y no duplica procesos.
- **Detener Remote** apaga sólo X0tigervnc y los bridges remotos. MacDesk,
  Termux:X11, XFCE, XFWM, Plank y las ventanas permanecen vivos.

## Seguridad

- Bind VNC: `100.108.132.112:5902` exclusivamente.
- Seguridad: `VncAuth`.
- Redimensionado seguro: `UseSHM=0` evita el crash MIT-SHM al conectar o desconectar el monitor.
- La app no contiene ni muestra la contraseña VNC.
- Permisos Android: `INTERNET` y `com.termux.permission.RUN_COMMAND`.
- Keystore y artefactos locales están excluidos mediante `.gitignore`.

## Evidencia

```text
ANDROID_PACKAGE=com.macdesk.remote
LAUNCHER_ACTIVITY=com.macdesk.remote/.MainActivity
APP_STATUS=REMOTE ACTIVO
TERMUX_RUN_COMMAND_PERMISSION=GRANTED
VNC_BIND=100.108.132.112:5902_ONLY
LAN_WILDCARD=NO
DISPLAY=:2
XFCE_SESSION_COUNT=1
XFWM_COUNT=1
PLANK_COUNT=1
X0TIGERVNC_COUNT=1
RESIZE_MONITOR_RECONNECT=PASS
USE_SHM=0
STOP_LEAVES_MACDESK_RUNNING=PASS
START_IDEMPOTENCE=PASS
```

## Rollback

Desinstalar sólo el launcher:

```sh
adb -s emulator-5554 uninstall com.macdesk.remote
```

Esto no elimina MacDesk ni la configuración/contraseña VNC. Para retirar
también el código fuente del launcher se puede borrar únicamente
`android/macdesk-remote-launcher/` y `scripts/macdesk-remote-app-control`.

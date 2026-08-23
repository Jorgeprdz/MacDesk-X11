# MacDesk Remote launcher

Aplicación Android independiente para controlar Remote Sharing de MacDesk V6.

- Al abrirse comprueba `100.108.132.112:5902`.
- Si Remote está apagado, usa el servicio oficial `com.termux.RUN_COMMAND` para iniciar el entrypoint normal de MacDesk cuando haga falta y después `macdesk-vnc-start`.
- Si Remote ya está activo, sólo muestra su estado.
- **Detener Remote** ejecuta `macdesk-vnc-stop`; no detiene Termux:X11, XFCE, Plank ni las aplicaciones abiertas.
- No modifica Termux:X11 ni los launchers existentes.

Construcción local:

```sh
./build.sh
```

El APK queda en `build/MacDesk-Remote.apk`. El keystore local de actualización no se versiona.

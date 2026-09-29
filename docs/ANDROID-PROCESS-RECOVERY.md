# Recuperación de procesos Android — 29 de septiembre de 2026

## Causa demostrada

Android terminó Codex y el escritorio mediante su control de procesos secundarios.
El búfer de eventos contiene `am_kill` con motivo `Trimming phantom processes`:

- 28 de septiembre, 22:45:46 (UTC−06): PRoot, Codex y codex-code-mode-host.
- 28 de septiembre, 22:49:15 (UTC−06): Termux:X11, PRoot, dbus-run-session,
  dbus-daemon y xfce4-session.

El límite reportado por ActivityManager era 32 procesos. Los UIDs actuales de
Termux y Termux:X11 eran diferentes (10532 y 10571). El antiguo problema de
force-stop con UID compartido no explica estos eventos.

## Ajuste aplicado

Con ADB conectado al teléfono:

```sh
adb shell settings put global settings_enable_monitor_phantom_procs false
adb shell settings get global settings_enable_monitor_phantom_procs
```

El segundo comando debe devolver `false`. Esto equivale funcionalmente a activar
**Disable child process restrictions** en las opciones de desarrollador: se
suprime ese mecanismo de terminación de procesos. Es un ajuste global de Android,
no una excepción exclusiva para MacDesk. No evita otras causas de cierre como
agotamiento de memoria o una detención explícita de la aplicación.

Valor anterior: no configurado (`null`). Para restaurarlo:

```sh
adb shell settings delete global settings_enable_monitor_phantom_procs
```

Referencias: [incidencia oficial de Termux](https://github.com/termux/termux-app/issues/2366)
y [documentación del mantenedor sobre procesos secundarios](https://github.com/agnostic-apollo/Android-Docs/blob/master/en/docs/apps/processes/phantom-cached-and-empty-processes.md#commands-for-android-12l-13-and-higher).

## Cambios del ciclo de vida

- `macdesk-stop` valida los argumentos del proceso antes de enviar TERM. Para
  XFCE verifica además que desciende del PRoot de MacDesk. Un PID ajeno se rechaza
  conservando el archivo para diagnóstico.
- Se detiene primero el supervisor, que de otro modo podría recrear un guardián
  durante el apagado. Se cierra XFCE antes que PRoot; TERM dirigido solamente a
  PRoot no cerró la sesión en este dispositivo.
- Se comprueba la identidad por hora de creación del proceso durante la espera.
  No se escala a SIGKILL; un proceso que no termina produce error y conserva su
  estado. La comprobación shell no es una garantía atómica basada en pidfd.
- Se elimina el sondeo global de Firefox que podía seleccionar un navegador ajeno.
  Las aplicaciones del escritorio pertenecen al ciclo de vida de su sesión.
- Antes de iniciar un nuevo PRoot se invalidan los registros de salud anteriores.
  Un PASS antiguo ya no permite anunciar que la sesión nueva está lista.

## Evidencia y límites

La prueba de reinicio del 29 de septiembre, 05:12:24–05:12:52 UTC, comprobó el
apagado, el launcher normal, una ventana X11 real y un nuevo registro con X11,
D-Bus, XFCONF, XFCE, XFWM, panel, ajustes y escritorio en PASS. Codex permaneció
vivo. Además, entre 05:14:31 y 05:19:31 UTC, once muestras confirmaron
las mismas identidades de proceso de Codex/XFCE/XFWM y heartbeat fresco
X11/XFWM/D-Bus en PASS. Es una prueba de estabilidad de cinco minutos, no
una certificación de uso prolongado ni de todas las funciones. Los registros detallados se conservan fuera del repositorio en
`/workspace/macdesk-maintenance/`.

Una segunda sesión PRoot no consiguió autenticarse al bus de la sesión gráfica.
Las consultas de salud ejecutadas dentro de la sesión sí funcionan. Una ventana
X11 externa es una prueba independiente; no convierte la consulta externa de
D-Bus en PASS. Esta limitación debe resolverse o respetarse en las futuras
integraciones entre el host y el escritorio.

La desconexión de ADB durante un sondeo no significa que XFCE murió: verificar
los PIDs, su hora de creación y la frescura del heartbeat local. Las pruebas
físicas de DeX, teclado y reconexión del monitor siguen pendientes.

## Pruebas de regresión

```sh
python3 tests/test-stop-owned-processes.py
python3 tests/test-launcher-stale-health.py
bash tests/test-xfce-startup-contract.sh
bash tests/test-guest-repo-paths.sh
```

Los casos nuevos verifican que un PID ajeno sobreviva al apagado, incluso si
sus argumentos mencionan la ruta de un guardián, que un guardián propio termine
y que un nuevo launcher fallido no reutilice un PASS anterior.

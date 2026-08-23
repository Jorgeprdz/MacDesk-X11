# MacDesk V6 — VNC de la sesión existente

## Arquitectura

`X0tigervnc` comparte directamente el framebuffer del `DISPLAY=:2` ya creado
por Termux:X11. No inicia `Xtigervnc`, `Xvnc`, Xorg, XFCE, XFWM ni Plank.

La escucha queda limitada a `100.108.132.112:5902` mediante el parámetro
`interface`; se deshabilita IPv6 para impedir un listener adicional. La
autenticación es `VncAuth` con `/root/.vnc/passwd` en modo `0600`. El
portapapeles VNC permanece desactivado inicialmente.

## Causa raíz del intento 5903

`x0vncserver` inicia su motor en segundo plano cuando no recibe `-fg` y termina
con éxito después de anunciar el servidor. Debian se ejecuta mediante PRoot con
`--kill-on-exit`, por lo que al salir el wrapper se elimina el `X0tigervnc`
daemonizado. Esto explica que el mensaje “New X0tigervnc server” apareciera en
`/tmp/macdesk-x0vnc.log` aunque después no existieran proceso ni listener.

La reproducción controlada confirmó:

- wrapper sin `-fg`: exit 0, proceso ausente y puerto ausente;
- wrapper con `-fg`: proceso y `127.0.0.1:5904` permanecieron activos;
- `DISPLAY=:2`, XTEST y DAMAGE funcionan sin `XAUTHORITY`;
- `DBUS_SESSION_BUS_ADDRESS` pertenece a XFCE, pero no es requisito de
  `X0tigervnc`.

El wrapper Debian 1.15 además rechaza `AcceptCutText` y `SendCutText` para el
modo scraping. Los scripts invocan directamente el motor oficial
`X0tigervnc`, en primer plano dentro del proceso PRoot persistente, para aplicar
todos los parámetros requeridos.

## Operación

```text
scripts/macdesk-vnc-start
scripts/macdesk-vnc-status
scripts/macdesk-vnc-stop
```

`start` y `stop` administran sólo un proceso cuyo ejecutable, DISPLAY, puerto,
interfaz, autenticación y PasswordFile coinciden exactamente. No utilizan
`pkill -f` ni alteran los scripts normales `macdesk`, `macdesk-stop` o
`macdesk-resume`.

## Entrada remota en aplicaciones Chromium

AVNC entrega el teclado mediante el dispositivo XTEST. Los bridges locales de
compatibilidad de WhatsApp y ChatGPT escuchan el teclado Lorie de Termux:X11.
Por eso Remote Mode agrega dos procesos marcados y exclusivos que reutilizan
el bridge existente sobre XTEST device 5: puerto de depuración 9225 para
WhatsApp y 9226 para ChatGPT.

La configuración global del teclado y los bridges locales no se modifican.
`macdesk-vnc-stop` elimina únicamente los procesos que contienen los
marcadores remotos exactos.

## AVNC

```text
Host: 100.108.132.112
Port: 5902
Security: VncAuth
Desktop esperado: SAME_EXISTING_MACDESK
```

La contraseña nunca se incluye en scripts, logs, documentación ni URI.

# MacDesk Smart Desktop — implementación y validación

29 septiembre 2026. Ampliación incremental sobre el baseline recuperado, no
reescritura. **No es una certificación de todos los criterios de los anexos.**

## Scope encontrado

Android → Termux → Termux:X11 `:2` → PRoot Debian 13 → un bus D-Bus →
XFCE 4.20/xfwm4 → panel, Plank, Nautilus 48.3. Existen supervisores de salud,
entrada y geometría, VNC, integración `/sdcard`, launchers y preferencias X11.
No existía núcleo compartido. El teclado actual neutraliza Super por un problema
histórico DeX; los guardianes de entrada/Plank consultan cada 250/500 ms.

Verificados: Python, X11 tools, GJS, GTK3, Evince, GStreamer y libarchive.
No disponibles: Python gi/dbus/Xlib, ffmpeg/ffprobe, pdftoppm, ImageMagick,
inotifywait y file en el PATH guest auditado. Sushi 46 ya proporciona SPACE en
Nautilus, con salida por inactividad a los 12 segundos salvo SUSHI_PERSIST.

## Arquitectura y seguridad

`scripts/lib/macdesk/`: context, profiles, snap, preview, continuity, memory,
xevents, core, cli y common. Un Python residente, sin HTTP ni nuevos puertos.
X11 usa libX11/ctypes con espera bloqueante; resize se agrupa con debounce.
ADB se consulta al invalidar contexto y como fallback cada **60 s mínimo**.
No hay API fiable de lifecycle/low-memory Android disponible en este guest:
la presión puede comunicarse mediante hook; no se presenta como automática.

El socket está en `~/.config/macdesk/runtime/` (0700), socket y capacidad
efímera 0600. La capacidad evita la inconsistencia real de SO_PEERCRED entre
instancias PRoot. No permite ejecutar comandos arbitrarios ni registrar PIDs
externos. Solo se terminan grupos de helpers creados por el núcleo con
`start_new_session=True`; jamás se trima XFCE/X11 ni aplicaciones del usuario.

Logs rotados en `~/.local/state/macdesk/`: núcleo 128 KiB × 3; comandos por
módulo 64 KiB × 2. No se registra contenido del clipboard ni archivos leídos.
Los informes de salud runtime dejan de versionarse; permanecen en disco.

## Comandos

Desde Termux, usar el launcher existente:

```sh
macdesk diagnostics
macdesk mode auto                  # o phone, tablet, desktop, remote
macdesk display list
macdesk display bind               # presentar Activity en destino descubierto
macdesk memory
macdesk memory ui                  # snapshot GTK; sin timer al cerrarse
macdesk memory trim
macdesk snap left                  # ventana activa
macdesk snap menu                  # selector efímero
macdesk quicklook '/sdcard/Download/archivo con espacios.pdf'
macdesk open-android 'https://example.org'
macdesk share '/sdcard/Download/archivo.pdf'
macdesk storage
macdesk android-status
macdesk event refresh              # invalidar contexto Android tras un hook
macdesk event low-memory           # también critical-memory
```

Dentro de XFCE se instalan `macdesk-mode`, `macdesk-snap`, `macdesk-quicklook`,
`macdesk-memory`, `macdesk-open-android`, `macdesk-share`, `macdesk-core`.
El entrypoint completo es `python3 /root/MacDesk-V6/scripts/macdesk-smart`.
Nautilus → Scripts ofrece Quick Look, Open in Android y Share with Android;
no reemplaza acciones existentes. La interfaz Nautilus basada en líneas no
admite nombres con saltos de línea; CLI sí usa argv, sin shell interpolado.

## Capacidades y límites

**Desktop Mode.** Auto: remoto primero, display externo confirmado, teclado
y ratón externos, tamaño físico + touch para tablet; resolución solo corrobora.
Se ignoran botones de volumen/encendido como teclado físico. Override JSON en
`~/.config/macdesk/display-mode`. Deltas DPI/panel/compositor/tiling reversibles;
si el usuario modifica un valor, se conserva. Fallos de restauración conservan
el snapshot para reintento. No se cambia resolución ni se inventan modos XRandR.
Plank, wallpaper y decoraciones existentes se conservan.

**Snap.** Mouse/preview nativos de xfwm4 con `tile_on_move`; sin watcher de
ventanas propio. CLI: `left`, `right`, `up` (maximizar), `down` (restaurar),
`top-left`, `top-right`, `bottom-left`, `bottom-right`, `third-left`,
`third-center`, `third-right`, `two-thirds-left`, `two-thirds-right`.
Representan 50/50, 33/67, 67/33, tercios y 2×2 sobre el monitor de la ventana,
respetando workarea y marco. Rechaza diálogos/paneles.
`macdesk-smart shortcuts` instala Super+flechas y Super+Z solamente si Super
está operativo y no existe conflicto XFCE. **En este teléfono Super está
desactivado por la política anterior: no se instalaron esos atajos.**

**Quick Look.** Visor GTK propio efímero; Escape/Space cierran. Texto 256 KiB;
ZIP central directory ≤2 MiB/1000 entradas; TAR streaming ≤1000 entradas; 7z
usa libarchive sin extraer. JPG/PNG/WebP/GIF y SVG autónomos se rasterizan en un
worker. SVG con enlaces/entidades se rechaza. Imagen ≤32 MiB/40 megapíxeles;
SVG ≤1 MiB; PDF ≤32 MiB, solo página 1. Media usa GStreamer: metadatos y primer
frame si codecs/appsink están disponibles; no reproduce audio/video completo.
El worker tiene límite de datos de 256 MiB, CPU 10 s, salida 32 MiB y timeout
externo 15 s. No limitar AS de GJS: su JIT reserva gran espacio virtual incluso
para documentos pequeños. ZIP/texto mantienen además AS 512 MiB.
Cache `~/.cache/macdesk/quicklook` ≤32 MiB, por ruta/tamaño/mtime y LRU aproximado
por mtime. Trim la vacía. La UI solo recibe imágenes ya reducidas.
**SPACE de Nautilus conserva Sushi**, no el visor acotado propio: no atribuir
estos límites a Sushi. No se probó aún cada codec, GIF animado o artwork.

**Continuity.** Clipboard delegado a `clipboardEnable` nativo de Termux:X11,
sin duplicar sincronizador ni polling. La restricción Android de foco/permisos
sigue aplicándose; no se certificó la matriz completa de clipboard. Open/share
usa Termux FileProvider, no `file://` vía ADB, ni copias a almacenamiento público.
`~/Android/` enlaza las cinco carpetas compartidas sin reemplazar archivos.
Battery/network/display se consultan bajo demanda. Notificaciones, SMS,
llamadas y drag/drop cross-environment permanecen fuera del MVP.

**Memory Governor.** ACTIVE, IDLE (visible sin foco), BACKGROUND, REMOTE,
SUSPENDED. Una limpieza por transición tras 10 s (IDLE tras 60 s), sin GC
global ni kernel tuning. El fallback puede tardar hasta 60 s en detectar una
transición, más debounce. Un hook `event refresh` evita esa espera. No pausa
apps ni precarga helpers al volver. Métricas RSS con scope/valores desconocidos
explícitos; X11 Android separado se reporta desconocido desde el guest.

**DeX.** DisplayInfo real: ID, nombre, tipo, estado y geometría; preferencia
DeX → EXTERNAL → INTERNAL. No ID 2 ni Full HD fijos. Se usa `am start --display`
sin force-stop. Al desconectar se redescubre y conserva sesión; no se afirma
que exista un workspace Samsung “desktop #2”. **Solo se observó display 0
interno durante esta validación; conexión/reconexión DeX requiere prueba física.**

## Flags

`~/.config/macdesk/features.json`, aplicados en el siguiente arranque del core:

```json
{"continuity":true,"window_snap":true,"quicklook":true,"desktop_mode":true,
 "memory_governor":true,"dex_binding":true,"android_interval":60,
 "super_shortcuts":false}
```

Continuity controla las acciones nuevas; el clipboard nativo se configura por
separado con `termux-x11-preference clipboardEnable:false`. Los errores del core
no alteran el resultado del arranque XFCE. No se añadieron paquetes al escritorio.
Se descargó ADB 35 ARM64 fuera del repositorio como herramienta de mantenimiento:
ADB 29 del entorno Codex no pudo conectar al puerto inalámbrico moderno.

## Validación y benchmark

Tests locales: parsing display/input/visibilidad, scoring/override, geometría
negativa, deltas y fallos de restore, debounce, límites texto/ZIP/cache,
socket real autenticado y rechazo sin capacidad, trim que conserva proceso
ajeno y cancelación del grupo propio. Se ejecutan con `python3 tests/test-*.py`
individualmente (unittest discovery ignora estos nombres con guiones), además
de los tests shell existentes, compilación Python y sintaxis shell.

Dispositivo: recuperación cold start, reinicios del launcher normal con nuevos
PASS X11/XFCE/XFWM/panel/bus; comandos entre instancias PRoot; modos manual/auto
y hook remoto; BACKGROUND real con trim; ventana de prueba con mitad/tercio y
maximizar/restaurar; imagen Unicode/espacios y cierre Escape; PDF página 1;
WAV metadatos; cambio/restitución de framebuffer mediante XRandR.

Muestras de 15 s de descendientes XFCE (excluyen Android X11 y guardianes
hermanos; RSS duplica páginas compartidas):

| Contexto de muestra | RSS KiB | Procesos | CPU de un núcleo |
| --- | ---: | ---: | ---: |
| Baseline recuperado | 266624 | 12 | 3,17 % |
| Posterior en background | 123936 | 12 | 2,51 % |
| Prueba con UI de memoria abierta | 371576 | 14 | 11,63 % |
| Final tras trim de helpers propios | 295840 | 12 | 2,78 % |

Core: 14508–20416 KiB (~14–20 MiB), **0,00 % CPU** en las dos muestras
finales de 15 s. El incremento de arenas Python tras dumpsys/metrics sitúa la
residencia cerca del objetivo ideal de 20 MiB; se mantiene por debajo de 30 MiB.
La UI de memoria y helpers fueron cerrados mediante el hook de presión crítica,
no matando aplicaciones de usuario. La reducción de RSS inmediata no es una
medición exacta de memoria reclamable: kernel/Android cambian residencia.

El RSS final de la muestra completa es unos 28,5 MiB mayor que el baseline,
pero cambió el contexto Android y la sesión restaurada; no atribuir toda la
variación al core ni anunciar un ahorro causal. El conjunto del escritorio
**no cumple aún ~0 % CPU idle**: conserva guardianes antiguos con consultas cada
250/500 ms. No hay benchmark completo foreground/background Android ni latencias
físicas/DeX certificadas; tiempo stop/start observado 14–17 s, no comparable a
un baseline aislado de startup. No se sustituye esa prueba con estimaciones.

Evidencia detallada, fuera de Git para no publicar dumps privados:
`/workspace/macdesk-maintenance/smart-*.log` y `smart-*.json`.
Quedan pendientes DeX/varios monitores físicos, mouse/teclado/touch reales,
Super, matriz clipboard, conexión VNC real, todos los codecs/7z, reinicio
Termux:X11 aislado y benchmark Android completo. Estos pendientes impiden
declarar aceptación total aunque la implementación y las pruebas indicadas
estén disponibles.


## Archivos y commits

Creados: `scripts/lib/macdesk/*.py`, `macdesk-smart`, `macdesk-smart-host`,
`quicklook-render.js`, `quicklook-viewer.js`, `snap-menu.js`;
`tests/test-smart-desktop.py`, `tests/test-smart-core.py`; scope, diseño,
este documento y plan en `docs/superpowers/plans/`.
Modificados: `scripts/macdesk`, `session-start`, `macdesk-stop`,
`lib/android-x11.sh`, `macdesk-vnc-start`, `macdesk-vnc-stop`, README y .gitignore.
Se retiraron del índice (no del disco) los dos informes de salud volátiles.

`4b3afd3b` conserva las correcciones recuperadas previas. El commit posterior
`feat: add lightweight MacDesk smart desktop core and on-demand tools` contiene
esta ampliación. No se publicó ni se hizo push.

Referencia de mantenimiento: [arquitectura ADB Wi-Fi de AOSP](https://android.googlesource.com/platform/packages/modules/adb/+/HEAD/docs/dev/adb_wifi.md).

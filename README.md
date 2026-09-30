# MacDesk V6

Reproducible Galaxy S25 DeX desktop based on Debian, Termux:X11, XFCE, and Adreno/Turnip acceleration.

Gate order is strict: GPU -> stable desktop -> applications -> Android storage -> performance -> visuals -> physical input -> regression.

## Instalación all-in-one

En **Termux**, fuera de Debian/PRoot, con este repositorio en `~/MacDesk-V6`:

```bash
bash "$HOME/MacDesk-V6/install.sh"
```

Instalación desde cero con un solo comando, usando la rama de esta ampliación:

```bash
curl -fL --retry 2 https://raw.githubusercontent.com/Jorgeprdz/MacDesk-X11/feature/macos-27-lightweight/install.sh -o "$HOME/macdesk-install.sh" && bash "$HOME/macdesk-install.sh"
```

Requiere Android ARM64 y Termux con `pkg`. Prepara Debian, XFCE, Plank,
Nautilus/Sushi, Firefox y las dependencias del núcleo; reutiliza instalaciones
existentes y conserva cambios locales. Android pide confirmar la instalación
del APK oficial de Termux:X11. Después ejecuta `macdesk`; para almacenamiento
compartido, concede permiso mediante `termux-setup-storage`.

`bash install.sh --plan` muestra acciones/paquetes; `--check` revisa sin instalar.
Si MacDesk está abierto, el instalador lo deja intacto y pide volver a ejecutarlo
tras cerrar normalmente el escritorio. No reinstala Debian ni hace reset de Git;
tampoco reinicia sesiones o habilita VNC. Los paquetes faltantes usan las versiones de
los repositorios configurados. No instala Chromium, LibreOffice o Mailspring:
sus launchers existentes requieren esas aplicaciones por separado.

El APK y su paquete complementario son componentes distintos, como explica la
[instalación oficial de Termux:X11](https://github.com/termux/termux-x11#setup-instructions).
Si ya tienes un APK con otra firma, consérvalo: el instalador no lo desinstala.
El flujo nuevo se validó con pruebas automatizadas y auditoría del teléfono
existente; falta probar una instalación en un dispositivo vacío.

## Funcionalidades

| Feature | Implementación y límites |
| --- | --- |
| Continuity | Clipboard nativo Termux:X11, abrir/compartir en Android, enlaces a almacenamiento y estado bajo demanda. |
| Window Snap | Tiling/preview de xfwm4; mitades, tercios, 2×2 y selector. Super depende de resolver el conflicto de teclado existente. |
| Quick Look | Visor GTK efímero, texto limitado, imágenes, PDF, metadata/thumbnail multimedia y listado de archivos comprimidos. SPACE de Nautilus conserva Sushi. |
| Automatic Desktop Mode | PHONE/TABLET/DESKTOP/REMOTE, selección conservadora, override y deltas reversibles. |
| Memory Governor | Detecta visibilidad Android; limpia únicamente helpers propios con debounce y muestra métricas. |
| DeX Display Binding | Descubre displays dinámicamente y prefiere DeX/externo sin fijar ID ni resolución; prueba física pendiente. |

Un único núcleo ligero comparte contexto; no añade Electron, Node daemon,
servidor HTTP ni cuatro servicios independientes. Consulta [comandos, pruebas
y limitaciones](docs/SMART-DESKTOP.md): el escritorio completo todavía no está
certificado con CPU idle cercana a cero ni con toda la matriz de hardware.

## Recovery status (2026-09-29)

Android's phantom-process trimming was confirmed as the cause of repeated
Codex and desktop SIGKILL events. The device now has
`settings_enable_monitor_phantom_procs=false`. Normal XFCE startup, an owned
stop/restart, and a real X11 test window pass in `SAFE_FALLBACK` software graphics.
Shutdown validates process ownership; new launches require fresh health results.

This is a recovery baseline, **not a new full-product acceptance**. External DeX,
physical input, application coverage, and the six smart-desktop additions still
need their current-device acceptance. D-Bus clients in a separate PRoot session
remain unable to authenticate to the desktop bus; in-session checks pass.

See [Android process recovery](docs/ANDROID-PROCESS-RECOVERY.md) and
[remaining smart-desktop scope](docs/SMART-DESKTOP-SCOPE.md). The older hardware,
UID, rendering and resolution claims below are historical, not current evidence.

## Smart desktop additions (2026-09-29)

A single optional Python core now provides reversible PHONE/TABLET/DESKTOP/REMOTE
profiles, shared display context, conservative Android visibility detection and
memory trimming of its own preview helpers. Snap reuses xfwm4 plus on-demand
layouts; bounded Quick Look reuses installed GJS/Evince/GStreamer/libarchive.
Android open/share and storage links reuse Termux tools, and clipboard remains
Termux:X11's native integration. No desktop packages were added.

Read [commands, validation and known gaps](docs/SMART-DESKTOP.md) before treating
this as accepted on hardware. Physical DeX, Super keyboard behavior, full
clipboard/VNC coverage and whole-session near-zero idle CPU remain unverified.

## Historical acceptance (2026-08-21)

Recorded status: **daily-computer and bug-resolution PASS**.
Debian, XFCE/XFWM, host VirGL, the DeX keyboard contract, dynamic display
recovery, Chromium app keyboard bridges, Plank geometry recovery, and the
in-session health monitor are installed and survived a full phone reboot.

Firefox ESR is the primary browser. It uses the verified Adreno 830 -> Turnip
-> Zink path with WebRender/EGL and the Linux/XFCE port of Liquid Fox. Zen was
removed after repeated GTK/X11 freezes; its last profile backup is retained in
shared storage under `Download/MacDesk-Backups`.

Termux:X11 standalone `1.03.01-f68cd36-21.08.26` is installed with Android UID
10423, isolated from Termux UID 10602. The old shared-UID force-stop hazard no
longer applies. `scripts/restart-termux-x11-safe` remains the supported restart
path.

The final resolution is native 1920x1080 at 100% scale. The rejected 75%
experiment was completely rolled back because it produced visible pixelation;
no monitor-connect scaling automation remains.

Operational commands:

- `macdesk`: start or focus V6.
- `macdesk-resume`: detect the current DeX display, focus X11, and recover V6
  only when X11/XFWM are not healthy.
- `scripts/check-dex-keyboard.sh`: keyboard/accessibility regression gate.
- `scripts/measure-stability`: RSS, swap, process and Android exit history.
- `scripts/migrate-termux-x11-external.sh`: host-side standalone migration;
  retained for provenance/recovery and never run from Termux.
- `scripts/launch-whatsapp`: isolated Chromium WhatsApp window with its scoped
  physical-keyboard bridge.
- `scripts/launch-chatgpt`: isolated Chromium ChatGPT window with its scoped
  physical-keyboard bridge.
- `scripts/launch-firefox`: primary Firefox launcher with Adreno acceleration,
  Liquid Fox, single-instance focus, and safe URL/tab routing.
- `scripts/plank-geometry-guard`: realigns Plank after DeX/XRandR resizing.

Final evidence and the signed-off defect matrix are recorded in
`docs/MACDESK-V6-BUG-RESOLUTION-CERTIFICATE.md`.
# Iconos BigSur sin aparecer en la galería Android

## Recuperar fondos XFCE y cursores

`bash scripts/restore-xfce-assets.sh` recupera los 11 fondos oficiales de XFCE 4.20
y cursores Adwaita de Debian 13. Requiere `curl`, `dpkg-deb` y `sha256sum`
(en Termux: `pkg install curl dpkg coreutils`). Descarga los paquetes oficiales,
comprueba SHA256 y extrae los recursos sin instalar paquetes del sistema.
Guarda fondos en `~/.local/share/backgrounds/xfce` y cursores en
`~/.local/share/icons/MacDesk-Adwaita`, con `.nomedia` antes de copiar imágenes.
Conserva las licencias, no sobrescribe fondos existentes ni modifica BigSur.
En XFCE abre Configuración del escritorio → Fondo → Otra carpeta y pega
`/root/.local/share/backgrounds/xfce` (MacDesk con HOME compartido).
El cursor se selecciona al iniciar XFCE mediante un autostart efímero.
Para dejar de imponerlo, elimina
`~/.config/autostart/macdesk-restored-cursor.desktop` y elige otro en
Ratón y panel táctil → Tema. El script no reinicia sesiones.

Instalador del [tema BigSur de yeyushengfan258](https://www.opendesktop.org/p/1399044).
Ejecuta en **Termux** (no dentro de `/sdcard` como HOME):

```sh
pkg install -y python curl && mkdir -p "$HOME/.cache/macdesk" && touch "$HOME/.cache/macdesk/.nomedia" && curl -fL --retry 2 https://raw.githubusercontent.com/Jorgeprdz/MacDesk-X11/feature/macos-27-lightweight/scripts/install-bigsur-icons.py -o "$HOME/.cache/macdesk/install-bigsur-icons.py" && python "$HOME/.cache/macdesk/install-bigsur-icons.py"
```

Para la variante oscura, vuelve a ejecutar el script con `--dark`.
También funciona desde la terminal Linux de MacDesk con Python 3.9+.

- Instala ambos temas en almacenamiento privado oculto: `~/.local/share/macdesk/icon-themes/`, enlazados desde `~/.local/share/icons/`.
- Crea `.nomedia` antes de descargar o extraer imágenes. No copia nada a Downloads, Pictures ni `/sdcard`.
- Conserva temas ajenos: si ya existe una carpeta BigSur no administrada por este instalador, pide renombrarla y se detiene.
- Descarga el enlace vigente mediante la API oficial de OpenDesktop; limita tamaño, valida rutas y conserva licencias. Corrige un enlace del paquete que apunta al HOME de su autor.
- Selecciona **BigSur** desde **XFCE → Apariencia → Iconos** para verlo ahora. Se aplica automáticamente en la próxima sesión; no reinicia XFCE ni cierra aplicaciones. La selección se guarda en `~/.config/macdesk/icon-theme` y un autostart compatible con versiones anteriores.
- No agrega procesos residentes. Las versiones anteriores quedan conservadas en la carpeta oculta para evitar pérdida de datos.

La galería puede conservar miniaturas antiguas hasta actualizar su índice; el script no borra fotos ni modifica su base de datos. Para volver a elegir libremente otro tema, elimina `~/.config/autostart/macdesk-bigsur-icons.desktop` y `~/.config/macdesk/icon-theme`, y selecciónalo en Apariencia.

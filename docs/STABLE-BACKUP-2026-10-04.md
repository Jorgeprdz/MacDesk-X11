# Respaldo estable — 4 de octubre de 2026

Estado probado en el Samsung con Android/DeX, Termux, Debian PRoot y Termux:X11 `:2`.

## Incluido

- Arranque y guardas de la sesión XFCE, perfil gráfico seguro y los launchers vigentes.
- Dock XFCE Docklike: grupos de ventanas, apps transitorias, minimizar/restaurar, vistas previas transparentes, magnificación y bounce. CSS de la cápsula, margen inferior de 12px, configuración y binario aarch64 con código del patch y licencia.
- Listener común de dock y escritorio. Reconoce el dock por su strut inferior y conserva su identidad al ampliar la pantalla. Reacomoda los iconos a la derecha después de estabilizar la resolución; aplica tamaños compactos al dock en pantallas pequeñas. Los dos autostarts convergen en un solo proceso con bloqueo.
- Aplicaciones/Descargas desplegables, selector de apps Android y Centro de control. Puente Android, Java fuente y DEX; volumen, brillo, batería y enlaces de ajustes nativos.
- Accesos fijos Android a WhatsApp, Chrome, Samsung Internet y Spotify, con iconos macOS. Resuelven el componente desde el catálogo instalado y no dependen de que la app esté marcada en la carpeta Aplicaciones.
- Launcher host de Linea Individual con Hangover y reutilización de ventanas; icono macOS de ONLYOFFICE, su wrapper y el helper GTK aarch64 de la instalación vigente.

## Restaurar en el mismo entorno

1. Mantener el repo en `$HOME/MacDesk-V6` de Termux. Debian debe montarlo como `/root/MacDesk-V6`; se mantiene el display `:2`.
2. Tener instalados XFCE, xfce4-panel, xfce4-docklike-plugin 0.4.3, xfce4-cpugraph-plugin, python3-gi, python3-xlib, GTK3, wmctrl, desktop-file-utils y dbus-x11. El binario Docklike guardado requiere las bibliotecas ABI de la instalación Debian existente.
3. En Termux: Python, ADB inalámbrico ya conectado, Termux:X11 y proot-distro. Dar acceso al almacenamiento Android con el mecanismo existente de Termux.
4. Iniciar con `scripts/macdesk`. `configure-macos-dock` crea el motor Docklike por defecto; `configure-docklike` instala el plugin, CSS, launchers y autostarts. Reutiliza la configuración y preferencias ya existentes.
5. Si se restaura sin estado privado, abrir Aplicaciones → Elegir apps de Android → Actualizar lista, elegir las apps y Guardar. Esto reconstruye el catálogo e iconos desde el teléfono. Los cuatro accesos fijos quedan funcionales después de actualizar el catálogo.

El DEX se vuelve de solo lectura antes de cargarlo. Para recompilar el plugin ver `tools/docklike/README.md`. Las fuentes Java del puente están en `tools/android-bridge/`.

No se suben el catálogo personal de apps, las respuestas del puente, Descargas, capturas del escritorio, sesiones de navegador, contraseñas ni datos de las apps. El prefijo Wine/instalador propietario de Linea y las instalaciones de ONLYOFFICE/Hangover siguen requiriendo respaldo privado aparte; este repo conserva sus launchers e integración, no sus datos.

## Verificado

- Diez pruebas unitarias del modelo Android y reglas del dock.
- Prueba GTK de selector, búsqueda, guardado, controles y Descargas.
- Cambio real de resolución en Termux:X11: 768×571, 904×1065 y 1920×1080; dock de 740×54, 858×62 y 1090×78 respectivamente, centrado, sin recortar los extremos y a 12px del borde. Iconos del escritorio pasan de columna 3 a columna 9 al ampliar.
- Actualización real del catálogo (201 apps) y apertura nativa correcta de los cuatro accesos fijos Android.
- Restauradas las preferencias originales de resolución nativa después de la prueba.
- `tests/test-dock-live-geometry.py` comprueba margen, centrado y ancho directamente en X11. `tests/test_dock_geometry.py` cubre el caso que antes dejaba el dock arriba al ampliar.

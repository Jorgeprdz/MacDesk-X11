# Alcance pendiente tras recuperar XFCE

Estado histórico: auditoría inicial. La implementación y validación posteriores están en [SMART-DESKTOP.md](SMART-DESKTOP.md); la aceptación completa de hardware sigue pendiente.
Fuentes del alcance: anexos 164 y 165 recuperados en
`/workspace/macdesk-recovered-requests/`. La recuperación de procesos se documenta
en `ANDROID-PROCESS-RECOVERY.md`.

## Arquitectura observada

Android → Termux → Termux:X11 en :2 y PRoot Debian → un dbus-run-session →
startxfce4/XFWM → panel, Plank y aplicaciones.

La sesión inicia input-guard, plank-geometry-guard y session-health-supervisor.
El supervisor verifica periódicamente salud y recrea el guardián de Plank.
Existe launcher Android remoto, scripts VNC, un detector DeX basado en dumpsys
accessibility y un puente de entrada Chromium. No existe todavía macdesk-core.
El detector DeX debe dejar de equiparar cualquier display de accesibilidad con
un monitor externo confirmado.

## Capacidades verificadas en el dispositivo

| Área | Hallazgo | Consecuencia |
| --- | --- | --- |
| X11 | wmctrl, xdotool, xprop, xrandr disponibles | Reutilizar antes de añadir una biblioteca |
| Escritorio | XFWM 4.20, XFCE 4.20, Nautilus 48.3 | Conservar el gestor de ventanas y la sesión |
| Preview | Sushi 46 y su ejecutable presentes | Investigar formatos y límites antes de reemplazarlo |
| Python | Intérprete presente; gi, dbus, Xlib no importables | No suponer GTK o D-Bus Python disponibles |
| Multimedia | ffmpeg, ffprobe, poppler e ImageMagick no encontrados | Medir dependencias antes de añadir previews |
| Archivos | Download, Pictures, Documents, Movies y Music accesibles en /sdcard | Usar acceso directo sin copiar bibliotecas |
| Pantalla | Android solo informó display interno; X11 1280×1024 | Falta observar conexión y desconexión DeX real |
| Bus | Funciona dentro de la sesión; cliente de otro PRoot rechazado | El núcleo gráfico debe vivir dentro del bus existente |

## Trabajo que falta

1. Definir núcleo compartido y canal de eventos: sin cuatro daemons, sin servidor
   HTTP y sin consultas frecuentes a dumpsys. Respetar fallos opcionales.
2. Detectar displays Android reales y contexto remoto. Confirmar DeX mediante
   identidad, tipo y estado; nunca fijar ID 2. Registrar conexión/desconexión.
3. Aplicar modos PHONE/TABLET/DESKTOP/REMOTE mediante deltas reversibles, con
   override manual y conservación de preferencias del usuario.
4. Integrar snap mediante capacidades XFWM y eventos, con geometría por monitor,
   layouts, vista previa efímera y detección de conflictos de atajos.
5. Completar Quick Look bajo demanda: formatos, lectura acotada, caché limitada,
   archivos grandes, espacios y Unicode. No asumir cobertura completa de Sushi.
6. Continuity: reutilizar clipboard de X11 cuando esté disponible, abrir/compartir
   con Android mediante argumentos seguros y exponer estado solo bajo demanda.
7. Governor: estados ACTIVE/IDLE/BACKGROUND/REMOTE/SUSPENDED; una limpieza por
   transición con debounce. Solo recursos recreables registrados por MacDesk;
   nunca cerrar documentos, navegadores ni procesos del usuario para ahorrar RAM.
8. Medir RAM/CPU antes y después, arranque, reapertura de preview, snapping y
   cambio de modo. Validar teléfono, DeX, rotación, reconexión, VNC y entradas físicas.

El presupuesto solicitado para infraestructura permanente es menos de 30 MB,
idealmente 15–20 MB, y CPU idle cercana a cero. No se dispone todavía de una
medición que permita certificar ese presupuesto para las funciones nuevas.

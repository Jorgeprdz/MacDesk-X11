# Smart Desktop: diseño incremental

Se conserva Android → Termux → Termux:X11 :2 → PRoot Debian → un bus
D-Bus → XFCE/xfwm4 → panel/Plank/Nautilus. No se restaura otro checkout.
Los cambios de recuperación sin commit son anteriores a esta ampliación.

## Decisiones

Un proceso Python estándar dentro del bus de XFCE comparte contexto, escucha
un socket Unix privado y eventos de geometría X11 (libX11 mediante ctypes).
Los comandos son efímeros. Los cambios Android se verifican al recibir eventos
y, si ADB está disponible, mediante fallback conservador de 60 segundos;
no existe API lifecycle fiable dentro del guest actual. Sin puente no se
infiere background a partir del foco de una aplicación Linux.

Se descartan cuatro demonios y un nuevo servicio Android/JVM. El núcleo no
reemplaza el supervisor de salud existente ni modifica la política de teclado
que resolvió problemas físicos: Super desactivado se informa como conflicto.
El coste de los guardianes antiguos se mide aparte; no prometer idle global
cero mientras permanezcan sus bucles existentes.

Desktop mode aplica deltas xfconf con snapshot y restauración condicional:
si el usuario cambió un valor, se conserva. Se reutiliza tiling y preview de
xfwm4; los layouts fraccionarios consultan únicamente la ventana activa y los
monitores al invocarse. No se sustituye el window manager.

Quick Look propio es efímero, usa GJS/GTK ya requerido por Sushi si está
disponible. Texto acotado a 256 KiB, archivos comprimidos listados sin extraer,
con límites de tiempo/entradas. PDF/media reutilizan Evince/GStreamer de Sushi; herramientas externas son fallback opcional. Ausencia muestra metadatos y explicación. Nautilus conserva Sushi
para SPACE, cuya cobertura y residencia no se confunden con el visor acotado.

Continuity reutiliza clipboardEnable de Termux:X11 (ya configurado). No se
añade otro sincronizador que compita por CLIPBOARD. Open/share usan únicamente
handlers disponibles; no se publican archivos privados mediante file:// ADB.

Governor termina solamente hijos recreables creados por el núcleo, usando
objetos Popen (sin aceptar PIDs proporcionados por clientes); conserva XFCE y
apps. Debounce background 10 segundos, una limpieza por transición. Métricas
/proc son opcionales; inaccesible significa desconocido, nunca cero.

Display discovery usa DisplayInfo real de dumpsys display, no accesibilidad
ni ID 2 fijo. Solo un display activo identificado como DeX/external puede ser
preferido. am start --display se usa al cambiar destino, sin force-stop y sin
reiniciar servidor. Geometría Linux sigue los eventos X11, no se inventan modos
xrandr que Android no haya publicado.

## Aceptación y límites del entorno

Tests deterministas de parsing, perfiles, reversibilidad, geometría negativa,
archivos grandes, Unicode, presión y transiciones. Pruebas de socket real y
medición del núcleo sin display. Dispositivo: ADB offline al iniciar trabajo;
DeX, interacción física, reinicios y benchmark completo requieren recuperarlo.
No se certifican a partir de fixtures ni de evidencia histórica.

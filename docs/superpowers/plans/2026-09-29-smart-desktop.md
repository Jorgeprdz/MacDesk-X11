# Smart Desktop Implementation Plan

> Ejecución inline con superpowers:executing-plans; autorización explícita del
> usuario para continuar del scope a implementación y pruebas.

**Goal:** añadir seis capacidades sin reescribir la sesión recuperada.
**Architecture:** núcleo Python único con socket Unix y eventos X11; módulos
efímeros y tiling/clipboard existentes.
**Tech Stack:** Python estándar, libX11, XFCE tools, GJS/GTK opcional existente.
**Spec:** `docs/SMART-DESKTOP-DESIGN.md` y anexos completos del usuario.

## Global Constraints

No root, kernel tuning, force-stop, procesos de usuario terminados, HTTP,
ID/resolución fija, dependencias pesadas ni reemplazo XFCE/xfwm4.

## Review Focus

ADB ausente o respuesta parcial: estado desconocido, sesión intacta.
Display ID reutilizado: descubrir de nuevo cada snapshot.
Preferencias editadas durante perfil: no sobrescribir al restaurar.
Nombres maliciosos/Unicode: argv y rutas absolutas, nunca shell interpolado.
Background rápido y PID reciclado: debounce y solo hijos propios.

## Secuencia

- [x] Tests fallando: `tests/test-smart-desktop.py`, parsing displays,
  scoring/override, deltas, geometría, límites preview y governor.
- [x] `scripts/lib/macdesk/{common,context,profiles}.py`: estado atómico,
  detección y políticas puras; pruebas sin Android.
- [x] `scripts/lib/macdesk/{snap,preview,continuity}.py`: comandos bajo demanda;
  `scripts/quicklook-viewer.js`: visor GTK efímero.
- [x] `scripts/lib/macdesk/{core,xevents,cli}.py`: socket privado, debounce,
  logging rotado, hijos propios, eventos X11 y fallback Android lento.
- [x] `scripts/macdesk-smart` y aliases; hook opcional fail-safe en sesión;
  entrypoints host y VNC; detector DeX corrige helper existente.
- [x] Ejecutar tests Python/shell pertinentes, compilación, diff check,
  integración socket y benchmark local. Registrar pruebas físicas pendientes.
- [x] Documentar comandos, flags, limitaciones y costes; revisar diff y commit
  de la ampliación sin apropiarse de modificaciones previas ajenas.

## Resultado y pendientes

Implementación y revisión independiente realizadas. Correcciones: grupos propios de
preview, DATA 256 MiB compatible con JIT, snapshots conservados al fallar restore,
DISPLAY host explícito, métricas desconocidas y señales físicas/input. La validación
de hardware no es completa: véase SMART-DESKTOP.md. No certificar DeX ni idle global.

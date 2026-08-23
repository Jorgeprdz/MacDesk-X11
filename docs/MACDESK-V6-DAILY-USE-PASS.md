# CERTIFICADO DE ACEPTACIÓN — MACDESK V6

> Estado histórico, sustituido el 21 de agosto de 2026 por el gate de
> estabilización integral. No debe interpretarse como aceptación final mientras
> la migración standalone, los ciclos fríos y las pruebas físicas sigan
> pendientes.

> **Cierre:** esas condiciones fueron satisfechas posteriormente. El estado
> vigente y la matriz final de defectos se encuentran en
> `docs/MACDESK-V6-BUG-RESOLUTION-CERTIFICATE.md`.

**Certificado:** `MACDESK-V6-DAILY-OFFICE-LEISURE-PASS`  
**Fecha:** 21 de agosto de 2026  
**Dispositivo:** Samsung Galaxy S25 `SM-S931B`  
**Entorno:** Samsung DeX · Termux:X11 · Debian PRoot · XFCE/XFWM · Adreno 830

## Resultado certificado

**PASS HISTÓRICO — REVALIDACIÓN INTEGRAL PENDIENTE**

MacDesk V6 ha alcanzado un estado funcional y visual suficientemente estable
para utilizarse diariamente, conectado mediante Samsung DeX, en navegación web,
gestión de archivos, documentos, hojas de cálculo, presentaciones, terminal y
consumo general de contenido.

## Evidencia de aceptación

| Componente | Resultado |
|---|---|
| Aceleración Turnip/Vulkan/EGL/GLES/OpenGL | PASS |
| Renderizador por software ausente | PASS |
| XFCE/XFWM estable | PASS |
| Apariencia Golden Gate | PASS físico |
| Teclado para el uso validado | PASS físico |
| Mouse y manejo de ventanas | PASS físico |
| Zen Browser | PASS físico |
| Nautilus | PASS físico |
| Nautilus frío / caliente | 1.29 s / 0.99 s |
| Android storage `/mnt/s25` | lectura/escritura PASS |
| LibreOffice Writer, Calc e Impress | PASS funcional |
| Plank GoldenGate, compositor XFWM y lanzadores | PASS |
| Reinicio controlado de sesión | PASS de ingeniería |

## Alcance

Este certificado acredita el uso diario para:

- Ofimática con LibreOffice.
- Navegación y ocio con Zen Browser.
- Gestión directa de archivos del teléfono con Nautilus.
- Terminal y tareas Linux de escritorio.
- Interacción física mediante teclado, mouse y pantalla DeX.

## Exclusiones pendientes

Este documento **no es todavía el certificado final integral de MacDesk V6**.
Permanecen abiertos:

- Tres ciclos fríos finales consecutivos y recuperación tras terminación no limpia.
- Matriz exhaustiva final del teclado mexicano-español/Super.
- Migración de Termux:X11 a UID standalone mediante ADB externo.
- Revalidación posterior de memoria, apps y reconexión DeX.

Estas exclusiones no invalidan el PASS aquí concedido para ofimática y ocio.

Chromium permanece instalado como navegador secundario opcional. Por decisión
del propietario, su aceleración específica no bloquea la aceptación: Zen es el
navegador principal certificado.

## Dictamen histórico

**MACDESK_V6_DAILY_COMPUTER=REVALIDATION_PENDING**  
**OFFICE_USE=PASS**  
**LEISURE_USE=PASS**  
**FINAL_V6_RELEASE=PENDING_EXTERNAL_ADB**

El dictamen vigente es `MACDESK_V6_DAILY_COMPUTER=PASS`; consulte el certificado
final enlazado al inicio de este documento.

Emitido por Codex con base en pruebas automatizadas y la validación física
comunicada por el usuario en el dispositivo objetivo. Las capturas temporales
de evidencia fueron eliminadas después de revisarse, por solicitud del usuario.

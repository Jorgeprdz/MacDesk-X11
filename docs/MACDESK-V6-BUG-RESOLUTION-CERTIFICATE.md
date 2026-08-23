# CERTIFICADO DE RESOLUCIÓN DE BUGS — MACDESK V6

**Certificado:** `MACDESK-V6-FINAL-BUG-RESOLUTION-PASS`  
**Fecha de emisión:** 21 de agosto de 2026, 21:26 CDT  
**Dispositivo:** Samsung Galaxy S25 `SM-S931B`  
**Plataforma:** Samsung DeX · Termux:X11 · Debian PRoot · XFCE/XFWM  
**Termux:X11:** `1.03.01-f68cd36-21.08.26`  
**Resultado:** **PASS — APTO COMO COMPUTADORA DE USO DIARIO**

## Declaración

Se certifica que los defectos bloqueantes encontrados durante la estabilización
de MacDesk V6 fueron diagnosticados, corregidos, persistidos y sometidos a
pruebas automáticas y físicas en el dispositivo objetivo. El sistema sobrevivió
un reinicio completo del teléfono y recuperó el escritorio y sus funciones
aceptadas.

Este documento sustituye los certificados históricos que todavía mostraban la
migración standalone o la revalidación física como pendientes.

## Matriz de defectos cerrados

| ID | Defecto observado | Causa o condición corregida | Solución vigente | Evidencia final | Estado |
|---|---|---|---|---|---|
| BR-01 | Reiniciar o detener Termux:X11 podía terminar también Termux y la sesión | Termux y Termux:X11 compartían UID | Migración a APK standalone con UID independiente y reinicio seguro | X11 UID 10423; Termux UID 10602; reboot completo PASS | **RESUELTO** |
| BR-02 | Alt+Tab no abría el selector rápido esperado de aplicaciones DeX | Captura/interceptación conflictiva y traducción incorrecta de modificadores | KeyInterceptor, captura Meta y auto-Accessibility desactivados; scancodes preferidos; contrato de teclas persistente | `ALT-TAB CONFIG: PASS` y validación física del selector | **RESUELTO** |
| BR-03 | Ctrl se perdía, no abría Ctrl+T o parecía quedar pegado | Secuencia de press/release inconsistente al cruzar Android, Termux:X11 y XKB | `input-guard` restablece el dispositivo Lorie, neutraliza Mod4 residual y conserva Control utilizable | Ctrl+T, Ctrl+C, Ctrl+V y ausencia de tecla pegada confirmados físicamente | **RESUELTO** |
| BR-04 | WhatsApp Web no recibía texto aunque otros programas sí | El campo editable de Chromium perdía la ruta XInput2 válida bajo DeX; la ruta Firefox mostró errores de almacenamiento/conectividad | Perfil Chromium aislado, renderizado estable por software y puente X11→CDP limitado a la pestaña WhatsApp enfocada | Texto y Ctrl+A físicos PASS; puente reporta `input bridge ready`; reboot PASS | **RESUELTO** |
| BR-05 | La alternativa Firefox de WhatsApp parpadeaba una alerta de almacenamiento persistente y reportaba falta de Internet | Persistencia/origen web no confiable en esa envoltura | Ruta descartada como producción; launcher certificado usa Chromium aislado | WhatsApp Chromium enlazado por QR y operativo | **RESUELTO POR SUSTITUCIÓN** |
| BR-06 | No existía una ventana independiente de ChatGPT integrada al escritorio | Faltaba launcher, perfil y solución para el mismo fallo de teclado de Chromium | `launch-chatgpt`, perfil independiente, CDP local 9226 y entrada limitada a la ventana enfocada | Escritura física PASS; lanzador ChatGPT persiste en Plank después del reboot | **RESUELTO** |
| BR-07 | Plank permanecía en la posición calculada para la primera geometría y no bajaba tras redimensionar | Plank conservaba en caché la altura inicial del monitor GDK | `plank-geometry-guard` detecta una geometría estable, confirma el desajuste y reinicia sólo el dock | Prueba física de resize PASS; raíz 1920x1080 y dock `Y=904`, `HEIGHT=176`, borde=1080 | **RESUELTO** |
| BR-08 | Existía riesgo de perder fixes al reiniciar el teléfono | Cambios inicialmente sólo activos en runtime | Preferencias, guardas, launchers y orden del dock integrados al arranque de V6 | Reboot completo: X11, VirGL, XFCE, XFWM, D-Bus, Zen, terminal, WhatsApp y teclado PASS | **RESUELTO** |
| BR-09 | Escala 0.75 del monitor produjo una imagen muy pixelada | El modo escalado generó un lienzo 2560x1440 sobre una salida física 1920x1080 | Experimento retirado; perfil nativo 100%, fullscreen y sin automatización por conexión | XRandR 1920x1080; preferencias `native`, 100, separación secundaria `false`; búsqueda de automatización vacía | **REVERTIDO / CERRADO** |

## Evidencia automática al emitir el certificado

Lectura tomada el `2026-08-21T21:26:14-06:00`:

| Gate | Resultado observado |
|---|---|
| Termux:X11 instalado | `1.03.01-f68cd36-21.08.26`, UID 10423 |
| Aislamiento respecto de Termux | PASS — Termux UID 10602 |
| XRandR | `1920x1080`, 59.96 Hz |
| Raíz X11 | 1920 × 1080 |
| Preferencia de resolución | `displayResolutionMode=native` |
| Escala | `displayScale=100` |
| Pantalla completa | `fullscreen=true` |
| Perfil secundario separado | `storeSecondaryDisplayPreferencesSeparately=false` |
| D-Bus de sesión | PASS |
| XFCE | PASS |
| XFWM | PASS |
| Panel XFCE | PASS |
| KeyInterceptor | DISABLED |
| Filtro de teclado en DeX Display 6 | NONE |
| Auto Accessibility / Meta capture / pointer capture | FALSE / FALSE / FALSE |
| Prefer scancodes / workaround de teclado | TRUE / TRUE |
| Alt+Tab | PASS |
| VirGL multi-client | proceso activo |
| Input guard | proceso activo |
| Plank geometry guard | proceso activo |
| Geometría Plank | ancho 1920; borde inferior 1080 |
| Orden persistente del dock | incluye WhatsApp y ChatGPT |
| Automatización de escala 75% | no encontrada |

## Validación física comunicada por el propietario

- Ctrl+T abrió una pestaña nueva en Zen.
- Ctrl+C y Ctrl+V funcionaron en la prueba de texto.
- Alt+Tab abrió el selector rápido y permitió cambiar de aplicación.
- WhatsApp Chromium aceptó entrada del teclado físico.
- ChatGPT Chromium aceptó entrada del teclado físico.
- Plank se realineó después de redimensionar la ventana.
- Tras reiniciar el teléfono, los fixes siguieron presentes y funcionales.
- La escala 75% fue rechazada por pixelación y el propietario solicitó volver a
  la resolución original; el rollback quedó verificado en 1920x1080 nativo.

## Componentes persistentes relevantes

- `scripts/lib/android-x11.sh`: interfaz segura de preferencias y foco DeX.
- `scripts/input-guard`: contrato XKB y recuperación de modificadores.
- `scripts/check-dex-keyboard.sh`: gate de regresión Alt+Tab/Accessibility.
- `scripts/chromium-input-bridge.mjs`: traducción de teclado físico mediante CDP
  local, condicionada al foco.
- `scripts/launch-whatsapp`: app Chromium y perfil aislado de WhatsApp.
- `scripts/launch-chatgpt`: app Chromium y perfil aislado de ChatGPT.
- `scripts/plank-geometry-guard`: recuperación del dock tras cambios XRandR.
- `scripts/session-start`: persistencia de launchers, guardas y sesión.
- `scripts/macdesk-resume`: reconexión dinámica al display DeX vigente.

## Alcance y reservas

El PASS cubre el hardware, versión de Termux:X11 y configuración documentados.
WhatsApp y ChatGPT usan deliberadamente renderizado Chromium por software para
priorizar estabilidad de composición y entrada; no se certifica aceleración GPU
para esas dos ventanas. La tecla Super dedicada dentro de X11 permanece
neutralizada por diseño para evitar el antiguo modificador pegado; las funciones
aceptadas son Ctrl, portapapeles y Alt+Tab nativo de DeX.

No se certifica la escala 75%: quedó expresamente rechazada y eliminada. La
configuración certificada del monitor es 1920x1080 nativo al 100%.

## Dictamen

```text
MACDESK_V6_DAILY_COMPUTER=PASS
BLOCKING_BUGS=RESOLVED
STANDALONE_UID_ISOLATION=PASS
PHYSICAL_KEYBOARD_CONTRACT=PASS
WHATSAPP_INPUT=PASS
CHATGPT_INPUT=PASS
PLANK_RESIZE_RECOVERY=PASS
POST_REBOOT_PERSISTENCE=PASS
DISPLAY_MODE=1920x1080_NATIVE_100_PERCENT
REJECTED_SCALE_75=ROLLED_BACK
```

Emitido por Codex con base en inspección del sistema vivo, gates automatizados,
logs persistentes y las pruebas físicas comunicadas por el propietario. Es un
certificado técnico de aceptación del proyecto, no una garantía comercial del
hardware ni de servicios web de terceros.

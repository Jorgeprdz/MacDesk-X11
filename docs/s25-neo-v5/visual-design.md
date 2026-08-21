# S25 Neo visual design

## Decisión de arquitectura

La auditoría del 20 de agosto de 2026 confirmó que el escritorio instalado no es XFCE: usa **Labwc 0.9.6**, Yambar, Plank, Nautilus y foot sobre Termux:X11. Tampoco hay Zen Browser ni una App Store instalada; Chromium es el navegador predeterminado. Para respetar el sistema funcional, esta personalización no instala XFCE, no sustituye Labwc, no cambia el navegador y no añade un software center.

La identidad visible es **S25 Neo · MacDesk**. WhiteSur es solamente la fuente de assets GTK, iconos, cursor y wallpaper.

## Diseño

- Controles GTK claros, radios moderados y espaciado moderno mediante WhiteSur-Light.
- Iconografía WhiteSur azul estándar para carpetas, aplicaciones y acciones.
- Cursor WhiteSur a 24 px, adecuado para 1920×1080 a escala 1.0.
- Adwaita Sans 11, ya instalada y legible; no se descargaron fuentes propietarias.
- Barra Yambar de 34 px, fondo oscuro semitransparente, branding discreto, título de ventana y reloj. Se retiraron CPU/RAM por ser indicadores técnicos redundantes.
- Plank centrado, intellihide, iconos de 42 px, animaciones mínimas y fondo claro translúcido.
- Wallpaper WhiteSur dark 1080p. No está fijado directamente en el arranque: `scripts/s25-neo-wallpaper` lee `state/wallpaper`, por lo que la selección persiste.
- Sin blur, compositor adicional, shell pesado ni servicios residentes nuevos.

## Fuentes upstream fijadas

- [WhiteSur GTK](https://github.com/vinceliuice/WhiteSur-gtk-theme), commit `1912dee2e48d5d347237dfab6e6a0862bac22714`
- [WhiteSur icons](https://github.com/vinceliuice/WhiteSur-icon-theme), commit `f6a78df1c9ea8c5f804b6c72d03408ca3db3521b`
- [WhiteSur cursors](https://github.com/vinceliuice/WhiteSur-cursors), commit `e190baf618ed95ee217d2fd45589bd309b37672b`
- [WhiteSur wallpapers](https://github.com/vinceliuice/WhiteSur-wallpapers), commit `5c1d7ca20b8de0a7efe443792c19e49277262e02`

Se usa el release GTK precompilado; no se instala `sassc` ni se compila el tema. Los repos están en `vendor/visual/`.

## Configuración modificada

- `config/labwc/environment`, `rc.xml` y `autostart`
- `config/yambar/config.yml`
- `config/plank/dock.theme`
- `config/gtk/settings.ini`
- `scripts/s25-desktop-prepare` y `nautilus-session-service`
- wallpaper y selector persistente en `config/wallpapers/` y `state/wallpaper`

GTK3/GTK4 se configura para root y para el usuario `macdesk`. Nautilus conserva su bus mínimo, previews, almacenamiento compartido y asociaciones existentes.

## Uso

Aplicar o reparar idempotentemente:

```sh
$HOME/MacDesk-V5/scripts/s25-neo-beautify.sh
```

Validar:

```sh
$HOME/MacDesk-V5/scripts/s25-neo-visual-check.sh
```

Cambiar wallpaper de forma persistente:

```sh
printf '%s\n' '/ruta/absoluta/fondo.jpg' > "$HOME/MacDesk-V5/state/wallpaper"
```

El cambio aparece en el siguiente arranque de MacDesk. La imagen debe ser legible desde Fedora PRoot.

Revertir exactamente la configuración activa previa:

```sh
$HOME/MacDesk-V5/scripts/s25-neo-beautify-rollback.sh
```

El backup utilizado se registra en `state/visual-backups/latest`; el log acumulativo está en `logs/s25-neo-beautify.log`.

## Diferencias pendientes respecto al pedido

Los checks `XFCE` y `ZEN` reportan `NOT_INSTALLED`. Esto es intencional y evita un falso PASS: instalar XFCE o Zen sería una migración funcional fuera del alcance de esta capa visual. La personalización compatible con el sistema real sí queda aplicada y validada.
# Storage and DeX integration

Phone storage integration is documented in [storage-integration.md](storage-integration.md). Termux:X11's own `fullscreen` preference is used while S25 Neo runs; the previous preference set is saved under `state/` and restored by `macdesk-stop`. No privileged Android setting is changed.

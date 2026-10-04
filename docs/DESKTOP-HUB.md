# Aplicaciones, Descargas y Centro de control

En la parte derecha del dock:

- **Aplicaciones** (carpeta azul con Android): cuadrícula y buscador. Android muestra solo los accesos elegidos, junto a las cinco apps principales de MacDesk.
- **Descargas** (carpeta azul con flecha): archivos recientes de `/sdcard/Download`, búsqueda y botón Abrir carpeta. Los archivos se abren con el visor nativo de Android usando MediaStore; los subdirectorios se abren en Files. Se muestran hasta 120 entradas recientes para limitar el trabajo al abrir el panel.
- **Centro de control** (icono de deslizadores): batería, volumen multimedia y brillo del teléfono, accesos a Wi-Fi/Bluetooth/Sonido/Pantalla de Android, modo oscuro, preferencias del dock y configuración de pantalla de MacDesk.

Para cambiar los accesos: Aplicaciones → Elegir apps de Android → marcar/desmarcar → Guardar. El botón Actualizar lista incorpora apps recién instaladas y actualiza sus iconos. Se puede buscar por nombre o paquete. Quitar todas limpia la selección; no desinstala aplicaciones.

Selección inicial: Canva, Chrome Beta (nombre que devuelve Android), Galería, Gmail, Maps y WhatsApp. El catálogo contiene 201 apps al instalar esta función; solo seis generan accesos de escritorio.

Los paneles se cierran con Escape, con la cruz o al pulsar fuera. Los accesos Android abren o recuperan las tareas nativas de Android; su ejecución sigue en Android/DeX. Las ventanas de Linux mantienen la gestión del dock existente.

Datos persistentes:

- `state/android-apps/catalog.json`, `icons/`: catálogo e iconos reales, sin consultas continuas.
- `state/android-apps/selected.json`: selección.
- `state/android-apps/adb-device`: dispositivo ADB preferido; usa la conexión inalámbrica ya configurada o el dispositivo local disponible.
- `state/desktop-hub.json`: modo oscuro seleccionado.
- `config/dock-hub/launchers/`: las tres entradas del dock, restauradas por `scripts/configure-docklike`.
- `scripts/macdesk-desktop-hub-setup`: regenera solo los accesos seleccionados al iniciar.

El puente `ANDROID` comparte el dispatcher existente con Linea Individual. Valida acciones, componentes de aplicaciones y rutas de Descargas; devuelve resultados por archivos JSON privados. El listado y los iconos se actualizan solo al pedirlo. GTK se inicia al abrir un panel y termina al cerrarlo.

Validación: pruebas del modelo (selección, retirada de accesos, rutas, orden y validación de controles); prueba GTK de búsqueda/selector/guardar/deslizadores/cuadrícula; catálogo y 201 iconos en el teléfono; apertura nativa de app y archivo nuevo indexado en MediaStore; cambio de tema; cierre al pulsar fuera; entradas .desktop válidas y dock a 12px del borde.

Además de la carpeta, el dock tiene accesos fijos a WhatsApp, Chrome, Samsung Internet y Spotify con iconos macOS. `scripts/macdesk-android-open` los resuelve por paquete contra el catálogo actual. Cambiar la selección de Aplicaciones no elimina estos cuatro accesos.

El dock y los iconos del escritorio comparten `scripts/dock-geometry-listener`: resize con debounce para el escritorio, strut inferior para identificar el dock y tamaños adaptados al ancho. Véase `docs/STABLE-BACKUP-2026-10-04.md` para restauración y resultados de pruebas.

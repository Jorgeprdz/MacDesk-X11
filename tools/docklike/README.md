# Docklike para MacDesk

Base oficial: [xfce4-docklike-plugin 0.4.3](https://github.com/xfce-mirror/xfce4-docklike-plugin/tree/xfce4-docklike-plugin-0.4.3), commit `efb05d53557e2c11e865eb92a6aa1f85d5060faa`.

`macdesk.patch` añade magnificación animada, bounce al iniciar una app y vistas previas RGBA transparentes. El tamaño de los iconos sigue el alto del panel para caber en ventanas pequeñas. `libdocklike-aarch64.so` es el binario probado en Debian/Termux aarch64; no sirve para x86_64. Licencia GPL-3.0, incluida en `COPYING`.

`build.sh` recompila desde la etiqueta oficial. Dependencias Debian: build-essential, git, patch, autoconf, automake, libtool, gettext, intltool, xfce4-dev-tools, libgtk-3-dev, libxfce4panel-2.0-dev, libxfce4ui-2-dev, libxfce4util-dev, libxfconf-0-dev, libxfce4windowing-0-dev, libwnck-3-dev y libkeybinder-3.0-dev. Puede requerir `autopoint` por separado.

`scripts/configure-docklike` instala el binario y conserva una copia del original. El patch se aplica sin modificar otras partes del upstream.

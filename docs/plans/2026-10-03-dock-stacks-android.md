# Android shortcuts, dock stacks and control center

Intent: lightweight MacDesk UI, Android native apps remain responsible for substantial work. User requested Android app shortcuts with actual icons, Applications and Downloads dock stacks, a way to choose shortcuts, and a Control Center.

Design: cached Android launcher catalog plus rendered launcher icons; shared selected-app JSON; host FIFO extends existing dispatcher and returns per-request JSON results. GTK3 popovers anchor above launcher buttons, scroll grids and search apps/files. Selection is a searchable checklist, persisted atomically; only chosen apps get desktop launchers. Downloads show phone Download recent files and folder links; file actions route to the Android viewer through MediaStore with granted content URIs. Linux launcher actions continue restoring existing windows. Control Center uses the existing ADB connection for volume/brightness; offers native Wi-Fi/Bluetooth settings links, theme switching, dock preferences and display settings.

Implementation and validation:
1. Android Java catalog/icon helper and host request protocol; test labels/icons, safe request validation, result handling.
2. GTK stack/selector/control UI; test filtering, selection persistence, desktop-file generation, downloads ordering/path validation.
3. Add fixed XFCE launcher plugins for Applications, Downloads, Control Center; preserve dock geometry and app restoration.
4. Start host service in normal Termux context; live catalog refresh, selected apps only, GTK screenshots, actual no-op/read controls, isolated launch/open verification where possible.
5. Confirm autostart/restart persistence and 12px bottom gap, document any platform limits.

No continuous app catalog polling or background thumbnail capture. Refresh explicitly from chooser. Sensitive filesystem paths and arbitrary commands are never accepted by the Android request handler.

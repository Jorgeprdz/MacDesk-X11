<div align="center">

# 🖥️ MacDesk V6

### Turn Samsung DeX into a lightweight Linux desktop.

**Debian · Termux:X11 · XFCE · Adreno / Turnip · Galaxy S25**

<img alt="Android ARM64" src="https://img.shields.io/badge/Android-ARM64-3DDC84?logo=android&logoColor=white">
<img alt="Debian" src="https://img.shields.io/badge/Debian-Linux-A81D33?logo=debian&logoColor=white">
<img alt="XFCE" src="https://img.shields.io/badge/Desktop-XFCE-2284F2?logo=xfce&logoColor=white">
<img alt="Termux X11" src="https://img.shields.io/badge/Display-Termux%3AX11-111111">
<img alt="Project status" src="https://img.shields.io/badge/Status-Active-success">

<br>

*A reproducible desktop environment designed to make a Samsung Galaxy S25 + DeX behave more like a real lightweight computer.*

</div>

---

## ✨ What is MacDesk?

MacDesk V6 is a **Linux desktop environment for Android/DeX** built around Debian, Termux:X11 and XFCE.

The project focuses on a practical daily-computer experience instead of simply launching a Linux desktop inside Android. It includes display recovery, desktop profiles, window management, Android integration, lightweight memory management, application launchers and hardware-aware recovery tooling.

> **Design goal:** keep the desktop fast, recoverable and lightweight — without Electron shells, Node daemons or unnecessary always-on services.

---

## 🚀 Quick start

### Existing MacDesk installation

Run this from **Termux**, outside Debian/PRoot:

```bash
bash "$HOME/MacDesk-V6/install.sh"
```

### New installation

The current all-in-one installer is published from the development branch:

```bash
curl -fL --retry 2 https://raw.githubusercontent.com/Jorgeprdz/MacDesk-X11/feature/macos-27-lightweight/install.sh -o "$HOME/macdesk-install.sh" && bash "$HOME/macdesk-install.sh"
```

After installation:

```bash
macdesk
```

For Android shared storage access:

```bash
termux-setup-storage
```

> The installer does **not** reset Git, reinstall Debian unnecessarily, uninstall an existing Termux:X11 APK, enable VNC, or forcibly restart an active desktop session.

---

## 🌟 Highlights

| | Feature | What it does |
|---|---|---|
| 🔄 | **Continuity** | Native Termux:X11 clipboard, Android open/share integration, storage shortcuts and desktop state helpers. |
| 🪟 | **Window Snap** | XFWM-based tiling with halves, thirds, 2×2 layouts and a lightweight selector. |
| 👀 | **Quick Look** | Fast previews for text, images, PDF, media metadata/thumbnails and archive contents. |
| 🖥️ | **Automatic Desktop Mode** | Reversible **PHONE / TABLET / DESKTOP / REMOTE** profiles with conservative environment detection. |
| 🧠 | **Memory Governor** | Detects Android visibility and trims only MacDesk-owned helpers with debounce and metrics. |
| 🔌 | **Dynamic DeX Binding** | Discovers displays dynamically and prefers DeX/external displays without hard-coding an ID or resolution. |
| 🛟 | **Recovery tooling** | Health checks, safe resume paths, ownership-aware shutdown and fallback graphics recovery. |
| ⚡ | **GPU path** | Adreno 830 → Turnip → Zink acceleration where supported, with a safe software fallback path. |

---

## 🧩 Architecture

```text
Android / Samsung DeX
        │
        ├── Termux
        │    ├── MacDesk launcher + recovery tools
        │    └── Termux:X11 integration
        │
        └── Debian (PRoot)
             ├── XFCE / XFWM
             ├── Plank
             ├── Nautilus / Sushi
             ├── Firefox ESR
             └── MacDesk smart-desktop helpers
```

MacDesk intentionally keeps the core small. The smart-desktop features share a single lightweight context instead of running several independent services.

---

## 🛠️ Installer modes

Preview the installation plan:

```bash
bash install.sh --plan
```

Run checks without installing:

```bash
bash install.sh --check
```

The installer prepares the Debian/XFCE desktop, Plank, Nautilus/Sushi, Firefox and core dependencies while reusing existing installations and preserving local changes.

Android may ask you to confirm installation of the official **Termux:X11 APK**. The Android APK and the Termux companion package are separate components; see the [official Termux:X11 setup instructions](https://github.com/termux/termux-x11#setup-instructions).

### Not installed automatically

MacDesk does not automatically install:

- Chromium
- LibreOffice
- Mailspring

Existing launchers for those applications require the corresponding application to be installed separately.

---

## ⌨️ Main commands

| Command | Purpose |
|---|---|
| `macdesk` | Start MacDesk or focus the existing V6 session. |
| `macdesk-resume` | Detect the current DeX display, focus X11 and recover the desktop only when needed. |
| `scripts/check-dex-keyboard.sh` | Run the keyboard/accessibility regression gate. |
| `scripts/measure-stability` | Inspect RSS, swap, process state and Android exit history. |
| `scripts/restart-termux-x11-safe` | Safely restart the standalone Termux:X11 environment. |
| `scripts/launch-firefox` | Launch/focus Firefox with the supported graphics path and URL/tab routing. |
| `scripts/launch-whatsapp` | Launch the isolated Chromium WhatsApp window and keyboard bridge. |
| `scripts/launch-chatgpt` | Launch the isolated Chromium ChatGPT window and keyboard bridge. |
| `scripts/plank-geometry-guard` | Realign Plank after DeX/XRandR display changes. |

---

## 📱 Current device baseline

Development and validation currently target a **Samsung Galaxy S25 (ARM64)** using DeX.

The established desktop baseline uses:

- **1920×1080**
- **100% scale**
- standalone Termux:X11
- Debian + XFCE/XFWM
- Firefox ESR as the primary browser

The previous 75% scaling experiment was removed because it produced visible pixelation.

---

## 🛟 Recovery status · 2026-09-29

Repeated desktop/Codex `SIGKILL` events were traced to Android phantom-process trimming. The development device now uses:

```text
settings_enable_monitor_phantom_procs=false
```

The following currently pass in the recovery baseline:

- normal XFCE startup
- owned stop/restart
- real X11 test window
- `SAFE_FALLBACK` software graphics
- process-ownership validation during shutdown
- fresh health validation before new launches

This recovery baseline is **not the same as full hardware acceptance**.

Physical external DeX, the complete input matrix, application coverage, full clipboard/VNC behavior and whole-session near-zero idle CPU still require current-device validation.

---

## 🧪 Validation philosophy

MacDesk uses a strict validation order:

```text
GPU
 ↓
Stable desktop
 ↓
Applications
 ↓
Android storage
 ↓
Performance
 ↓
Visuals
 ↓
Physical input
 ↓
Regression
```

A feature is not treated as accepted merely because it starts successfully.

The all-in-one installer has automated tests and has been audited against the existing development phone. A completely clean-device installation is still pending final validation.

---

## 📚 Documentation

- [Smart Desktop — commands, validation and known gaps](docs/SMART-DESKTOP.md)
- [Smart Desktop — remaining acceptance scope](docs/SMART-DESKTOP-SCOPE.md)
- [Android process recovery](docs/ANDROID-PROCESS-RECOVERY.md)
- [MacDesk V6 bug-resolution certificate](docs/MACDESK-V6-BUG-RESOLUTION-CERTIFICATE.md)

---

<details>
<summary><strong>📜 Historical acceptance · 2026-08-21</strong></summary>

<br>

Recorded status: **daily-computer and bug-resolution PASS**.

At that checkpoint, Debian, XFCE/XFWM, host VirGL, the DeX keyboard contract, dynamic display recovery, Chromium app keyboard bridges, Plank geometry recovery and the in-session health monitor had survived a full phone reboot.

Firefox ESR was validated with the Adreno 830 → Turnip → Zink path using WebRender/EGL and the Linux/XFCE port of Liquid Fox.

Zen was removed after repeated GTK/X11 freezes; its last profile backup was retained under:

```text
Download/MacDesk-Backups
```

The standalone Termux:X11 build used at that checkpoint was:

```text
1.03.01-f68cd36-21.08.26
```

The older shared-UID force-stop hazard no longer applied after separating Termux:X11 from the Termux UID.

These are **historical acceptance results**, not a claim that every newer smart-desktop feature has already completed the same hardware matrix.

</details>

---

## ⚠️ Known limitations

- Some physical DeX and external-display paths still require current-device acceptance.
- Super-key window shortcuts depend on resolving the existing keyboard conflict.
- D-Bus clients started from a separate PRoot session may not authenticate to the active desktop bus; in-session checks pass.
- The project is optimized around the current Galaxy S25/DeX development environment and should not yet be treated as universally hardware-certified.

---

<div align="center">

### MacDesk V6

**Android in your pocket. Linux on your desk.**

Built for a lightweight, recoverable DeX desktop workflow.

</div>

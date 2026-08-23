// MacDesk V6 primary Firefox profile.
user_pref("browser.download.folderList", 2);
user_pref("browser.download.dir", "/mnt/s25/Download");
user_pref("browser.download.useDownloadDir", true);
user_pref("browser.startup.page", 3);
user_pref("browser.tabs.inTitlebar", 1);
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);
// Native Firefox vertical tabs; Liquid Fox styles both expanded and collapsed
// sidebar states. The sidebar button remains available to toggle title width.
user_pref("sidebar.revamp", true);
user_pref("sidebar.verticalTabs", true);
user_pref("sidebar.visibility", "always-show");
user_pref("sidebar.position_start", true);
user_pref("sidebar.backupState", "{\"command\":\"\",\"panelOpen\":false,\"launcherExpanded\":true,\"launcherVisible\":true}");

// Adreno 830 -> Turnip -> Zink. The launcher supplies the matching Mesa/Vulkan
// environment; these preferences keep Firefox on WebRender + EGL over X11.
user_pref("gfx.webrender.all", false);
user_pref("gfx.webrender.software", true);
user_pref("gfx.x11-egl.force-enabled", false);
user_pref("gfx.x11-egl.force-disabled", true);
user_pref("layers.acceleration.disabled", true);
user_pref("layers.acceleration.force-enabled", false);
user_pref("webgl.disabled", false);
user_pref("webgl.force-enabled", true);

// PRoot does not expose a supported VA-API/Android codec bridge. Do not claim
// hardware video decoding; page composition and WebGL remain GPU accelerated.
user_pref("media.hardware-video-decoding.enabled", false);

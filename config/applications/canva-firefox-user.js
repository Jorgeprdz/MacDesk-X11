// MacDesk Canva: isolated Firefox profile. These preferences do not affect Zen.
user_pref("browser.startup.page", 1);
user_pref("browser.startup.homepage", "https://www.canva.com/?continue_in_browser=true");
user_pref("browser.aboutwelcome.enabled", false);
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.tabs.warnOnClose", false);
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

// Keep Google OAuth in this Firefox window. Separate GTK popup windows are
// unreliable in the Termux:X11 GLX path.
user_pref("browser.link.open_newwindow", 3);
user_pref("browser.link.open_newwindow.restriction", 0);

// Canva and Google authentication require cross-site cookies and DOM storage.
// This applies only to the dedicated Canva profile.
user_pref("network.cookie.cookieBehavior", 0);
user_pref("privacy.trackingprotection.enabled", false);
user_pref("privacy.trackingprotection.pbmode.enabled", false);
user_pref("dom.storage.enabled", true);
user_pref("security.webauthn.enable_conditional_mediation", false);

// Stable software rendering for Firefox ESR on Termux:X11. Canva retains
// software WebGL support, while virgl/EGL and hardware video decoding stay off.
user_pref("gfx.x11-egl.force-disabled", true);
user_pref("layers.acceleration.disabled", true);
user_pref("media.hardware-video-decoding.enabled", false);
user_pref("webgl.disabled", false);

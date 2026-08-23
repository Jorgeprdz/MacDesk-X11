// Dedicated WhatsApp profile: keep networking independent from Zen and avoid
// graphics paths that are unreliable inside the Termux:X11 virpipe guest.
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.startup.page", 0);
user_pref("browser.tabs.warnOnClose", false);
user_pref("browser.tabs.warnOnOpen", false);
user_pref("datareporting.policy.dataSubmissionPolicyBypassNotification", true);
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

user_pref("network.http.http3.enable", false);
user_pref("network.http.http2.enabled", true);
// WhatsApp's :5222 chat socket is closed immediately when Firefox negotiates
// RFC 8441 over HTTP/2 in this X11 guest. Keep HTTP/2 for page resources, but
// use the classic HTTP/1.1 Upgrade path for WebSockets.
user_pref("network.http.http2.websockets", false);
user_pref("network.http.spdy.enabled", true);
user_pref("network.trr.mode", 5);
user_pref("network.proxy.type", 0);
user_pref("network.dns.disableIPv6", true);
user_pref("network.manage-offline-status", false);

user_pref("network.cookie.cookieBehavior", 0);
user_pref("privacy.trackingprotection.enabled", false);
user_pref("privacy.trackingprotection.pbmode.enabled", false);
user_pref("privacy.partition.network_state", false);
user_pref("dom.storage.enabled", true);
// WhatsApp requests persistent IndexedDB immediately after QR login. In this
// dedicated single-site profile, grant that request without a flashing
// permission doorhanger that otherwise interrupts initialization.
user_pref("dom.storageManager.prompt.testing", true);
user_pref("dom.storageManager.prompt.testing.allow", true);

user_pref("gfx.x11-egl.force-disabled", true);
user_pref("gfx.webrender.all", false);
user_pref("layers.acceleration.disabled", true);
user_pref("media.hardware-video-decoding.enabled", false);
user_pref("webgl.disabled", true);

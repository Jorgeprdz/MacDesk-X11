# Samsung DeX Super source repair

Status: source patch prepared; not installed in the production APK.

## Exact path

1. Android delivers a `KeyEvent` to
   `InputEventSender.sendKeyEvent(KeyEvent)`.
2. That method selects either `e.getScanCode()` or `e.getKeyCode()` and calls
   `mInjector.sendKeyEvent(scancode, keyCode, pressed)`.
3. JNI `activity.cpp::sendKeyEvent` selects the scancode when nonzero,
   otherwise maps through `android_to_linux_keycode[key_code]`, then adds the
   X keycode offset of 8.
4. Android Meta-left maps to Linux `KEY_LEFTMETA` and X keycode 133; the
   Samsung-misreported Alt-left release maps to `KEY_LEFTALT` and X keycode 64.

## Patch behavior

On key-up only, an incoming `KEYCODE_ALT_LEFT` is canonicalized to the tracked
Meta key only when Alt is not tracked pressed and Meta is tracked pressed. The
corrected release forces keycode mapping rather than using the bad release
scancode.

This preserves genuine Ctrl, Shift, and Alt events, does not periodically clear
modifiers, and does not inject global/random releases. Acceptance still
requires a built APK plus raw 133/133 evidence, full es-MX input, focus/DeX
reconnect testing, and three restart cycles.

The requested short revision `50ac80f` is not reachable from current upstream
Git refs. The inspection tree is therefore current upstream commit
`1cd9d31d915d7d6dd449a2c3d11d0ed3f5a3e4eb`; production installation must pin
the exact build commit and matching companion package.

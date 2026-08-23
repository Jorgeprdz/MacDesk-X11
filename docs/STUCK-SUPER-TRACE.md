# Stuck Super modifier trace

Status: `FAIL` — isolated to the Samsung DeX / Termux:X11 translation boundary.

## Baseline failure

Static preferences were `dexMetaKeyCapture=false`,
`hardwareKbdScancodesWorkaround=true`, `preferScancodes=false`, and
`filterOutWinkey=false`.

- Raw Super press: keycode 133 (`Super_L`).
- Raw physical release: keycode 64 (`Alt_L`), not 133.
- Lorie device initially reported Super up while XI2 reported Mod4
  `base=0x40 effective=0x40`.
- The following `a` reached XI2 and `xev` with Mod4 state `0x40`.
- Reapplying the latam XKB map did not clear the mismatch.

Evidence: `logs/super-xinput-xi2.log` and `logs/super-xev.log`.

## Preference matrix

| Test | DeX capture | HW workaround | Prefer scancodes | Result |
|---|---:|---:|---:|---|
| Baseline | false | true | false | Super press 133, release 64; Mod4 stuck |
| 2 | false | false | false | No Super events; following `a` state 0 |
| 3 | true | false | false | Super 133 pairs, but unmatched Control_L 37 remains; following `a` state 4 |
| 4 | true | false | true | Physical Super becomes paired Control_L 37; following `a` state 0 |
| 5 | true | true | true | Same Control_L mapping plus stray release 133; following `a` state 0 |

Evidence: `logs/super-xinput-test2.log` through
`logs/super-xinput-test5.log` and matching `super-xev-test*.log` files.

## Layer result

- Android physical layer: direct Android down/up visibility was unavailable to
  the unprivileged shell, so it is not independently marked pass.
- Termux:X11 / Lorie: first proven failure. Raw XInput already contains mismatched
  or semantically wrong keycodes.
- XKB: correctly applies the incoming raw events; it cannot release keycode 133
  when Termux:X11 sends release 64.
- XFWM: not the source; the fault is observable before WM shortcut handling.
- Client: `xev` reproduces the XI2 state and is downstream of the fault.

## Interim state

The safe interim static state disables DeX capture, the hardware scancode
workaround, and preferred scancodes. It prevents stuck or falsely-Control
modifiers but makes Super unavailable. This is deliberately `FAIL`, not a fix.

### Safe-state regression

During the later Ctrl/Alt/accent functional trace, XI2 began at Mod4
`base=0x40 effective=0x40`; Lorie subsequently reported both keycodes 133 and
134 down even though the capture contained no raw Super press. Ordinary `e`
therefore invoked the configured Super+E/Thunar shortcut. The prior claim that
this preference combination reliably prevents latching is withdrawn: it was
only clean immediately after restart.

Permanent acceptance requires a Termux:X11/One UI translation fix that emits a
matching Super press/release pair, followed by three cold restart and DeX
reconnect cycles.

### Runtime containment (2026-08-21)

- A live recurrence reported `Lorie keyboard key[133]=down`; Ctrl_L and Ctrl_R
  remained correctly mapped, but shortcuts arrived with the extra Mod4 state.
- `scripts/input-guard` now runs after `xfsettingsd`, clears Mod4, and resets
  only the Lorie keyboard when XKB restores Mod4 after startup or reconnect.
- A forced `setxkbmap -layout latam` regression test restored three Super keys
  to Mod4; the guard detected and cleared them within its next interval.
- This restores ordinary Ctrl/Alt shortcuts while deliberately leaving Super
  unavailable. It is containment, not the permanent Termux:X11 source repair.

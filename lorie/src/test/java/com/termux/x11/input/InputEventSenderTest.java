package com.termux.x11.input;

import static android.view.KeyEvent.KEYCODE_ALT_LEFT;
import static android.view.KeyEvent.KEYCODE_CTRL_LEFT;
import static android.view.KeyEvent.KEYCODE_META_LEFT;
import static android.view.KeyEvent.KEYCODE_META_RIGHT;
import static android.view.KeyEvent.KEYCODE_SHIFT_LEFT;
import static org.junit.Assert.assertEquals;

import java.util.Set;

import org.junit.Test;

public class InputEventSenderTest {
    private static int translate(int keyCode, boolean pressed, Integer... down) {
        return InputEventSender.canonicalizeSamsungMetaRelease(
                keyCode, pressed, Set.of(down));
    }

    @Test
    public void normalAltIsUnchanged() {
        assertEquals(KEYCODE_ALT_LEFT, translate(KEYCODE_ALT_LEFT, true));
        assertEquals(KEYCODE_ALT_LEFT, translate(KEYCODE_ALT_LEFT, false, KEYCODE_ALT_LEFT));
    }

    @Test
    public void normalMetaIsUnchanged() {
        assertEquals(KEYCODE_META_LEFT, translate(KEYCODE_META_LEFT, true));
        assertEquals(KEYCODE_META_LEFT, translate(KEYCODE_META_LEFT, false, KEYCODE_META_LEFT));
    }

    @Test
    public void brokenSamsungLeftMetaReleaseIsCorrected() {
        assertEquals(KEYCODE_META_LEFT, translate(KEYCODE_ALT_LEFT, false, KEYCODE_META_LEFT));
    }

    @Test
    public void brokenSamsungRightMetaReleaseIsCorrected() {
        assertEquals(KEYCODE_META_RIGHT, translate(KEYCODE_ALT_LEFT, false, KEYCODE_META_RIGHT));
    }

    @Test
    public void realAltWhileMetaIsUnchanged() {
        assertEquals(KEYCODE_ALT_LEFT,
                translate(KEYCODE_ALT_LEFT, false, KEYCODE_META_LEFT, KEYCODE_ALT_LEFT));
    }

    @Test
    public void ctrlIsUnchanged() {
        assertEquals(KEYCODE_CTRL_LEFT, translate(KEYCODE_CTRL_LEFT, true));
        assertEquals(KEYCODE_CTRL_LEFT, translate(KEYCODE_CTRL_LEFT, false, KEYCODE_CTRL_LEFT));
    }

    @Test
    public void shiftIsUnchanged() {
        assertEquals(KEYCODE_SHIFT_LEFT, translate(KEYCODE_SHIFT_LEFT, true));
        assertEquals(KEYCODE_SHIFT_LEFT, translate(KEYCODE_SHIFT_LEFT, false, KEYCODE_SHIFT_LEFT));
    }
}

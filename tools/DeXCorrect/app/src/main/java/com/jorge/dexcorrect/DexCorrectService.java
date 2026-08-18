package com.jorge.dexcorrect;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.content.Context;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.util.Log;
import android.util.SparseArray;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.view.textservice.SentenceSuggestionsInfo;
import android.view.textservice.SpellCheckerSession;
import android.view.textservice.SuggestionsInfo;
import android.view.textservice.TextInfo;
import android.view.textservice.TextServicesManager;

import java.util.Locale;

public class DexCorrectService extends AccessibilityService
        implements SpellCheckerSession.SpellCheckerSessionListener {

    private static final String TAG = "DexCorrect";

    private final Handler handler =
            new Handler(Looper.getMainLooper());

    private final SparseArray<Pending> pendings =
            new SparseArray<>();

    private SpellCheckerSession spellSession;

    private int sequence = 1;

    /*
     * Evita que ACTION_SET_TEXT provoque otro ciclo
     * de autocorrección sobre nuestro propio cambio.
     */
    private String programmaticText;
    private int programmaticWindow = -1;
    private long programmaticUntil = 0;

    private String lastQuerySignature = "";

    private static class Pending {

        int sequence;

        String packageName;

        int windowId;

        String word;

        int wordStart;

        int wordEnd;

        Pending(
                int sequence,
                String packageName,
                int windowId,
                String word,
                int wordStart,
                int wordEnd) {

            this.sequence = sequence;
            this.packageName = packageName;
            this.windowId = windowId;
            this.word = word;
            this.wordStart = wordStart;
            this.wordEnd = wordEnd;
        }
    }

    @Override
    protected void onServiceConnected() {

        super.onServiceConnected();

        AccessibilityServiceInfo info =
                getServiceInfo();

        /*
         * v0.2:
         * ya NO necesitamos interceptar KeyEvents.
         *
         * Eso evita depender de SPACE/ENTER y evita
         * competir con Key Mapper / Essentials.
         */
        info.flags &=
                ~AccessibilityServiceInfo.FLAG_REQUEST_FILTER_KEY_EVENTS;

        info.flags |=
                AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS;

        info.eventTypes =
                AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED;

        info.feedbackType =
                AccessibilityServiceInfo.FEEDBACK_GENERIC;

        /*
         * No queremos coalescing artificial:
         * necesitamos ver el momento en que aparece
         * el espacio o puntuación.
         */
        info.notificationTimeout = 0;

        setServiceInfo(info);

        TextServicesManager tsm =
                (TextServicesManager)
                        getSystemService(
                                Context.TEXT_SERVICES_MANAGER_SERVICE
                        );

        try {

            /*
             * "es" + referToSettings=true permite que Android
             * seleccione el subtipo español configurado,
             * por ejemplo es_MX.
             */
            spellSession =
                    tsm.newSpellCheckerSession(
                            null,
                            new Locale("es"),
                            this,
                            true
                    );

        } catch (Throwable t) {

            Log.e(
                    TAG,
                    "No se pudo abrir sesión ES",
                    t
            );
        }

        if (spellSession == null) {

            try {

                spellSession =
                        tsm.newSpellCheckerSession(
                                null,
                                null,
                                this,
                                true
                        );

            } catch (Throwable t) {

                Log.e(
                        TAG,
                        "No se pudo abrir sesión fallback",
                        t
                );
            }
        }

        Log.i(
                TAG,
                "CONNECTED spellSession=" +
                        (spellSession != null)
        );
    }

    @Override
    public void onAccessibilityEvent(
            AccessibilityEvent event) {

        if (event == null) {
            return;
        }

        if (event.getEventType() !=
                AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED) {

            return;
        }

        if (spellSession == null) {
            return;
        }

        inspectTextChange(event);
    }

    private void inspectTextChange(
            AccessibilityEvent event) {

        AccessibilityNodeInfo node =
                event.getSource();

        if (node == null) {

            node =
                    findFocus(
                            AccessibilityNodeInfo.FOCUS_INPUT
                    );
        }

        if (node == null) {
            return;
        }

        if (!node.isEditable() ||
                node.isPassword()) {

            return;
        }

        CharSequence cs =
                node.getText();

        if (cs == null) {
            return;
        }

        String text =
                cs.toString();

        int windowId =
                node.getWindowId();

        /*
         * Ignorar el TYPE_VIEW_TEXT_CHANGED producido
         * por nuestro propio ACTION_SET_TEXT.
         */
        if (SystemClock.uptimeMillis()
                <= programmaticUntil &&
                windowId == programmaticWindow &&
                text.equals(programmaticText)) {

            Log.d(
                    TAG,
                    "IGNORING_OWN_CHANGE"
            );

            return;
        }

        /*
         * Una eliminación no completa una palabra.
         */
        if (event.getAddedCount() <= 0) {
            return;
        }

        int boundary =
                findInsertedBoundary(
                        event,
                        text,
                        node
                );

        if (boundary < 1 ||
                boundary > text.length()) {

            return;
        }

        /*
         * Caminamos hacia atrás desde el carácter
         * anterior al espacio/puntuación.
         */
        int i =
                boundary - 1;

        while (i >= 0 &&
                !Character.isLetter(
                        text.charAt(i))) {

            i--;
        }

        if (i < 0) {
            return;
        }

        int end =
                i + 1;

        while (i >= 0 &&
                Character.isLetter(
                        text.charAt(i))) {

            i--;
        }

        int start =
                i + 1;

        if (end <= start) {
            return;
        }

        String word =
                text.substring(
                        start,
                        end
                );

        if (word.length() < 2) {
            return;
        }

        CharSequence packageCs =
                node.getPackageName();

        String packageName =
                packageCs == null
                        ? ""
                        : packageCs.toString();

        String signature =
                packageName +
                "|" +
                windowId +
                "|" +
                start +
                "|" +
                end +
                "|" +
                word;

        if (signature.equals(
                lastQuerySignature)) {

            return;
        }

        lastQuerySignature =
                signature;

        int seq =
                sequence++;

        if (sequence >
                Integer.MAX_VALUE - 1000) {

            sequence = 1;
        }

        Pending pending =
                new Pending(
                        seq,
                        packageName,
                        windowId,
                        word,
                        start,
                        end
                );

        /*
         * No dejamos crecer indefinidamente
         * solicitudes abandonadas.
         */
        if (pendings.size() > 40) {

            pendings.removeAt(0);
        }

        pendings.put(
                seq,
                pending
        );

        Log.i(
                TAG,
                "QUERY seq=" +
                        seq +
                        " word=[" +
                        word +
                        "] pkg=" +
                        packageName +
                        " window=" +
                        windowId
        );

        try {

            /*
             * Usamos la API de sentence suggestions.
             * Aunque mandamos una palabra en v0.2,
             * nos deja preparada la arquitectura
             * para contexto completo después.
             */
            spellSession.getSentenceSuggestions(
                    new TextInfo[]{
                            new TextInfo(
                                    word,
                                    77,
                                    seq
                            )
                    },
                    5
            );

        } catch (Throwable t) {

            pendings.remove(seq);

            Log.e(
                    TAG,
                    "SPELL_REQUEST_FAILED word=" +
                            word,
                    t
            );
        }
    }

    private int findInsertedBoundary(
            AccessibilityEvent event,
            String text,
            AccessibilityNodeInfo node) {

        int from =
                event.getFromIndex();

        int added =
                event.getAddedCount();

        /*
         * Primero usamos el rango exacto que Android
         * reporta como agregado.
         */
        if (from >= 0 &&
                added > 0 &&
                from < text.length()) {

            int to =
                    Math.min(
                            text.length(),
                            from + added
                    );

            for (int i = from;
                 i < to;
                 i++) {

                if (isBoundary(
                        text.charAt(i))) {

                    return i;
                }
            }
        }

        /*
         * Fallback para apps/WebViews que reportan
         * rangos incompletos: usamos el cursor.
         */
        int cursor =
                node.getTextSelectionStart();

        if (cursor < 0 ||
                cursor > text.length()) {

            cursor =
                    text.length();
        }

        if (cursor <= 0) {
            return -1;
        }

        int candidate =
                cursor - 1;

        if (candidate >= 0 &&
                candidate < text.length() &&
                isBoundary(
                        text.charAt(candidate))) {

            return candidate;
        }

        return -1;
    }

    private boolean isBoundary(
            char c) {

        return Character.isWhitespace(c) ||
                c == '.' ||
                c == ',' ||
                c == ';' ||
                c == ':' ||
                c == '!' ||
                c == '?' ||
                c == ')' ||
                c == ']' ||
                c == '}';
    }

    @Override
    public void onGetSentenceSuggestions(
            SentenceSuggestionsInfo[] results) {

        if (results == null) {
            return;
        }

        for (SentenceSuggestionsInfo sentence :
                results) {

            if (sentence == null) {
                continue;
            }

            int count =
                    sentence.getSuggestionsCount();

            for (int i = 0;
                 i < count;
                 i++) {

                SuggestionsInfo info =
                        sentence.getSuggestionsInfoAt(i);

                if (info != null) {

                    processSuggestion(
                            info
                    );
                }
            }
        }
    }

    /*
     * Compatibilidad por si algún spell checker
     * responde mediante la ruta antigua.
     */
    @Override
    public void onGetSuggestions(
            SuggestionsInfo[] results) {

        if (results == null) {
            return;
        }

        for (SuggestionsInfo info :
                results) {

            if (info != null) {

                processSuggestion(
                        info
                );
            }
        }
    }

    private void processSuggestion(
            SuggestionsInfo info) {

        final int seq =
                info.getSequence();

        final Pending p =
                pendings.get(seq);

        if (p == null) {

            Log.d(
                    TAG,
                    "STALE_RESULT seq=" +
                            seq
            );

            return;
        }

        /*
         * Ya tenemos respuesta para esta solicitud.
         */
        pendings.remove(seq);

        int attrs =
                info.getSuggestionsAttributes();

        boolean inDictionary =
                (attrs &
                        SuggestionsInfo.RESULT_ATTR_IN_THE_DICTIONARY)
                        != 0;

        int count =
                info.getSuggestionsCount();

        Log.i(
                TAG,
                "RESULT seq=" +
                        seq +
                        " word=[" +
                        p.word +
                        "] count=" +
                        count +
                        " attrs=" +
                        attrs +
                        " dict=" +
                        inDictionary
        );

        /*
         * Si el corrector afirma que la palabra
         * ya existe en el diccionario, no la tocamos.
         */
        if (inDictionary) {
            return;
        }

        if (count <= 0) {
            return;
        }

        String replacement =
                null;

        for (int i = 0;
             i < count;
             i++) {

            String candidate =
                    info.getSuggestionAt(i);

            if (candidate == null ||
                    candidate.length() == 0) {

                continue;
            }

            candidate =
                    preserveCase(
                            p.word,
                            candidate
                    );

            if (!candidate.equals(
                    p.word)) {

                replacement =
                        candidate;

                break;
            }
        }

        if (replacement == null) {
            return;
        }

        final String correction =
                replacement;

        handler.post(
                new Runnable() {

                    @Override
                    public void run() {

                        applyCorrection(
                                p,
                                correction
                        );
                    }
                }
        );
    }

    private String preserveCase(
            String original,
            String candidate) {

        if (original == null ||
                candidate == null ||
                original.length() == 0 ||
                candidate.length() == 0) {

            return candidate;
        }

        boolean allUpper =
                original.equals(
                        original.toUpperCase(
                                new Locale(
                                        "es",
                                        "MX"
                                )
                        )
                );

        if (allUpper) {

            return candidate.toUpperCase(
                    new Locale(
                            "es",
                            "MX"
                    )
            );
        }

        if (Character.isUpperCase(
                original.charAt(0))) {

            return Character.toUpperCase(
                    candidate.charAt(0)) +
                    candidate.substring(1);
        }

        return candidate;
    }

    private void applyCorrection(
            Pending p,
            String correction) {

        AccessibilityNodeInfo node =
                findFocus(
                        AccessibilityNodeInfo.FOCUS_INPUT
                );

        if (node == null ||
                !node.isEditable() ||
                node.isPassword()) {

            Log.w(
                    TAG,
                    "APPLY_NO_FOCUS word=" +
                            p.word
            );

            return;
        }

        CharSequence packageCs =
                node.getPackageName();

        String packageName =
                packageCs == null
                        ? ""
                        : packageCs.toString();

        if (node.getWindowId()
                != p.windowId ||
                !packageName.equals(
                        p.packageName)) {

            Log.w(
                    TAG,
                    "APPLY_TARGET_CHANGED word=" +
                            p.word
            );

            return;
        }

        CharSequence currentCs =
                node.getText();

        if (currentCs == null) {
            return;
        }

        String current =
                currentCs.toString();

        /*
         * ÉSTA ES LA DIFERENCIA CLAVE DE v0.2:
         *
         * no exigimos que TODO el mensaje siga
         * idéntico.
         *
         * Sólo comprobamos que la palabra que
         * queremos corregir siga en su sitio.
         */
        if (p.wordStart < 0 ||
                p.wordEnd >
                        current.length() ||
                p.wordEnd <=
                        p.wordStart) {

            Log.w(
                    TAG,
                    "APPLY_RANGE_INVALID word=" +
                            p.word
            );

            return;
        }

        String currentWord =
                current.substring(
                        p.wordStart,
                        p.wordEnd
                );

        if (!currentWord.equals(
                p.word)) {

            Log.w(
                    TAG,
                    "APPLY_WORD_CHANGED expected=[" +
                            p.word +
                            "] current=[" +
                            currentWord +
                            "]"
            );

            return;
        }

        String newText =
                current.substring(
                        0,
                        p.wordStart
                ) +
                correction +
                current.substring(
                        p.wordEnd
                );

        int delta =
                correction.length() -
                        p.word.length();

        int cursor =
                node.getTextSelectionStart();

        if (cursor < 0 ||
                cursor >
                        current.length()) {

            cursor =
                    current.length();
        }

        int newCursor =
                cursor;

        if (cursor >=
                p.wordEnd) {

            newCursor +=
                    delta;
        }

        if (newCursor < 0) {

            newCursor = 0;
        }

        if (newCursor >
                newText.length()) {

            newCursor =
                    newText.length();
        }

        Bundle setText =
                new Bundle();

        setText.putCharSequence(
                AccessibilityNodeInfo
                        .ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                newText
        );

        programmaticText =
                newText;

        programmaticWindow =
                node.getWindowId();

        programmaticUntil =
                SystemClock.uptimeMillis()
                        + 750;

        boolean ok =
                node.performAction(
                        AccessibilityNodeInfo.ACTION_SET_TEXT,
                        setText
                );

        Log.i(
                TAG,
                "APPLY [" +
                        p.word +
                        "] -> [" +
                        correction +
                        "] ok=" +
                        ok
        );

        if (!ok) {

            programmaticText = null;
            programmaticWindow = -1;
            programmaticUntil = 0;

            return;
        }

        /*
         * ACTION_SET_TEXT deja normalmente
         * el cursor al final; lo devolvemos al
         * punto donde el usuario estaba escribiendo.
         */
        Bundle selection =
                new Bundle();

        selection.putInt(
                AccessibilityNodeInfo
                        .ACTION_ARGUMENT_SELECTION_START_INT,
                newCursor
        );

        selection.putInt(
                AccessibilityNodeInfo
                        .ACTION_ARGUMENT_SELECTION_END_INT,
                newCursor
        );

        node.performAction(
                AccessibilityNodeInfo.ACTION_SET_SELECTION,
                selection
        );

        /*
         * Si esta corrección cambió la longitud
         * (ej. cmo -> como), desplazamos los índices
         * de solicitudes posteriores.
         */
        shiftLaterPendings(
                p,
                delta
        );
    }

    private void shiftLaterPendings(
            Pending applied,
            int delta) {

        if (delta == 0) {
            return;
        }

        for (int i = 0;
             i < pendings.size();
             i++) {

            Pending q =
                    pendings.valueAt(i);

            if (q == null) {
                continue;
            }

            if (q.windowId !=
                    applied.windowId) {

                continue;
            }

            if (!q.packageName.equals(
                    applied.packageName)) {

                continue;
            }

            if (q.wordStart >=
                    applied.wordEnd) {

                q.wordStart +=
                        delta;

                q.wordEnd +=
                        delta;
            }
        }
    }

    @Override
    public void onInterrupt() {
    }

    @Override
    public void onDestroy() {

        pendings.clear();

        if (spellSession != null) {

            try {

                spellSession.close();

            } catch (Throwable ignored) {
            }
        }

        super.onDestroy();
    }
}

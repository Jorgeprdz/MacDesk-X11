package com.macdesk.remote;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class MainActivity extends Activity {
    private static final String HOST = "100.108.132.112";
    private static final int PORT = 5902;
    private static final String CONTROL =
            "/data/data/com.termux/files/home/MacDesk-V6/scripts/macdesk-remote-app-control";
    private static final String TERMUX_PACKAGE = "com.termux";
    private static final String TERMUX_SERVICE = "com.termux.app.RunCommandService";
    private static final String RUN_ACTION = "com.termux.RUN_COMMAND";
    private static final String EXTRA_PATH = "com.termux.RUN_COMMAND_PATH";
    private static final String EXTRA_ARGS = "com.termux.RUN_COMMAND_ARGUMENTS";
    private static final String EXTRA_WORKDIR = "com.termux.RUN_COMMAND_WORKDIR";
    private static final String EXTRA_BACKGROUND = "com.termux.RUN_COMMAND_BACKGROUND";

    private final Handler main = new Handler(Looper.getMainLooper());
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private TextView badge;
    private TextView detail;
    private Button startButton;
    private Button stopButton;
    private Button refreshButton;
    private boolean firstCheck = true;
    private boolean commandPending = false;
    private int pollRemaining = 0;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        setContentView(buildContent());
        refreshState(true);
    }

    @Override
    protected void onDestroy() {
        worker.shutdownNow();
        super.onDestroy();
    }

    private View buildContent() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setPadding(dp(28), dp(48), dp(28), dp(28));
        root.setBackgroundColor(Color.rgb(244, 247, 250));

        TextView title = text("MacDesk Remote", 30, Color.rgb(16, 24, 32));
        title.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        root.addView(title, matchWrap(0, dp(12)));

        TextView subtitle = text("Galaxy S25 · escritorio compartido", 15, Color.rgb(74, 86, 96));
        subtitle.setGravity(Gravity.CENTER);
        root.addView(subtitle, matchWrap(0, dp(28)));

        badge = text("COMPROBANDO…", 18, Color.WHITE);
        badge.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        badge.setGravity(Gravity.CENTER);
        badge.setPadding(dp(18), dp(14), dp(18), dp(14));
        badge.setBackgroundColor(Color.rgb(96, 108, 118));
        root.addView(badge, matchWrap(0, 0));

        detail = text(HOST + ":" + PORT + "\nVncAuth · mismo DISPLAY :2", 16,
                Color.rgb(49, 59, 67));
        detail.setGravity(Gravity.CENTER);
        detail.setLineSpacing(0, 1.25f);
        root.addView(detail, matchWrap(dp(26), dp(26)));

        startButton = button("Iniciar Remote");
        startButton.setOnClickListener(v -> runRemoteCommand("start"));
        root.addView(startButton, matchWrap(0, dp(10)));

        stopButton = button("Detener Remote");
        stopButton.setOnClickListener(v -> runRemoteCommand("stop"));
        root.addView(stopButton, matchWrap(0, dp(10)));

        refreshButton = button("Actualizar estado");
        refreshButton.setOnClickListener(v -> refreshState(false));
        root.addView(refreshButton, matchWrap(0, dp(24)));

        TextView note = text(
                "Detener Remote sólo apaga el acceso VNC.\nMacDesk, XFCE, Plank y tus ventanas permanecen abiertos.",
                14, Color.rgb(74, 86, 96));
        note.setGravity(Gravity.CENTER);
        note.setLineSpacing(0, 1.25f);
        root.addView(note, matchWrap(0, 0));
        return root;
    }

    private TextView text(String value, int sp, int color) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(sp);
        view.setTextColor(color);
        return view;
    }

    private Button button(String label) {
        Button button = new Button(this);
        button.setText(label);
        button.setTextSize(15);
        button.setAllCaps(false);
        return button;
    }

    private LinearLayout.LayoutParams matchWrap(int top, int bottom) {
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        params.topMargin = top;
        params.bottomMargin = bottom;
        return params;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private void refreshState(boolean autoStartIfOff) {
        setBusy("COMPROBANDO…");
        worker.execute(() -> {
            boolean online = isRemoteOnline();
            main.post(() -> {
                if (online) {
                    commandPending = false;
                    showOnline();
                } else if (autoStartIfOff && firstCheck) {
                    firstCheck = false;
                    runRemoteCommand("start");
                } else {
                    commandPending = false;
                    showOffline();
                }
                firstCheck = false;
            });
        });
    }

    private boolean isRemoteOnline() {
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress(HOST, PORT), 850);
            return true;
        } catch (Exception ignored) {
            return false;
        }
    }

    private void runRemoteCommand(String action) {
        if (commandPending) return;
        if (!isTermuxInstalled()) {
            showError("Termux no está instalado");
            return;
        }
        commandPending = true;
        setBusy(action.equals("start") ? "INICIANDO…" : "DETENIENDO…");
        try {
            Intent intent = new Intent(RUN_ACTION);
            intent.setComponent(new ComponentName(TERMUX_PACKAGE, TERMUX_SERVICE));
            intent.putExtra(EXTRA_PATH, CONTROL);
            intent.putExtra(EXTRA_ARGS, new String[]{action});
            intent.putExtra(EXTRA_WORKDIR,
                    "/data/data/com.termux/files/home/MacDesk-V6");
            intent.putExtra(EXTRA_BACKGROUND, true);
            startService(intent);
            // Safe stop closes both input bridges before X0tigervnc.
            pollRemaining = action.equals("start") ? 45 : 45;
            pollForExpectedState(action.equals("start"));
        } catch (Exception error) {
            commandPending = false;
            showError("Termux rechazó el comando: " + error.getClass().getSimpleName());
        }
    }

    private void pollForExpectedState(boolean expectedOnline) {
        worker.execute(() -> {
            boolean online = isRemoteOnline();
            main.post(() -> {
                if (online == expectedOnline) {
                    commandPending = false;
                    if (online) showOnline(); else showOffline();
                    return;
                }
                if (--pollRemaining <= 0) {
                    commandPending = false;
                    showError(expectedOnline
                            ? "Remote no inició. Revisa el log en Termux."
                            : "Remote continúa activo. Revisa el log en Termux.");
                    return;
                }
                main.postDelayed(() -> pollForExpectedState(expectedOnline), 1000);
            });
        });
    }

    private boolean isTermuxInstalled() {
        try {
            getPackageManager().getPackageInfo(TERMUX_PACKAGE, 0);
            return true;
        } catch (PackageManager.NameNotFoundException ignored) {
            return false;
        }
    }

    private void setBusy(String state) {
        badge.setText(state);
        badge.setBackgroundColor(Color.rgb(230, 126, 34));
        startButton.setEnabled(false);
        stopButton.setEnabled(false);
        refreshButton.setEnabled(false);
    }

    private void showOnline() {
        badge.setText("REMOTE ACTIVO");
        badge.setBackgroundColor(Color.rgb(30, 142, 76));
        detail.setText(HOST + ":" + PORT + "\nVncAuth · SAME EXISTING MACDESK");
        startButton.setEnabled(false);
        stopButton.setEnabled(true);
        refreshButton.setEnabled(true);
    }

    private void showOffline() {
        badge.setText("REMOTE APAGADO");
        badge.setBackgroundColor(Color.rgb(95, 105, 115));
        detail.setText(HOST + ":" + PORT + "\nMacDesk no se comparte remotamente");
        startButton.setEnabled(true);
        stopButton.setEnabled(false);
        refreshButton.setEnabled(true);
    }

    private void showError(String message) {
        badge.setText("REVISIÓN NECESARIA");
        badge.setBackgroundColor(Color.rgb(183, 28, 28));
        detail.setText(message);
        startButton.setEnabled(true);
        stopButton.setEnabled(true);
        refreshButton.setEnabled(true);
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
    }
}

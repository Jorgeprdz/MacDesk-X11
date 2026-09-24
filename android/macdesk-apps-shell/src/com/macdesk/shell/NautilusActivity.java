package com.macdesk.shell;

import android.app.Activity;
import android.app.ActivityManager;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.TextView;
import android.widget.Toast;

public final class NautilusActivity extends Activity implements SurfaceHolder.Callback {
    private static final String TERMUX_PACKAGE = "com.termux";
    private static final String TERMUX_SERVICE = "com.termux.app.RunCommandService";
    private static final String RUN_ACTION = "com.termux.RUN_COMMAND";
    private static final String EXTRA_PATH = "com.termux.RUN_COMMAND_PATH";
    private static final String EXTRA_ARGS = "com.termux.RUN_COMMAND_ARGUMENTS";
    private static final String EXTRA_WORKDIR = "com.termux.RUN_COMMAND_WORKDIR";
    private static final String EXTRA_BACKGROUND = "com.termux.RUN_COMMAND_BACKGROUND";
    private static final String LAUNCHER =
            "/data/data/com.termux/files/home/MacDesk-V6/scripts/launch-nautilus-app";
    private static final String WORKDIR =
            "/data/data/com.termux/files/home/MacDesk-V6";

    private TextView status;
    private boolean launchRequested;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        setTaskDescription(new ActivityManager.TaskDescription("Files"));
        setContentView(buildContent());

        if (state == null) {
            requestNautilus();
        }
    }

    private FrameLayout buildContent() {
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.rgb(17, 19, 24));

        SurfaceView surface = new SurfaceView(this);
        surface.setBackgroundColor(Color.rgb(17, 19, 24));
        surface.getHolder().addCallback(this);
        root.addView(surface, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        status = new TextView(this);
        status.setText("Preparing Files…");
        status.setTextColor(Color.WHITE);
        status.setTextSize(15);
        status.setGravity(Gravity.CENTER);
        status.setPadding(dp(24), dp(16), dp(24), dp(16));
        status.setBackgroundColor(Color.argb(205, 24, 27, 33));

        FrameLayout.LayoutParams overlay = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT,
                Gravity.CENTER);
        root.addView(status, overlay);
        return root;
    }

    private void requestNautilus() {
        if (launchRequested) return;
        launchRequested = true;

        if (!isInstalled(TERMUX_PACKAGE)) {
            showError("Termux runtime not found");
            return;
        }

        try {
            Intent command = new Intent(RUN_ACTION);
            command.setComponent(new ComponentName(TERMUX_PACKAGE, TERMUX_SERVICE));
            command.putExtra(EXTRA_PATH, LAUNCHER);
            command.putExtra(EXTRA_ARGS, new String[0]);
            command.putExtra(EXTRA_WORKDIR, WORKDIR);
            command.putExtra(EXTRA_BACKGROUND, true);
            startService(command);
            setStatus("Nautilus runtime started\nWaiting for X11 → Android surface bridge");
        } catch (Exception error) {
            showError("Runtime launch failed: " + error.getClass().getSimpleName());
        }
    }

    private boolean isInstalled(String packageName) {
        try {
            getPackageManager().getPackageInfo(packageName, 0);
            return true;
        } catch (PackageManager.NameNotFoundException ignored) {
            return false;
        }
    }

    private void setStatus(String message) {
        if (status != null) status.setText(message);
    }

    private void showError(String message) {
        setStatus(message);
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    @Override
    public void surfaceCreated(SurfaceHolder holder) {
        // This Surface is intentionally owned by the Nautilus Android Task.
        // M1 will attach the matching top-level X window here without ever
        // opening the Termux:X11 desktop Activity.
        setStatus(launchRequested
                ? "Nautilus runtime started\nWaiting for X11 → Android surface bridge"
                : "Surface ready");
    }

    @Override
    public void surfaceChanged(SurfaceHolder holder, int format, int width, int height) {
        // M1: forward Android task geometry to the X11 top-level window.
    }

    @Override
    public void surfaceDestroyed(SurfaceHolder holder) {
        // Do not kill the shared apps runtime here. Android may recreate the
        // Activity during DeX resizing or display migration.
    }
}

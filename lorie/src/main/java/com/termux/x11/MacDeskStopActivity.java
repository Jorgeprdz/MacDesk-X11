package com.termux.x11;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;

public class MacDeskStopActivity extends Activity {
    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Intent command = new Intent();
        command.setClassName("com.termux", "com.termux.app.RunCommandService");
        command.setAction("com.termux.RUN_COMMAND");
        command.putExtra("com.termux.RUN_COMMAND_PATH",
                "/data/data/com.termux/files/usr/bin/bash");
        command.putExtra("com.termux.RUN_COMMAND_ARGUMENTS",
                new String[]{"-lc",
                        "if command -v macdesk-stop >/dev/null 2>&1; then exec macdesk-stop; " +
                        "elif [ -x \"$HOME/bin/macdesk-stop\" ]; then exec \"$HOME/bin/macdesk-stop\"; " +
                        "else exit 127; fi"});
        command.putExtra("com.termux.RUN_COMMAND_WORKDIR",
                "/data/data/com.termux/files/home");
        command.putExtra("com.termux.RUN_COMMAND_BACKGROUND", true);
        try {
            startService(command);
        } catch (Throwable e) {
            Log.e("MacDesk", "Unable to stop MacDesk", e);
        }
        finishAndRemoveTask();
    }
}

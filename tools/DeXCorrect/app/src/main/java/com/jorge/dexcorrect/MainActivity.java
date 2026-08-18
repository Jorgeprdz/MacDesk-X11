package com.jorge.dexcorrect;

import android.app.Activity;
import android.os.Bundle;
import android.provider.Settings;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class MainActivity extends Activity {

    private int dp(float v) {
        return (int)(v * getResources().getDisplayMetrics().density + 0.5f);
    }

    @Override
    public void onCreate(Bundle b) {
        super.onCreate(b);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setPadding(dp(28), dp(48), dp(28), dp(28));
        root.setBackgroundColor(Color.rgb(247,247,247));

        TextView icon = new TextView(this);
        icon.setText("✨");
        icon.setTextSize(54);
        icon.setGravity(Gravity.CENTER);
        root.addView(icon);

        TextView title = new TextView(this);
        title.setText("DeX Correct");
        title.setTextSize(30);
        title.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        title.setTextColor(Color.rgb(25,25,25));
        title.setGravity(Gravity.CENTER);
        title.setPadding(0, dp(10), 0, dp(8));
        root.addView(title);

        TextView body = new TextView(this);
        body.setText(
            "Autocorrección para el teclado físico de DeX.\n\n" +
            "Gboard sigue siendo tu teclado.\n\n" +
            "Prueba después:\n" +
            "tambien informacion rapido cmo estas"
        );
        body.setTextSize(17);
        body.setTextColor(Color.rgb(70,70,70));
        body.setGravity(Gravity.CENTER);
        body.setPadding(0, dp(10), 0, dp(30));
        root.addView(body);

        Button button = new Button(this);
        button.setText("ACTIVAR DEX CORRECT");
        button.setTextSize(15);
        button.setAllCaps(false);

        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));
            }
        });

        root.addView(button);

        setContentView(root);
    }
}

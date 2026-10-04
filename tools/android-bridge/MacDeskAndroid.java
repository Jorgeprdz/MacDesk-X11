import android.content.*;
import android.content.pm.*;
import android.graphics.*;
import android.graphics.drawable.Drawable;
import android.media.AudioManager;
import android.os.BatteryManager;
import android.provider.Settings;
import org.json.*;
import java.io.*;
import java.util.*;
import java.security.MessageDigest;

public final class MacDeskAndroid {
    static Context context() throws Exception {
        Class<?> thread = Class.forName("android.app.ActivityThread");
        java.lang.reflect.Constructor<?> constructor = thread.getDeclaredConstructor();
        constructor.setAccessible(true);
        Object instance = constructor.newInstance();
        java.lang.reflect.Field current = thread.getDeclaredField("sCurrentActivityThread");
        current.setAccessible(true); current.set(null, instance);
        Class<?> internal = Class.forName("android.app.ActivityThreadInternal");
        java.lang.reflect.Constructor<?> configuration = Class.forName("android.app.ConfigurationController").getDeclaredConstructor(internal);
        configuration.setAccessible(true);
        java.lang.reflect.Field controller = thread.getDeclaredField("mConfigurationController");
        controller.setAccessible(true); controller.set(instance, configuration.newInstance(instance));
        Context system = (Context) thread.getMethod("getSystemContext").invoke(instance);
        return system.createPackageContext("com.termux", Context.CONTEXT_IGNORE_SECURITY);
    }
    static String key(String component) throws Exception {
        byte[] bytes = MessageDigest.getInstance("SHA-256").digest(component.getBytes("UTF-8"));
        StringBuilder result = new StringBuilder();
        for (int i=0;i<12;i++) result.append(String.format("%02x", bytes[i]));
        return result.toString();
    }
    public static void main(String[] args) throws Exception {
        android.os.Looper.prepareMainLooper();
        Context context = context();
        if (args.length > 0 && args[0].equals("status")) {
            JSONObject state = new JSONObject();
            AudioManager audio = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
            state.put("volume", audio.getStreamVolume(AudioManager.STREAM_MUSIC));
            state.put("volume_max", audio.getStreamMaxVolume(AudioManager.STREAM_MUSIC));
            state.put("brightness", Settings.System.getInt(context.getContentResolver(), Settings.System.SCREEN_BRIGHTNESS, 128));
            Intent battery = context.registerReceiver(null, new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
            if (battery != null) {
                state.put("battery", battery.getIntExtra(BatteryManager.EXTRA_LEVEL,-1)*100 / Math.max(1,battery.getIntExtra(BatteryManager.EXTRA_SCALE,100)));
                state.put("charging", battery.getIntExtra(BatteryManager.EXTRA_PLUGGED,0)!=0);
            }
            System.out.println(state.toString());
            return;
        }
        File destination = new File(args[0]);
        File icons = new File(destination,"icons"); icons.mkdirs();
        PackageManager pm = context.getPackageManager();
        Intent main = new Intent(Intent.ACTION_MAIN); main.addCategory(Intent.CATEGORY_LAUNCHER);
        List<ResolveInfo> entries = pm.queryIntentActivities(main, 0);
        Map<String, JSONObject> apps = new TreeMap<>();
        for (ResolveInfo entry : entries) {
            ActivityInfo info = entry.activityInfo;
            if (!info.exported || !info.enabled || !info.applicationInfo.enabled || apps.containsKey(info.packageName)) continue;
            String component = new ComponentName(info.packageName,info.name).flattenToShortString();
            try {
                Drawable drawable = pm.getDrawable(info.packageName, entry.getIconResource(), info.applicationInfo);
                if (drawable == null) drawable = pm.getDefaultActivityIcon();
                Bitmap bitmap = Bitmap.createBitmap(128,128,Bitmap.Config.ARGB_8888);
                Canvas canvas = new Canvas(bitmap); drawable.setBounds(0,0,128,128); drawable.draw(canvas);
                String filename = key(component)+".png";
                try (FileOutputStream out = new FileOutputStream(new File(icons, filename))) {
                    bitmap.compress(Bitmap.CompressFormat.PNG,100,out);
                }
                bitmap.recycle();
                JSONObject app = new JSONObject();
                app.put("package",info.packageName); app.put("component",component);
                app.put("label",entry.loadLabel(pm).toString()); app.put("icon","icons/"+filename);
                apps.put(info.packageName, app);
            } catch (Exception e) { System.err.println("Skipping "+info.packageName+": "+e); }
        }
        JSONObject result = new JSONObject(); result.put("version",1); result.put("updated",System.currentTimeMillis());
        result.put("apps",new JSONArray(apps.values()));
        File temporary = new File(destination,"catalog.json.tmp");
        try(FileOutputStream out=new FileOutputStream(temporary)) {out.write(result.toString().getBytes("UTF-8"));}
        if (!temporary.renameTo(new File(destination,"catalog.json"))) throw new IOException("Cannot replace catalog");
        System.out.println("{\"ok\":true,\"count\":"+apps.size()+"}");
    }
}

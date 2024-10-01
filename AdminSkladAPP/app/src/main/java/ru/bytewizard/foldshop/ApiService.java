package ru.bytewizard.foldshop;

import android.content.Context;
import android.content.Intent;
import android.os.Handler;
import android.os.Looper;
import android.widget.Toast;
import java.io.IOException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.concurrent.TimeUnit;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import okhttp3.MediaType;
import android.content.SharedPreferences;
import org.json.JSONException;
import org.json.JSONObject;

public class ApiService {
    private static final String API_URL = "http://192.168.31.51:8000";
    private static final Handler handler = new Handler(Looper.getMainLooper());

    public static void login(MainActivity mainActivity, String username, String token) {
        String hashedToken = hashPassword(token);

        OkHttpClient client = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .build();

        String url = API_URL + "/authfold";

        // Формируем тело запроса
        JSONObject jsonBody = new JSONObject();
        try {
            jsonBody.put("username", username);
            jsonBody.put("token_hash", hashedToken);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        RequestBody body = RequestBody.create(
                jsonBody.toString(),
                MediaType.get("application/json; charset=utf-8")
        );

        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                handler.post(() -> showError(mainActivity, "Ошибка подключения"));
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (response.isSuccessful()) {
                    String responseBody = response.body().string();
                    handler.post(() -> {
                        // Обработка успешного ответа
                        mainActivity.runOnUiThread(() -> {
                            Toast.makeText(mainActivity, "Успешная авторизация", Toast.LENGTH_SHORT).show();
                            // Перейти в другую активность или сохранить токен
                        });
                    });
                } else {
                    handler.post(() -> showError(mainActivity, "Неверные данные"));
                }
            }
        });
    }

    private static String hashPassword(String password) {
        String salt = "vG#Qj8p$!rF3z7M&AyTn2cL*wU5eK?xH-VdR%jN$PqX6ZoB@C4pT9!k^u1YjVmL";
        String saltedPassword = password + salt;
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-512");
            byte[] hashedBytes = digest.digest(saltedPassword.getBytes());
            StringBuilder hexString = new StringBuilder();
            for (byte b : hashedBytes) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    private static void showError(Context context, String message) {
        handler.post(() -> Toast.makeText(context, message, Toast.LENGTH_LONG).show());
    }
}

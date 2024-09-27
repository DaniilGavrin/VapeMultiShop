package ru.bytewizard.vapeshop;

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
import android.content.Context;
import android.content.SharedPreferences;
import org.json.JSONObject;

public class ApiService {

    private static final String API_URL = "http://192.168.31.51:8000";
    private static final Handler handler = new Handler(Looper.getMainLooper());

    private static void saveUserData(Context context, String userData) {
        SharedPreferences sharedPreferences = context.getSharedPreferences("UserPrefs", Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = sharedPreferences.edit();

        try {
            // Парсинг JSON-ответа
            JSONObject jsonObject = new JSONObject(userData);

            // Извлекаем данные пользователя из JSON
            String username = jsonObject.getString("username");
            String email = jsonObject.getString("email");
            String token = jsonObject.getString("token");
            String userId = jsonObject.getString("user_id");  // Пример дополнительных данных
            String cartId = jsonObject.optString("cart_id", null);  // Если может быть null

            // Сохраняем данные в SharedPreferences
            editor.putString("username", username);
            editor.putString("email", email);
            editor.putString("token", token);
            editor.putString("user_id", userId);
            editor.putString("cart_id", cartId); // Сохранение, если поле присутствует
            editor.apply();  // Применяем изменения

        } catch (Exception e) {
            e.printStackTrace();
            showError(context, "Ошибка при сохранении данных пользователя.");
            }
        }

    public static void login(Context context, String username, String password) {
        String hashedPassword = hashPassword(password);

        OkHttpClient client = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .build();

        String url = API_URL + "/login";

        RequestBody body = RequestBody.create(
                MediaType.parse("application/json"),
                "{\"username\":\"" + username + "\", \"password\":\"" + hashedPassword + "\"}"
        );

        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                showError(context, "Ошибка подключения к API: " + e.getMessage());
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (!response.isSuccessful()) {
                    showError(context, "Ошибка авторизации: " + response.message());
                } else {
                    // Пример парсинга ответа от API
                    String userData = response.body().string(); // Ответ в формате JSON

                    // Сохранение информации о пользователе в SharedPreferences
                    saveUserData(context, userData);

                    // Перенаправление на другое Activity после успешной авторизации
                    Intent intent = new Intent(context, HomeActivity.class);
                    context.startActivity(intent);
                }
            }
        });
    }

    private static String hashPassword(String password) {
        String salt = "bB_eygUmMRpIuevFoMGU-mv_FDHhKsdM";
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
        // Показать уведомление об ошибке в главном потоке
        handler.post(() -> Toast.makeText(context, message, Toast.LENGTH_LONG).show());
    }
}

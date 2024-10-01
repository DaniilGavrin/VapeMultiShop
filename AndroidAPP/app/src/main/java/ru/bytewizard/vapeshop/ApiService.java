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
import android.content.SharedPreferences;
import org.json.JSONException;
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
            JSONObject dataObject = jsonObject.getJSONObject("data");

            // Извлекаем данные пользователя из JSON
            editor.putInt("id", dataObject.getInt("id")); // id скорее всего число
            editor.putString("user_id", dataObject.optString("user_id", null)); // Может быть null
            editor.putString("username", dataObject.getString("username"));
            editor.putString("email", dataObject.getString("email"));
            editor.putString("token", dataObject.getString("token"));
            editor.putString("cart_id", dataObject.optString("cart_id", null)); // Может быть null

            // Применяем изменения
            editor.apply();

        } catch (JSONException e) {
            e.printStackTrace();
            showError(context, "Ошибка при парсинге данных пользователя.");
        }
    }

    public static void register(Context context, String username, String password, String email) {
        String hashedPassword = hashPassword(password);

        OkHttpClient client = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .build();

        String url = API_URL + "/register";  // Проверьте правильность URL

        // Формируем тело запроса
        JSONObject jsonBody = new JSONObject();
        try {
            jsonBody.put("username", username);
            jsonBody.put("password_hash", hashedPassword);
            jsonBody.put("email", email);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        RequestBody body = RequestBody.create(
                MediaType.parse("application/json"),
                jsonBody.toString()  // Преобразуем JSON в строку
        );

        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .build();

        // Логирование отправляемых данных
        System.out.println("Register Request JSON: " + jsonBody.toString());

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                showError(context, "Ошибка подключения к API: " + e.getMessage());
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (!response.isSuccessful()) {
                    String errorResponse = response.body().string();
                    showError(context, "Ошибка регистрации: " + errorResponse);

                    // Логирование ответа сервера
                    System.out.println("Register Response Error: " + errorResponse);
                } else {
                    String userData = response.body().string(); // Ответ в формате JSON
                    saveUserData(context, userData); // Сохранение информации о пользователе в SharedPreferences

                    // Перенаправление на другое Activity после успешной регистрации
                    Intent intent = new Intent(context, HomeActivity.class);
                    context.startActivity(intent);
                }
            }
        });
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
                    String userData = response.body().string(); // Ответ в формате JSON
                    saveUserData(context, userData); // Сохранение информации о пользователе в SharedPreferences

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

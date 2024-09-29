package ru.bytewizard.vapeshop;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

public class RegisterActivity extends AppCompatActivity {

    // Переменные для полей ввода
    private EditText usernameEditText;
    private EditText emailEditText;
    private EditText passwordEditText;
    private EditText confirmPasswordEditText;
    private Button registerButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        // Привязка элементов интерфейса к переменным
        usernameEditText = findViewById(R.id.username);
        emailEditText = findViewById(R.id.mail);
        passwordEditText = findViewById(R.id.password);
        confirmPasswordEditText = findViewById(R.id.replaypassword);
        registerButton = findViewById(R.id.register_button);

        // Логика для кнопки регистрации
        registerButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Получение введенных данных
                String username = usernameEditText.getText().toString().trim();
                String email = emailEditText.getText().toString().trim();
                String password = passwordEditText.getText().toString().trim();
                String confirmPassword = confirmPasswordEditText.getText().toString().trim();

                // Проверка на заполненность полей
                if (TextUtils.isEmpty(username) || TextUtils.isEmpty(email) || TextUtils.isEmpty(password) || TextUtils.isEmpty(confirmPassword)) {
                    Toast.makeText(RegisterActivity.this, "Заполните все поля", Toast.LENGTH_SHORT).show();
                    return;
                }

                // Проверка на совпадение паролей
                if (!password.equals(confirmPassword)) {
                    Toast.makeText(RegisterActivity.this, "Пароли не совпадают", Toast.LENGTH_SHORT).show();
                    return;
                }

                // Вызов метода регистрации из ApiService
                ApiService.register(RegisterActivity.this, username, password, email);
            }
        });
    }
}

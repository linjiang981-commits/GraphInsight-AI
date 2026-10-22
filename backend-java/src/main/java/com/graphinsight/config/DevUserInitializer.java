package com.graphinsight.config;

import com.graphinsight.entity.User;
import com.graphinsight.repository.UserRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import java.nio.charset.StandardCharsets;

@Component
@Profile("dev")
public class DevUserInitializer implements CommandLineRunner {
    private final UserRepository users;
    private final PasswordEncoder passwords;
    private final String username;
    private final String password;

    public DevUserInitializer(
            UserRepository users, PasswordEncoder passwords,
            @Value("${app.demo.username}") String username,
            @Value("${app.demo.password}") String password
    ) {
        this.users = users;
        this.passwords = passwords;
        this.username = username;
        this.password = password;
    }

    @Override
    public void run(String... args) {
        if (users.findByUsername(username).isPresent()) { return; }
        if (username.isBlank() || username.length() > 64) {
            throw new IllegalArgumentException("Invalid demo username");
        }
        if (password.length() < 12 || password.getBytes(StandardCharsets.UTF_8).length > 72) {
            throw new IllegalArgumentException("Demo password needs 12+ characters and at most 72 UTF-8 bytes");
        }
        users.save(new User(username, passwords.encode(password)));
    }
}

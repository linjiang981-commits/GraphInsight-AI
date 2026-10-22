package com.graphinsight.service;

import com.graphinsight.dto.LoginResponse;
import com.graphinsight.dto.UserResponse;
import com.graphinsight.entity.User;
import com.graphinsight.repository.UserRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.JwsHeader;
import org.springframework.security.oauth2.jwt.JwtClaimsSet;
import org.springframework.security.oauth2.jwt.JwtEncoder;
import org.springframework.security.oauth2.jwt.JwtEncoderParameters;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.List;

@Service
@Transactional(readOnly = true)
public class AuthService {
    private final UserRepository users;
    private final PasswordEncoder passwords;
    private final JwtEncoder encoder;
    private final String issuer;
    private final String audience;
    private final long ttlSeconds;

    public AuthService(
            UserRepository users, PasswordEncoder passwords, JwtEncoder encoder,
            @Value("${app.jwt.issuer}") String issuer,
            @Value("${app.jwt.audience}") String audience,
            @Value("${app.jwt.ttl-seconds}") long ttlSeconds
    ) {
        if (ttlSeconds < 1 || ttlSeconds > 86400) {
            throw new IllegalArgumentException("JWT TTL must be between 1 and 86400 seconds");
        }
        this.users = users;
        this.passwords = passwords;
        this.encoder = encoder;
        this.issuer = issuer;
        this.audience = audience;
        this.ttlSeconds = ttlSeconds;
    }

    public LoginResponse login(String username, String password) {
        if (password.getBytes(StandardCharsets.UTF_8).length > 72) {
            throw new BadCredentialsException("Invalid credentials");
        }
        User user = users.findByUsername(username)
                .orElseThrow(() -> new BadCredentialsException("Invalid credentials"));
        if (!passwords.matches(password, user.getPasswordHash())) {
            throw new BadCredentialsException("Invalid credentials");
        }
        Instant now = Instant.now();
        JwtClaimsSet claims = JwtClaimsSet.builder()
                .issuer(issuer).subject(user.getId().toString())
                .audience(List.of(audience)).issuedAt(now)
                .expiresAt(now.plusSeconds(ttlSeconds))
                .claim("username", user.getUsername()).claim("scope", "ai:chat")
                .build();
        JwsHeader header = JwsHeader.with(MacAlgorithm.HS256).build();
        String token = encoder.encode(JwtEncoderParameters.from(header, claims)).getTokenValue();
        return new LoginResponse(token, "Bearer", ttlSeconds);
    }

    public UserResponse currentUser(String subject) {
        long userId;
        try { userId = Long.parseLong(subject); }
        catch (NumberFormatException exception) {
            throw new BadCredentialsException("Invalid subject");
        }
        User user = users.findById(userId)
                .orElseThrow(() -> new BadCredentialsException("User no longer exists"));
        return new UserResponse(user.getId(), user.getUsername());
    }
}
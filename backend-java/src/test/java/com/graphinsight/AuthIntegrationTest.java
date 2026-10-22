package com.graphinsight;

import com.graphinsight.dto.ChatResponse;
import com.graphinsight.entity.User;
import com.graphinsight.repository.UserRepository;
import com.graphinsight.service.AiService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import jakarta.servlet.Filter;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.JwsHeader;
import org.springframework.security.oauth2.jwt.JwtClaimsSet;
import org.springframework.security.oauth2.jwt.JwtEncoder;
import org.springframework.security.oauth2.jwt.JwtEncoderParameters;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.context.bean.override.mockito.MockitoBean;

import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;
import java.security.SecureRandom;
import java.time.Instant;
import java.util.Base64;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.MOCK, properties = {
        "spring.datasource.url=jdbc:h2:mem:day8;MODE=PostgreSQL;DB_CLOSE_DELAY=-1",
        "spring.datasource.username=sa",
        "spring.datasource.password=",
        "spring.jpa.hibernate.ddl-auto=create-drop",
        "app.demo.username=student",
        "app.demo.password=Test-only-Password-123!",
        "app.jwt.ttl-seconds=1800"
})
@ActiveProfiles("dev")
class AuthIntegrationTest {
    @Autowired WebApplicationContext context;
    @Autowired @Qualifier("springSecurityFilterChain") Filter securityFilter;
    MockMvc mvc;
    @Autowired UserRepository users;
    @Autowired PasswordEncoder passwords;
    @Autowired JwtEncoder encoder;
    @MockitoBean AiService aiService;

    @DynamicPropertySource
    static void jwtSecret(DynamicPropertyRegistry registry) {
        byte[] bytes = new byte[32];
        new SecureRandom().nextBytes(bytes);
        String secret = Base64.getEncoder().encodeToString(bytes);
        registry.add("app.jwt.secret", () -> secret);
    }

    @BeforeEach
    void setupMvc() {
        mvc = MockMvcBuilders.webAppContextSetup(context).addFilters(securityFilter).build();
    }

    record Response(int statusCode, String body) {
    }

    Response request(String method, String path, String body, String token)
            throws Exception {
        MockHttpServletRequestBuilder builder = MockMvcRequestBuilders
                .request(HttpMethod.valueOf(method), path)
                .contentType(MediaType.APPLICATION_JSON);
        if (token != null) {
            builder.header("Authorization", "Bearer " + token);
        }
        if (body != null) { builder.content(body); }
        var result = mvc.perform(builder).andReturn().getResponse();
        return new Response(result.getStatus(), result.getContentAsString());
    }

    String login() throws Exception {
        Response response = request("POST", "/api/auth/login",
                "{\"username\":\"student\",\"password\":\"Test-only-Password-123!\"}", null);
        assertEquals(200, response.statusCode(), response.body());
        Matcher matcher = Pattern.compile("\"accessToken\":\"([^\"]+)\"").matcher(response.body());
        assertTrue(matcher.find(), response.body());
        return matcher.group(1);
    }

    String signedToken(String issuer, String audience, Instant expiresAt, String scope) {
        User user = users.findByUsername("student").orElseThrow();
        JwtClaimsSet.Builder claims = JwtClaimsSet.builder()
                .issuer(issuer).subject(user.getId().toString())
                .audience(List.of(audience)).issuedAt(Instant.now().minusSeconds(120))
                .claim("scope", scope);
        if (expiresAt != null) {
            claims.expiresAt(expiresAt);
        }
        return encoder.encode(JwtEncoderParameters.from(
                JwsHeader.with(MacAlgorithm.HS256).build(), claims.build())).getTokenValue();
    }

    @Test
    void passwordIsHashedAndLoginReturnsJwt() throws Exception {
        User user = users.findByUsername("student").orElseThrow();
        assertNotEquals("Test-only-Password-123!", user.getPasswordHash());
        assertTrue(passwords.matches("Test-only-Password-123!", user.getPasswordHash()));
        assertEquals(3, login().split("\\.").length);
    }

    @Test
    void wrongPasswordAndUnknownUserReturn401() throws Exception {
        for (String body : List.of(
                "{\"username\":\"student\",\"password\":\"wrong-password\"}",
                "{\"username\":\"missing-user\",\"password\":\"wrong-password\"}")) {
            assertEquals(401, request("POST", "/api/auth/login", body, null).statusCode());
        }
    }

    @Test
    void blankFieldsReturn400() throws Exception {
        assertEquals(400, request("POST", "/api/auth/login",
                "{\"username\":\"\",\"password\":\"\"}", null).statusCode());
    }

    @Test
    void missingAndFakeTokensReturn401() throws Exception {
        assertEquals(401, request("GET", "/api/auth/me", null, null).statusCode());
        assertEquals(401, request("GET", "/api/auth/me", null, "token-admin-001").statusCode());
    }

    @Test
    void meReturnsIdentityWithoutHash() throws Exception {
        Response response = request("GET", "/api/auth/me", null, login());
        assertEquals(200, response.statusCode(), response.body());
        assertTrue(response.body().contains("\"username\":\"student\""));
        assertFalse(response.body().toLowerCase().contains("password"));
    }

    @Test
    void tamperedSignatureReturns401() throws Exception {
        String[] parts = login().split("\\.");
        char changed = parts[2].charAt(0) == 'A' ? 'B' : 'A';
        parts[2] = changed + parts[2].substring(1);
        assertEquals(401, request("GET", "/api/auth/me", null, String.join(".", parts)).statusCode());
    }

    @Test
    void expiredTokenReturns401() throws Exception {
        String token = signedToken("graphinsight-local", "graphinsight-api",
                Instant.now().minusSeconds(60), "ai:chat");
        assertEquals(401, request("GET", "/api/auth/me", null, token).statusCode());
    }

    @Test
    void wrongIssuerAndAudienceReturn401() throws Exception {
        for (String token : List.of(
                signedToken("wrong-issuer", "graphinsight-api", Instant.now().plusSeconds(60), "ai:chat"),
                signedToken("graphinsight-local", "wrong-audience", Instant.now().plusSeconds(60), "ai:chat"))) {
            assertEquals(401, request("GET", "/api/auth/me", null, token).statusCode());
        }
    }

    @Test
    void missingExpiryReturns401() throws Exception {
        String token = signedToken("graphinsight-local", "graphinsight-api", null, "ai:chat");
        assertEquals(401, request("GET", "/api/auth/me", null, token).statusCode());
    }

    @Test
    void unauthorizedAiRequestDoesNotReachService() throws Exception {
        assertEquals(401, request("POST", "/api/ai/chat",
                "{\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}],\"temperature\":0.1}",
                null).statusCode());
        verifyNoInteractions(aiService);
    }

    @Test
    void validTokenWithoutScopeReturns403() throws Exception {
        String token = signedToken("graphinsight-local", "graphinsight-api",
                Instant.now().plusSeconds(60), "");
        assertEquals(403, request("POST", "/api/ai/chat",
                "{\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}],\"temperature\":0.1}",
                token).statusCode());
        verifyNoInteractions(aiService);
    }

    @Test
    void validTokenCanUseAiEndpointWithoutPaidModelCall() throws Exception {
        when(aiService.chat(any())).thenReturn(new ChatResponse("offline-test-answer"));
        Response response = request("POST", "/api/ai/chat",
                "{\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}],\"temperature\":0.1}",
                login());
        assertEquals(200, response.statusCode(), response.body());
        assertTrue(response.body().contains("offline-test-answer"));
        verify(aiService, times(1)).chat(any());
    }
}

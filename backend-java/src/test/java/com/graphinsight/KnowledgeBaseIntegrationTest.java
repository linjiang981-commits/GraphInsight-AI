package com.graphinsight;

import com.graphinsight.entity.*;
import com.graphinsight.repository.*;
import com.graphinsight.service.AuthService;
import com.graphinsight.service.AiService;
import jakarta.servlet.Filter;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;
import java.security.SecureRandom;
import java.util.Base64;
import java.util.UUID;
import java.util.regex.Pattern;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest(properties = {
        "spring.datasource.url=jdbc:h2:mem:day9;MODE=PostgreSQL;DB_CLOSE_DELAY=-1",
        "spring.datasource.username=sa",
        "spring.datasource.password=",
        "spring.jpa.hibernate.ddl-auto=create-drop",
        "app.jwt.ttl-seconds=1800"
})
class KnowledgeBaseIntegrationTest {
    @Autowired WebApplicationContext context;
    @Autowired @Qualifier("springSecurityFilterChain") Filter securityFilter;
    @Autowired UserRepository users;
    @Autowired KnowledgeBaseRepository bases;
    @Autowired KnowledgeDocumentRepository documents;
    @Autowired ConversationRepository conversations;
    @Autowired PasswordEncoder passwords;
    @Autowired AuthService auth;
    @MockitoBean AiService aiService;

    MockMvc mvc;
    User alice;
    User bob;
    String aliceToken;
    String bobToken;
    static final String PATH = "/api/knowledge-bases";
    static final String PASSWORD = "Test-only-Day9-Password!";

    @DynamicPropertySource
    static void jwtSecret(DynamicPropertyRegistry registry) {
        byte[] bytes = new byte[32];
        new SecureRandom().nextBytes(bytes);
        String value = Base64.getEncoder().encodeToString(bytes);
        registry.add("app.jwt.secret", () -> value);
    }

    @BeforeEach
    void setup() {
        mvc = MockMvcBuilders.webAppContextSetup(context).addFilters(securityFilter).build();
        String suffix = UUID.randomUUID().toString();
        alice = users.saveAndFlush(new User("alice-" + suffix, passwords.encode(PASSWORD)));
        bob = users.saveAndFlush(new User("bob-" + suffix, passwords.encode(PASSWORD)));
        aliceToken = auth.login(alice.getUsername(), PASSWORD).accessToken();
        bobToken = auth.login(bob.getUsername(), PASSWORD).accessToken();
    }

    long createBase(String token, String name) throws Exception {
        String body = mvc.perform(post(PATH).header("Authorization", "Bearer " + token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"" + name + "\",\"description\":\"learning\"}"))
                .andExpect(status().isCreated())
                .andExpect(header().exists("Location"))
                .andExpect(jsonPath("$.status").value("ACTIVE"))
                .andExpect(jsonPath("$.createdAt").isNotEmpty())
                .andExpect(jsonPath("$.passwordHash").doesNotExist())
                .andReturn().getResponse().getContentAsString();
        var matcher = Pattern.compile("\"id\"\\s*:\\s*(\\d+)").matcher(body);
        assertTrue(matcher.find(), body);
        return Long.parseLong(matcher.group(1));
    }

    @Test
    void ownerCanCreateReadUpdateAndDelete() throws Exception {
        long id = createBase(aliceToken, "network");
        mvc.perform(get(PATH + "/" + id).header("Authorization", "Bearer " + aliceToken))
                .andExpect(status().isOk()).andExpect(jsonPath("$.name").value("network"));
        mvc.perform(put(PATH + "/" + id).header("Authorization", "Bearer " + aliceToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"new-name\",\"description\":\"updated\",\"status\":\"ACTIVE\"}"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.name").value("new-name"));
        assertEquals("new-name", bases.findById(id).orElseThrow().getName());
        mvc.perform(delete(PATH + "/" + id).header("Authorization", "Bearer " + aliceToken))
                .andExpect(status().isNoContent()).andExpect(content().string(""));
        assertFalse(bases.existsById(id));
        mvc.perform(get(PATH + "/" + id).header("Authorization", "Bearer " + aliceToken))
                .andExpect(status().isNotFound());
    }

    @Test
    void listDoesNotLeakOtherUsersData() throws Exception {
        createBase(aliceToken, "alice-private");
        createBase(bobToken, "bob-private");
        mvc.perform(get(PATH).header("Authorization", "Bearer " + bobToken))
                .andExpect(status().isOk()).andExpect(jsonPath("$.totalElements").value(1))
                .andExpect(jsonPath("$.content[0].name").value("bob-private"));
    }

    @Test
    void anotherUserCannotReadUpdateOrDelete() throws Exception {
        long id = createBase(aliceToken, "private");
        mvc.perform(get(PATH + "/" + id).header("Authorization", "Bearer " + bobToken))
                .andExpect(status().isNotFound());
        mvc.perform(put(PATH + "/" + id).header("Authorization", "Bearer " + bobToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"hacked\",\"description\":\"\",\"status\":\"ARCHIVED\"}"))
                .andExpect(status().isNotFound());
        mvc.perform(delete(PATH + "/" + id).header("Authorization", "Bearer " + bobToken))
                .andExpect(status().isNotFound());
        assertEquals("private", bases.findById(id).orElseThrow().getName());
    }

    @Test
    void requestBodyCannotAssignAnotherOwner() throws Exception {
        var response = mvc.perform(post(PATH).header("Authorization", "Bearer " + aliceToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"spoof\",\"ownerId\":" + bob.getId() + "}"))
                .andReturn().getResponse();
        // Both reject-unknown-fields (400) and ignore-unknown-fields (201) are safe.
        assertTrue(response.getStatus() == 400 || response.getStatus() == 201);
        mvc.perform(get(PATH).header("Authorization", "Bearer " + bobToken))
                .andExpect(status().isOk()).andExpect(jsonPath("$.totalElements").value(0));
        if (response.getStatus() == 201) {
            mvc.perform(get(PATH).header("Authorization", "Bearer " + aliceToken))
                    .andExpect(jsonPath("$.totalElements").value(1));
        }
    }

    @Test
    void invalidInputsReturn400() throws Exception {
        for (String body : new String[]{
                "{\"name\":\"   \"}", "{}",
                "{\"name\":\"" + "x".repeat(101) + "\"}",
                "{\"name\":\"ok\",\"description\":\"" + "x".repeat(1001) + "\"}"}) {
            mvc.perform(post(PATH).header("Authorization", "Bearer " + aliceToken)
                            .contentType(MediaType.APPLICATION_JSON).content(body))
                    .andExpect(status().isBadRequest());
        }
        long id = createBase(aliceToken, "valid");
        mvc.perform(put(PATH + "/" + id).header("Authorization", "Bearer " + aliceToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"ok\",\"status\":\"UNKNOWN\"}"))
                .andExpect(status().isBadRequest());
        mvc.perform(get(PATH + "/abc").header("Authorization", "Bearer " + aliceToken))
                .andExpect(status().isBadRequest());
    }

    @Test
    void pagingIsBoundedAndStable() throws Exception {
        createBase(aliceToken, "first");
        createBase(aliceToken, "second");
        mvc.perform(get(PATH + "?page=0&size=1").header("Authorization", "Bearer " + aliceToken))
                .andExpect(status().isOk()).andExpect(jsonPath("$.totalElements").value(2))
                .andExpect(jsonPath("$.totalPages").value(2))
                .andExpect(jsonPath("$.content[0].name").value("second"));
        mvc.perform(get(PATH + "?page=1&size=1").header("Authorization", "Bearer " + aliceToken))
                .andExpect(jsonPath("$.content[0].name").value("first"));
        for (String query : new String[]{"?page=-1", "?size=0", "?size=51", "?page=abc"}) {
            mvc.perform(get(PATH + query).header("Authorization", "Bearer " + aliceToken))
                    .andExpect(status().isBadRequest());
        }
    }

    @Test
    void documentPreventsKnowledgeBaseDeletion() throws Exception {
        long id = createBase(aliceToken, "with-document");
        var document = documents.saveAndFlush(
                new KnowledgeDocument(bases.findById(id).orElseThrow(), "guide.pdf"));
        assertEquals(DocumentStatus.PENDING, document.getStatus());
        mvc.perform(delete(PATH + "/" + id).header("Authorization", "Bearer " + aliceToken))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.code").value("KNOWLEDGE_BASE_NOT_EMPTY"));
        assertTrue(bases.existsById(id));
    }

    @Test
    void conversationPreventsKnowledgeBaseDeletion() throws Exception {
        long id = createBase(aliceToken, "with-conversation");
        var conversation = conversations.saveAndFlush(
                new Conversation(bases.findById(id).orElseThrow(), "first chat"));
        assertEquals(ConversationStatus.ACTIVE, conversation.getStatus());
        mvc.perform(delete(PATH + "/" + id).header("Authorization", "Bearer " + aliceToken))
                .andExpect(status().isConflict());
        assertTrue(conversations.existsById(conversation.getId()));
    }

    @Test
    void databaseForeignKeyAlsoRejectsDeletingParent() throws Exception {
        long id = createBase(aliceToken, "fk-check");
        documents.saveAndFlush(
                new KnowledgeDocument(bases.findById(id).orElseThrow(), "reference.md"));
        // deleteAllByIdInBatch bypasses the service's "not empty" check.
        assertThrows(DataIntegrityViolationException.class,
                () -> bases.deleteAllByIdInBatch(java.util.List.of(id)));
        assertTrue(bases.existsById(id));
    }

    @Test
    void archiveKeepsTheRowAndItCanBeReactivated() throws Exception {
        long id = createBase(aliceToken, "archive-check");
        for (String state : new String[]{"ARCHIVED", "ACTIVE"}) {
            mvc.perform(put(PATH + "/" + id).header("Authorization", "Bearer " + aliceToken)
                            .contentType(MediaType.APPLICATION_JSON)
                            .content("{\"name\":\"archive-check\",\"status\":\"" + state + "\"}"))
                    .andExpect(status().isOk()).andExpect(jsonPath("$.status").value(state));
            assertTrue(bases.existsById(id));
        }
    }

    @Test
    void missingTokenReturns401WithoutCallingAi() throws Exception {
        mvc.perform(get(PATH)).andExpect(status().isUnauthorized());
        mvc.perform(post(PATH).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"anonymous\"}"))
                .andExpect(status().isUnauthorized());
        verifyNoInteractions(aiService);
    }

    @Test
    void deletedUserCannotUseExistingJwtForKnowledgeBases() throws Exception {
        users.deleteById(bob.getId());
        mvc.perform(get(PATH).header("Authorization", "Bearer " + bobToken))
                .andExpect(status().isUnauthorized());
    }
}

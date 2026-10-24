package com.graphinsight.controller;

import com.graphinsight.dto.*;
import com.graphinsight.service.AuthService;
import com.graphinsight.service.KnowledgeBaseService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;
import java.net.URI;

@RestController
@RequestMapping("/api/knowledge-bases")
public class KnowledgeBaseController {
    private final KnowledgeBaseService bases;
    private final AuthService auth;

    public KnowledgeBaseController(KnowledgeBaseService bases, AuthService auth) {
        this.bases = bases;
        this.auth = auth;
    }

    @PostMapping
    public ResponseEntity<KnowledgeBaseResponse> create(
            @AuthenticationPrincipal Jwt jwt,
            @Valid @RequestBody KnowledgeBaseCreateRequest request
    ) {
        KnowledgeBaseResponse result = bases.create(ownerId(jwt), request);
        return ResponseEntity.created(URI.create("/api/knowledge-bases/" + result.id()))
                .body(result);
    }

    @GetMapping
    public PageResponse<KnowledgeBaseResponse> list(
            @AuthenticationPrincipal Jwt jwt,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        return bases.list(ownerId(jwt), page, size);
    }

    @GetMapping("/{id}")
    public KnowledgeBaseResponse get(@AuthenticationPrincipal Jwt jwt, @PathVariable Long id) {
        return bases.get(ownerId(jwt), id);
    }

    @PutMapping("/{id}")
    public KnowledgeBaseResponse update(
            @AuthenticationPrincipal Jwt jwt, @PathVariable Long id,
            @Valid @RequestBody KnowledgeBaseUpdateRequest request
    ) {
        return bases.update(ownerId(jwt), id, request);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(
            @AuthenticationPrincipal Jwt jwt, @PathVariable Long id
    ) {
        bases.delete(ownerId(jwt), id);
        return ResponseEntity.noContent().build();
    }

    private Long ownerId(Jwt jwt) {
        return auth.currentUser(jwt.getSubject()).id();
    }
}

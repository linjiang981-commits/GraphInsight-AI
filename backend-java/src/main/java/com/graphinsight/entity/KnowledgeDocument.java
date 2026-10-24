package com.graphinsight.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "kb_document", indexes = {
        @Index(name = "idx_kb_document_kb", columnList = "knowledge_base_id")
})
public class KnowledgeDocument {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "knowledge_base_id", nullable = false)
    private KnowledgeBase knowledgeBase;

    @Column(name = "original_name", nullable = false, length = 200)
    private String originalName;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private DocumentStatus status = DocumentStatus.PENDING;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    protected KnowledgeDocument() {}

    public KnowledgeDocument(KnowledgeBase knowledgeBase, String originalName) {
        this.knowledgeBase = knowledgeBase;
        this.originalName = originalName;
    }

    @PrePersist
    void onCreate() { createdAt = Instant.now(); }

    public Long getId() { return id; }
    public DocumentStatus getStatus() { return status; }
}

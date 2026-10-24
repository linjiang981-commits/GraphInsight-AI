package com.graphinsight.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "conversation", indexes = {
        @Index(name = "idx_conversation_kb", columnList = "knowledge_base_id")
})
public class Conversation {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "knowledge_base_id", nullable = false)
    private KnowledgeBase knowledgeBase;

    @Column(name = "title", nullable = false, length = 200)
    private String title;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private ConversationStatus status = ConversationStatus.ACTIVE;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    protected Conversation() {}

    public Conversation(KnowledgeBase knowledgeBase, String title) {
        this.knowledgeBase = knowledgeBase;
        this.title = title;
    }

    @PrePersist
    void onCreate() { createdAt = Instant.now(); }

    public Long getId() { return id; }
    public ConversationStatus getStatus() { return status; }
}

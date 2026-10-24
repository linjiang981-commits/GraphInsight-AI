package com.graphinsight.dto;

import com.graphinsight.entity.KnowledgeBase;
import com.graphinsight.entity.KnowledgeBaseStatus;
import java.time.Instant;

public record KnowledgeBaseResponse(
        Long id, String name, String description, KnowledgeBaseStatus status,
        Instant createdAt, Instant updatedAt
) {
    public static KnowledgeBaseResponse from(KnowledgeBase entity) {
        return new KnowledgeBaseResponse(
                entity.getId(), entity.getName(), entity.getDescription(),
                entity.getStatus(), entity.getCreatedAt(), entity.getUpdatedAt());
    }
}

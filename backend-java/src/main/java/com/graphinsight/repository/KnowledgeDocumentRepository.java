package com.graphinsight.repository;

import com.graphinsight.entity.KnowledgeDocument;
import org.springframework.data.jpa.repository.JpaRepository;

public interface KnowledgeDocumentRepository extends JpaRepository<KnowledgeDocument, Long> {
    boolean existsByKnowledgeBase_Id(Long knowledgeBaseId);
}

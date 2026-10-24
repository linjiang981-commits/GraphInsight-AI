package com.graphinsight.repository;

import com.graphinsight.entity.Conversation;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ConversationRepository extends JpaRepository<Conversation, Long> {
    boolean existsByKnowledgeBase_Id(Long knowledgeBaseId);
}

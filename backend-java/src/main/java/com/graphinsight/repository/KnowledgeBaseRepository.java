package com.graphinsight.repository;

import com.graphinsight.entity.KnowledgeBase;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface KnowledgeBaseRepository extends JpaRepository<KnowledgeBase, Long> {
    Page<KnowledgeBase> findByOwner_Id(Long ownerId, Pageable pageable);
    Optional<KnowledgeBase> findByIdAndOwner_Id(Long id, Long ownerId);
}

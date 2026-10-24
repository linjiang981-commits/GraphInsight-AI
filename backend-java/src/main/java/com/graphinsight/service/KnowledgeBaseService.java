package com.graphinsight.service;

import com.graphinsight.dto.*;
import com.graphinsight.entity.KnowledgeBase;
import com.graphinsight.entity.User;
import com.graphinsight.exception.BusinessException;
import com.graphinsight.repository.*;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class KnowledgeBaseService {
    private final KnowledgeBaseRepository bases;
    private final UserRepository users;
    private final KnowledgeDocumentRepository documents;
    private final ConversationRepository conversations;

    public KnowledgeBaseService(
            KnowledgeBaseRepository bases, UserRepository users,
            KnowledgeDocumentRepository documents, ConversationRepository conversations
    ) {
        this.bases = bases;
        this.users = users;
        this.documents = documents;
        this.conversations = conversations;
    }

    @Transactional
    public KnowledgeBaseResponse create(Long ownerId, KnowledgeBaseCreateRequest request) {
        User owner = users.findById(ownerId)
                .orElseThrow(() -> new BadCredentialsException("User no longer exists"));
        KnowledgeBase base = new KnowledgeBase(
                owner, request.name().strip(), description(request.description()));
        return KnowledgeBaseResponse.from(bases.saveAndFlush(base));
    }

    public PageResponse<KnowledgeBaseResponse> list(Long ownerId, int page, int size) {
        if (page < 0 || size < 1 || size > 50) {
            throw new BusinessException(HttpStatus.BAD_REQUEST, "INVALID_PAGE",
                    "page 必须 >= 0，size 必须在 1 到 50 之间");
        }
        var result = bases.findByOwner_Id(ownerId,
                PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "id")));
        return new PageResponse<>(
                result.getContent().stream().map(KnowledgeBaseResponse::from).toList(),
                result.getNumber(), result.getSize(),
                result.getTotalElements(), result.getTotalPages());
    }

    public KnowledgeBaseResponse get(Long ownerId, Long id) {
        return KnowledgeBaseResponse.from(ownedBase(ownerId, id));
    }

    @Transactional
    public KnowledgeBaseResponse update(
            Long ownerId, Long id, KnowledgeBaseUpdateRequest request
    ) {
        KnowledgeBase base = ownedBase(ownerId, id);
        base.update(request.name().strip(), description(request.description()), request.status());
        bases.flush();
        return KnowledgeBaseResponse.from(base);
    }

    @Transactional
    public void delete(Long ownerId, Long id) {
        KnowledgeBase base = ownedBase(ownerId, id);
        if (documents.existsByKnowledgeBase_Id(id)
                || conversations.existsByKnowledgeBase_Id(id)) {
            throw new BusinessException(HttpStatus.CONFLICT, "KNOWLEDGE_BASE_NOT_EMPTY",
                    "知识库包含文档或会话，请先归档，暂不支持删除非空知识库");
        }
        bases.delete(base);
        bases.flush();
    }

    private KnowledgeBase ownedBase(Long ownerId, Long id) {
        return bases.findByIdAndOwner_Id(id, ownerId)
                .orElseThrow(() -> new BusinessException(HttpStatus.NOT_FOUND,
                        "KNOWLEDGE_BASE_NOT_FOUND", "知识库不存在或不可访问"));
    }

    private String description(String value) {
        return value == null ? "" : value.strip();
    }
}
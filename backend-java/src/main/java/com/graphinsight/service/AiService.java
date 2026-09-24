package com.graphinsight.service;

import com.graphinsight.dto.ChatRequest;
import com.graphinsight.dto.ChatResponse;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;


@Service
public class AiService {

    private final RestClient restClient;

    public AiService() {

        this.restClient = RestClient.create(
                "http://127.0.0.1:8000"
        );
    }


    public ChatResponse chat(ChatRequest request) {

        return restClient
                .post()
                .uri("/api/chat")
                .body(request)
                .retrieve()
                .body(ChatResponse.class);
    }
}

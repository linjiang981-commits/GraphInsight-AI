package com.graphinsight.controller;

import com.graphinsight.dto.ChatRequest;
import com.graphinsight.dto.ChatResponse;
import com.graphinsight.service.AiService;
import org.springframework.web.bind.annotation.*;


@RestController
@RequestMapping("/api/ai")
public class AiController {

    private final AiService aiService;


    public AiController(AiService aiService) {
        this.aiService = aiService;
    }


    @PostMapping("/chat")
    public ChatResponse chat(
            @RequestBody ChatRequest request
    ) {

        return aiService.chat(request);
    }
}
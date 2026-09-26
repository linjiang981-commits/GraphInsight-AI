package com.graphinsight.dto;

import java.util.List;

public record ChatRequest(
        List<ChatMessage> messages,
        double temperature
) {
}
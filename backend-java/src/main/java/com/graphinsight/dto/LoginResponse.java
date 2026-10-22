package com.graphinsight.dto;

public record LoginResponse(String accessToken, String tokenType, long expiresIn) {
}

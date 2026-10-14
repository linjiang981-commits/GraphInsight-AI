package com.graphinsight.controller;


import com.graphinsight.dto.LoginRequest;
import com.graphinsight.dto.LoginResponse;
import com.graphinsight.service.AuthService;

import org.springframework.web.bind.annotation.*;



@RestController
@RequestMapping("/api/auth")
public class AuthController {


    private final AuthService authService;



    public AuthController(
            AuthService authService
    ){

        this.authService=authService;

    }



    @PostMapping("/login")
    public LoginResponse login(
            @RequestBody LoginRequest request
    ){


        String token =
                authService.login(
                        request.getUsername(),
                        request.getPassword()
                );


        return new LoginResponse(token);

    }


}

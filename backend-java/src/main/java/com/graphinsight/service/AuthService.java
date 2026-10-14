package com.graphinsight.service;


import org.springframework.stereotype.Service;


@Service
public class AuthService {


    public String login(
            String username,
            String password
    ){


        if(
            "admin".equals(username)
            &&
            "123456".equals(password)
        ){

            return "token-admin-001";

        }


        throw new RuntimeException(
                "用户名或密码错误"
        );

    }


}
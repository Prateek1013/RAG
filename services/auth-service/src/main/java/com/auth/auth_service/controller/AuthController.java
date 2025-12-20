package com.auth.auth_service.controller;

import com.auth.auth_service.dto.JwtResponse;
import com.auth.auth_service.dto.LoginRequest;
import com.auth.auth_service.entity.Users;
import com.auth.auth_service.repository.UsersRepository;
import com.auth.auth_service.util.JwtUtils;
import com.auth.auth_service.util.enums.Role;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    @Autowired
    private UsersRepository usersRepository;
    @Autowired
    private JwtUtils jwtUtils;

    private BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

    @PostMapping("/login")
    public ResponseEntity<JwtResponse> login(@RequestBody LoginRequest loginRequest) {
        String email = loginRequest.getEmail();
        String pass=loginRequest.getPassword();
        if (userExists(email)) {
            Optional<Users> user=usersRepository.findByEmail(email);
            if(encoder.matches(pass,user.get().getPassword())) {
                String token = jwtUtils.generateToken(email);
                return new ResponseEntity<JwtResponse>(JwtResponse.builder().
                        email(email).
                        token(token).
                        message("User logged in successfully!").
                        build(),
                        HttpStatusCode.valueOf(200));
            }
            else return new ResponseEntity<JwtResponse>(JwtResponse.builder()
                    .email(email)
                    .token(null)
                    .message("Email or password incorrect!")
                    .build(),
                    HttpStatusCode.valueOf(401));
        }
        return new ResponseEntity<JwtResponse>(JwtResponse.builder()
                .email(email)
                .token(null)
                .message("No such user exists with email "+email)
                .build(),
                HttpStatusCode.valueOf(404));
    }

    @PostMapping("/register")
    public ResponseEntity<String> register(@RequestBody LoginRequest loginRequest) {
        String email = loginRequest.getEmail();
        if (userExists(email)) {
            return new ResponseEntity<>("User already exists!", HttpStatusCode.valueOf(200));
        }
        String password = loginRequest.getPassword();
        try {
            usersRepository.save(Users.builder()
                    .email(email)
                    .password(encoder.encode(password))
                    .role(Role.USER)
                    .build());
            return new ResponseEntity<String>("User registered successfully!", HttpStatusCode.valueOf(200));
        } catch (Exception e) {
            throw new RuntimeException(e.getMessage());
        }
    }

    private boolean userExists(String email) {
        Optional<Users> user = usersRepository.findByEmail(email);
        return user.isPresent();
    }
}

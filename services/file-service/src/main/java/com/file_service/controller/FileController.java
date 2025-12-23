package com.file_service.controller;

import com.file_service.repository.FileRepository;
import com.file_service.service.FileStorageService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/file")
public class FileController {
    @Autowired
    private FileRepository fileRepository;
    @Autowired
    private FileStorageService fileStorageService;

    @PostMapping("/upload")
    private ResponseEntity<String> upload(@RequestPart("file") MultipartFile file,
                                          @RequestHeader("X-user-id") String user_id){

        return ResponseEntity.ok("uploaded!");
    }
}

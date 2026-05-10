package com.file_service.controller;

import com.file_service.repository.FileRepository;
import com.file_service.service.FileStorageService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.*;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.util.Map;

@RestController
@RequestMapping("/api/file")
public class FileController {
    @Autowired
    private FileRepository fileRepository;
    @Autowired
    private FileStorageService fileStorageService;

    @PostMapping("/upload")
    private ResponseEntity<String> upload(@RequestPart("file") MultipartFile file,
                                          @RequestHeader("X-user-id") String user_id) {
        try {
            String fileName = fileStorageService.uploadFile(file, user_id);
            return new ResponseEntity<String>(fileName + "created!", HttpStatusCode.valueOf(200));
        } catch (Exception e) {
            return new ResponseEntity<>("Failed to upload! due " + e.getMessage(), HttpStatusCode.valueOf(404));
        }

    }

    @PostMapping("/getfile")
    public ResponseEntity<Map<String, String>> getFile(@RequestParam(name = "filename") String fileName,
                                                       @RequestHeader("X-user-id") String user_id) {
        try {
            String url = fileStorageService.getFile(fileName, user_id);
            if (url.equals("Bucket DNE!")) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", "Bucket does not exist"));
            }
            return ResponseEntity.ok(Map.of("url", url));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to get file URL: " + e.getMessage()));
        }
    }
}

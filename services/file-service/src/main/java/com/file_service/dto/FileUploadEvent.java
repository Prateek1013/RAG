package com.file_service.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FileUploadEvent {
    private UUID fileId;
    private String path;
    private String fileName;
    private UUID userId;
}

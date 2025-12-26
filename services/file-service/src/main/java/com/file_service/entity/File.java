package com.file_service.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "file")
@Builder
public class File {
    @Id
    @GeneratedValue
    private UUID id;
    @Column(nullable = false)
    private String path; //minio object name
    @Column(name = "file_name")
    private String fileName;
    @Column(nullable = false)
    private long size;
    @Column(name = "user_id", nullable = false)
    private UUID userId;
    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

}

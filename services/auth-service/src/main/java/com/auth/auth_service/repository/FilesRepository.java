package com.auth.auth_service.repository;

import com.auth.auth_service.entity.Files;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface FilesRepository extends JpaRepository<Files, UUID> {
}

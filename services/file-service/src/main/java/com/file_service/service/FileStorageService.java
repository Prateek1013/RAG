package com.file_service.service;

import io.minio.BucketExistsArgs;
import io.minio.MakeBucketArgs;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.UUID;

@Service
public class FileStorageService {

    @Value("${minio.bucket}")
    private String bucket;

    @Autowired
    private MinioClient minioClient;

    public String uploadFile(MultipartFile file,UUID user_id) throws Exception {

        boolean found = minioClient.bucketExists(
                BucketExistsArgs.builder().bucket(bucket).build());

        if (!found) {
            minioClient.makeBucket(
                    MakeBucketArgs.builder().bucket(bucket).build());
        }

        String objectName = user_id + "_" + file.getOriginalFilename();

        minioClient.putObject(
                PutObjectArgs.builder()
                        .bucket(bucket)
                        .object(objectName)
                        .stream(
                                file.getInputStream(),
                                file.getSize(),
                                -1
                        )
                        .contentType(file.getContentType())
                        .build()
        );

        return objectName;
    }
}


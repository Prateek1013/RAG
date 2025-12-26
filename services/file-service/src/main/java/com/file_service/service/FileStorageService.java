package com.file_service.service;

import com.file_service.entity.File;
import com.file_service.repository.FileRepository;
import io.minio.*;
import io.minio.http.Method;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.util.UUID;
import java.util.concurrent.TimeUnit;

@Service
public class FileStorageService {

    @Value("${minio.bucket}")
    private String bucket;

    @Autowired
    private MinioClient minioClient;
    @Autowired
    private FileRepository fileRepository;

    @Transactional
    public String uploadFile(MultipartFile file, String user_id) throws Exception {
        String objectName = user_id + "_" + file.getOriginalFilename();
        File filentity =new File();
        filentity.setFileName(file.getOriginalFilename());
        filentity.setSize(file.getSize());
        filentity.setUserId(UUID.fromString(user_id));
        filentity.setPath(objectName);
        fileRepository.save(filentity);
        boolean found = minioClient.bucketExists(
                BucketExistsArgs.builder().bucket(bucket).build());

        if (!found) {
            minioClient.makeBucket(
                    MakeBucketArgs.builder().bucket(bucket).build());
        }
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

    public String getFile(String fileName, String user_id) throws Exception {
        boolean found = minioClient.bucketExists(
                BucketExistsArgs.builder().bucket(bucket).build());
        if (!found) return "Bucket DNE!";
        String name = user_id + "_" + fileName;
//        return minioClient.getObject(GetObjectArgs
//                .builder()
//                .bucket(bucket)
//                .object(name)
//                .build());
        String url = minioClient.getPresignedObjectUrl(
                GetPresignedObjectUrlArgs.builder()
                        .method(Method.GET)
                        .bucket(bucket)
                        .object(name)
                        .expiry(5, TimeUnit.MINUTES)
                        .build()
        );
        return url;
    }
}


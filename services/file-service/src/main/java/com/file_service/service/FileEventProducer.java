package com.file_service.service;

import com.file_service.dto.FileUploadEvent;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Service
public class FileEventProducer {

    private static final String TOPIC = "file-uploaded-topic";

    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;

    public void sendFileUploadEvent(FileUploadEvent event) {
        kafkaTemplate.send(TOPIC, event.getFileId().toString(), event);
    }
}

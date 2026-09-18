package com.archguard.samples.violations.app.web;

import com.archguard.samples.violations.core.internal.InternalRepository;
import org.springframework.web.bind.annotation.RestController;

@RestController
public final class BadController {
    private final InternalRepository repository;

    public BadController(InternalRepository repository) {
        this.repository = repository;
    }

    public String get(String id) {
        return repository.load(id);
    }
}

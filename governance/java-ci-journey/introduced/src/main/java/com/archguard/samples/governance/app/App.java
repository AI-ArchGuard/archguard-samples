package com.archguard.samples.governance.app;

import com.archguard.samples.governance.api.PublicPort;
import com.archguard.samples.governance.internal.InternalRepository;

public final class App {
    private final PublicPort port;
    private final InternalRepository repository;

    public App(PublicPort port, InternalRepository repository) {
        this.port = port;
        this.repository = repository;
    }

    public String load(String id) {
        return port.load(id) + repository.load(id);
    }
}

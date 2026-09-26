package com.archguard.samples.governance.app;

import com.archguard.samples.governance.api.PublicPort;

public final class App {
    private final PublicPort port;

    public App(PublicPort port) {
        this.port = port;
    }

    public String load(String id) {
        return port.load(id);
    }
}

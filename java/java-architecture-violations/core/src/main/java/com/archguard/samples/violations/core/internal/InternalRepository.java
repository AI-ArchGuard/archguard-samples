package com.archguard.samples.violations.core.internal;

import org.springframework.stereotype.Repository;

@Repository
public final class InternalRepository {
    public String load(String id) {
        return id;
    }
}

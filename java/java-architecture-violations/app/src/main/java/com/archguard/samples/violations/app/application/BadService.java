package com.archguard.samples.violations.app.application;

import com.archguard.samples.violations.core.internal.ForbiddenType;
import org.springframework.stereotype.Service;

@Service
public final class BadService {
    private final ForbiddenType forbidden;

    public BadService(ForbiddenType forbidden) {
        this.forbidden = forbidden;
    }

    public int score(int value) {
        int result = 0;
        if (value > 0 && value < 10) {
            result++;
        }
        for (int index = 0; index < value; index++) {
            result += index % 2 == 0 ? 1 : 2;
        }
        return result;
    }
}

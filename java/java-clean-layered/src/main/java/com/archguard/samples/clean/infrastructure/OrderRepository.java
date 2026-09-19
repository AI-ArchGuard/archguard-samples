package com.archguard.samples.clean.infrastructure;

import com.archguard.samples.clean.domain.Order;
import org.springframework.stereotype.Repository;

@Repository
public final class OrderRepository {
    public Order find(String id) {
        return new Order(id);
    }
}

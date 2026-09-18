package com.archguard.samples.clean.application;

import com.archguard.samples.clean.arch.ArchGuarded;
import com.archguard.samples.clean.domain.Order;
import com.archguard.samples.clean.infrastructure.OrderRepository;
import org.springframework.stereotype.Service;

@ArchGuarded
@Service
public final class OrderService {
    private final OrderRepository repository;

    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }

    public Order load(String id) {
        return repository.find(id);
    }
}

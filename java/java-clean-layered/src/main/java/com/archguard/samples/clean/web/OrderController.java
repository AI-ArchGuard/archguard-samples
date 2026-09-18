package com.archguard.samples.clean.web;

import com.archguard.samples.clean.application.OrderService;
import com.archguard.samples.clean.domain.Order;
import org.springframework.web.bind.annotation.RestController;

@RestController
public final class OrderController {
    private final OrderService service;

    public OrderController(OrderService service) {
        this.service = service;
    }

    public Order get(String id) {
        return service.load(id);
    }
}

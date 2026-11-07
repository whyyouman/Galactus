import { OrderService } from "./order.service";

@Controller("/orders")
export class OrderController {
  constructor(private readonly orderService: OrderService) {}

  @Get("/")
  async list() {
    return [];
  }

  @Patch("/:id/cancel")
  async cancel(id: string) {
    return this.orderService.cancelOrder(id);
  }
}

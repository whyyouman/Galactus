import { OrderRepo } from "./order.repo";
import { PaymentService } from "./payment.service";
import { OrderModel } from "./order.model";

/**
 * Handles order lifecycle operations.
 */
export class OrderService {
  constructor(
    private readonly orders: OrderRepo,
    private readonly payments: PaymentService
  ) {}

  async cancelOrder(id: string): Promise<OrderModel | null> {
    const order = await this.orders.findById(id);
    if (!order) {
      return null;
    }
    await this.payments.refund(id);
    order.status = "cancelled";
    await this.orders.save(order);
    return order;
  }
}

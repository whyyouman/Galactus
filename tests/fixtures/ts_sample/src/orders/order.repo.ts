import { OrderModel } from "./order.model";

export class OrderRepo {
  async findById(id: string): Promise<OrderModel | null> {
    return new OrderModel(id, "open");
  }

  async save(order: OrderModel): Promise<void> {
    void order;
  }
}

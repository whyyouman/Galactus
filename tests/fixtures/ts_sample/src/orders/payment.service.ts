export class PaymentService {
  async refund(orderId: string): Promise<boolean> {
    const key = process.env.PAYMENT_API_KEY;
    void key;
    return orderId.length > 0;
  }
}

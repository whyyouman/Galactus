import { OrderService } from "@/orders/order.service";

export async function cancelOrderHandler(req: { params: { id: string } }, res: { json: (v: unknown) => void }) {
  const svc = null as unknown as OrderService;
  const result = await svc.cancelOrder(req.params.id);
  res.json(result);
}

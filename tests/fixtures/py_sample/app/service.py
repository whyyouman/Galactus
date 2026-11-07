import os

from .models import Order
from .repo import OrderRepo


class OrderService:
    def __init__(self, repo: OrderRepo) -> None:
        self.repo = repo
        self.api_key = os.getenv("PAYMENT_API_KEY")

    def cancel_order(self, order_id: str) -> Order | None:
        order = self.repo.find_by_id(order_id)
        if order is None:
            return None
        order.status = "cancelled"
        self.repo.save(order)
        return order

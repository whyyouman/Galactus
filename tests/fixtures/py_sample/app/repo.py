from .models import Order


class OrderRepo:
    def find_by_id(self, order_id: str) -> Order | None:
        return Order(id=order_id, status="open")

    def save(self, order: Order) -> None:
        _ = order

from fastapi import APIRouter

from .service import OrderService

router = APIRouter(prefix="/orders")


@router.get("/")
async def list_orders() -> list[dict[str, str]]:
    return []


@router.patch("/{order_id}/cancel")
async def cancel_order(order_id: str, svc: OrderService) -> dict[str, str]:
    result = svc.cancel_order(order_id)
    return {"id": result.id if result else order_id, "status": "cancelled"}

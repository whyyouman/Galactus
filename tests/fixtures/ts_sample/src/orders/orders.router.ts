import { Router } from "express";
import { cancelOrderHandler } from "./handlers";

export const ordersRouter = Router();

ordersRouter.get("/", (_req, res) => {
  res.json([]);
});

ordersRouter.patch("/:id/cancel", cancelOrderHandler);

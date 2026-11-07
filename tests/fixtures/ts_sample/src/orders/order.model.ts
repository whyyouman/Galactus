export class OrderModel {
  id: string;
  status: string;

  constructor(id: string, status: string) {
    this.id = id;
    this.status = status;
  }
}

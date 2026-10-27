from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

MAX_UNITS = 20



@dataclass(frozen=True)
class Money:
    amount: Decimal

    def __add__(self, other):
        return Money(self.amount + other.amount)

    def __sub__(self, other):
        return Money(self.amount - other.amount)

    def __mul__(self, factor):
        # factor puede ser int o Decimal (nunca float)
        return Money(self.amount * Decimal(factor))

    def __str__(self):
        return f"${self.amount:.2f}"



@dataclass
class Customer:
    customer_id: str
    name: str
    is_vip: bool = False


@dataclass(frozen=True)
class OrderItem:
    sku: str
    description: str
    unit_price: Money
    quantity: int

    @property
    def subtotal(self):
        return self.unit_price * self.quantity



class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


@dataclass(frozen=True)
class OrderConfirmed:
    order_id: str


@dataclass(frozen=True)
class OrderShipped:
    order_id: str


@dataclass(frozen=True)
class OrderDelivered:
    order_id: str


@dataclass(frozen=True)
class OrderCancelled:
    order_id: str


@dataclass(frozen=True)
class OrderReturned:
    order_id: str



class Order:
    def __init__(self, order_id, customer):
        self.order_id = order_id
        self.customer = customer
        self.status = OrderStatus.PENDING

        self.items = []
        self.events = []
        self.discount_rate = Decimal("0")  # 0.10 = 10%

    @property
    def units(self):
        return sum(item.quantity for item in self.items)

    @property
    def total(self):
        subtotal = Money(Decimal("0"))
        for item in self.items:
            subtotal = subtotal + item.subtotal
        return subtotal - (subtotal * self.discount_rate)

    def add_item(self, item):
        if self.status != OrderStatus.PENDING:
            raise ValueError("Solo se pueden agregar artículos a un pedido pendiente")
        if self.units + item.quantity > MAX_UNITS:
            raise ValueError("El pedido no puede tener más de 20 piezas")
        self.items.append(item)

    def confirm(self):
        if self.status != OrderStatus.PENDING:
            raise ValueError("El pedido debe estar pendiente")
        if not self.items:
            raise ValueError("No se puede confirmar un pedido vacío")
        self.status = OrderStatus.CONFIRMED
        self.events.append(OrderConfirmed(self.order_id))

    def ship(self):
        if self.status != OrderStatus.CONFIRMED:
            raise ValueError("El pedido debe estar confirmado")
        self.status = OrderStatus.SHIPPED
        self.events.append(OrderShipped(self.order_id))

    def deliver(self):
        if self.status != OrderStatus.SHIPPED:

            raise ValueError("El pedido debe estar enviado")
        self.status = OrderStatus.DELIVERED
        self.events.append(OrderDelivered(self.order_id))

    def cancel(self):
        if self.status not in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
            
            raise ValueError("Solo se puede cancelar un pedido pendiente o confirmado")
        self.status = OrderStatus.CANCELLED
        self.events.append(OrderCancelled(self.order_id))

    def return_order(self):
        if self.status != OrderStatus.DELIVERED:
            raise ValueError("Solo se puede devolver un pedido entregado")
        self.status = OrderStatus.RETURNED
        self.events.append(OrderReturned(self.order_id))

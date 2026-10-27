from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from datetime import datetime, timezone

MAX_UNITS = 20





class DomainException(Exception):
    pass


class InvalidOrderData(DomainException):
    pass


class InvalidOrderTransition(DomainException):
    pass


class OrderItemLimitExceeded(DomainException):
    pass





@dataclass(frozen=True)
class Money:

    amount: Decimal
    currency: str = "MXN"

    def __post_init__(self):
        if not self.amount.is_finite() or self.amount < 0:
            raise InvalidOrderData("El monto no es válido")

    def add(self, other):
        
        if self.currency != other.currency:
            raise InvalidOrderData("No se pueden sumar monedas distintas")
        return Money(self.amount + other.amount, self.currency)




@dataclass(frozen=True)
class Customer:

    id: str
    is_vip: bool = False
    active: bool = True


@dataclass(frozen=True)
class OrderItem:

    sku: str

    quantity: int
    unit_price: Money

    def __post_init__(self):
        if not self.sku.strip() or self.quantity <= 0:
            raise InvalidOrderData("El artículo necesita SKU y cantidad mayor a 0")

    @property
    def subtotal(self):

        return Money(self.unit_price.amount * self.quantity)




class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"


@dataclass(frozen=True)
class DomainEvent:
    name: str
    order_id: str
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )




@dataclass
class Order:
    customer: Customer
    id: str
    has_promotion: bool = False
    status: OrderStatus = OrderStatus.DRAFT
    items: list[OrderItem] = field(default_factory=list)
    events: list = field(default_factory=list)

    @property
    def units(self):
        return sum(item.quantity for item in self.items)

    @property
    def total(self):
        amount = sum((x.subtotal.amount for x in self.items), Decimal("0"))
        return Money(amount)

    def add_item(self, item):
        if self.status != OrderStatus.DRAFT:
            raise InvalidOrderTransition("Solo se pueden agregar artículos a un pedido en DRAFT")
        if self.units + item.quantity > MAX_UNITS:
            raise OrderItemLimitExceeded("El pedido no puede pasar de 20 unidades")
        if item.unit_price.currency != "MXN":
            raise InvalidOrderData("Solo se aceptan precios en MXN")
        self.items.append(item)




    def confirm(self):
        if self.status != OrderStatus.DRAFT:
            raise InvalidOrderTransition("Solo se puede confirmar un pedido en DRAFT")
        if not self.items or not self.customer.active:
            raise InvalidOrderData("El pedido necesita artículos y un cliente activo")
        self.status = OrderStatus.CONFIRMED
        self.events.append(DomainEvent("OrderConfirmed", self.id))

    def ship(self, tracking_number):
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderTransition("Solo se puede enviar un pedido CONFIRMED")
        if not tracking_number or not tracking_number.strip():
            raise InvalidOrderData("Falta el número de guía")
        self.status = OrderStatus.SHIPPED
        self.events.append(DomainEvent("OrderShipped", self.id))

    def cancel(self, reason):
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderTransition("Solo se puede cancelar un pedido CONFIRMED")
        if not reason or not reason.strip():
            raise InvalidOrderData("Falta el motivo de cancelación")
        self.status = OrderStatus.CANCELLED
        self.events.append(DomainEvent("OrderCancelled", self.id))

    def deliver(self):
        if self.status != OrderStatus.SHIPPED:
            raise InvalidOrderTransition("Solo se puede entregar un pedido SHIPPED")
        self.status = OrderStatus.DELIVERED
        self.events.append(DomainEvent("OrderDelivered", self.id))

    def return_order(self):
        if self.status != OrderStatus.SHIPPED:
            raise InvalidOrderTransition("Solo se puede devolver un pedido SHIPPED")
        self.status = OrderStatus.RETURNED
        self.events.append(DomainEvent("OrderReturned", self.id))
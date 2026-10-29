import pytest
from decimal import Decimal
from app.domain import (
    Money, 
    Customer, 
    Order, 
    OrderItem, 
    OrderStatus, 
    InvalidOrderData, 
    InvalidOrderTransition, 
    OrderItemLimitExceeded
)
from app.specifications import ten_percent, five_percent
from cargar_csv import load_fixture

# 1 y 2. Pruebas base que vienen textuales en el manual (Sección 12)
def test_money_negativo():
    with pytest.raises(InvalidOrderData):
        Money(Decimal("-1"))

def test_pedido_o001_inicia_draft():
    orders = load_fixture()
    assert orders["O001"].status.value == "DRAFT"
    assert orders["O001"].units == 4
    assert orders["O001"].total.amount == Decimal("2100.00")

# 3. Prueba de 21 unidades (Sección 12)
def test_limite_21_unidades():
    customer = Customer(id="C001", is_vip=False, active=True)
    order = Order(customer=customer, id="TEST_21")
    with pytest.raises(OrderItemLimitExceeded):
        order.add_item(OrderItem(sku="SKU001", quantity=21, unit_price=Money(Decimal("100.00"))))

# 4. Prueba de cliente inactivo (Sección 12)
def test_cliente_inactivo_no_puede_confirmar():
    customer = Customer(id="C002", is_vip=False, active=False)
    order = Order(customer=customer, id="TEST_INACTIVO")
    order.add_item(OrderItem(sku="SKU001", quantity=1, unit_price=Money(Decimal("100.00"))))
    with pytest.raises(InvalidOrderData):
        order.confirm()

# 5. Prueba de pedido vacío (Sección 12)
def test_pedido_vacio_no_puede_confirmar():
    customer = Customer(id="C003", is_vip=False, active=True)
    order = Order(customer=customer, id="TEST_VACIO")
    with pytest.raises(InvalidOrderData):
        order.confirm()

# 6. Prueba de descuento VIP (Sección 12)
def test_descuento_vip():
    orders = load_fixture()
    # O001 cumple: VIP, total > 500, unidades >= 4, sin promoción
    assert ten_percent.is_satisfied_by(orders["O001"]) is True

# 7. Prueba de promoción activa (Sección 12)
def test_promocion_activa_excluye_descuento():
    orders = load_fixture()
    # O005 tiene promoción activa (tiene_promocion=1), debe ser False
    assert ten_percent.is_satisfied_by(orders["O005"]) is False
    assert five_percent.is_satisfied_by(orders["O005"]) is False

# 8. Prueba de envío sin guía (Sección 12)
def test_envio_sin_guia():
    orders = load_fixture()
    order = orders["O002"]
    order.confirm()
    with pytest.raises(InvalidOrderData):
        order.ship(tracking_number="")

# 9. Prueba de confirmación doble (Sección 12)
def test_confirmacion_doble():
    orders = load_fixture()
    order = orders["O013"]
    order.confirm()
    with pytest.raises(InvalidOrderTransition):
        order.confirm()

# 10. Prueba de cancelación desde SHIPPED (Sección 12)
def test_cancelacion_desde_shipped():
    orders = load_fixture()
    order = orders["O001"]
    order.confirm()
    order.ship(tracking_number="GUIA123")
    with pytest.raises(InvalidOrderTransition):
        order.cancel(reason="Devolución pedida")
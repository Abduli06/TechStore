from decimal import Decimal


class Specification:
    def is_satisfied_by(self, order):
        raise NotImplementedError

    def __and__(self, other):
        return AndSpecification(self, other)


    def __or__(self, other):
        return OrSpecification(self, other)


    def __invert__(self):
        return NotSpecification(self)


class AndSpecification(Specification):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def is_satisfied_by(self, order):
        return self.left.is_satisfied_by(order) and self.right.is_satisfied_by(order)


class OrSpecification(Specification):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def is_satisfied_by(self, order):
        return self.left.is_satisfied_by(order) or self.right.is_satisfied_by(order)


class NotSpecification(Specification):
    def __init__(self, spec):
        self.spec = spec

    def is_satisfied_by(self, order):
        return not self.spec.is_satisfied_by(order)


# ---------- Reglas simples ----------
class IsVip(Specification):
    def is_satisfied_by(self, order):
        return order.customer.is_vip


class HasItems(Specification):
    def is_satisfied_by(self, order):
        return len(order.items) > 0


VIP_RULE = IsVip() & HasItems()   
GENERAL_RULE = HasItems() & ~IsVip()  


def get_discount(order):
    """Regresa 0.10 si aplica VIP, 0.05 si aplica la general, 0 si ninguna."""

    if VIP_RULE.is_satisfied_by(order):
        return Decimal("0.10")
    if GENERAL_RULE.is_satisfied_by(order):
        return Decimal("0.05")
    return Decimal("0")


def apply_discount(order):
    order.discount_rate = get_discount(order)

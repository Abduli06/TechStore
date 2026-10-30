# TechStore U4 - Núcleo de Lógica de Negocio

Sistema de administración de pedidos en memoria desarrollado con DDD (Domain-Driven Design), Specification Pattern, Máquina de Estados, Domain Events y API REST en FastAPI.

## Estructura del Proyecto

```
techstore/
├── app/
│   ├── __init__.py
│   ├── domain.py            # Entidades, Value Objects, eventos y máquina de estados
│   ├── specifications.py    # Patrón Specification y reglas de descuento
│   └── api.py               # API REST con FastAPI y mapeo de excepciones
├── datos/
│   ├── clientes.csv         # Catálogo de clientes (12 registros)
│   ├── productos.csv        # Catálogo de productos (12 registros)
│   ├── pedidos.csv          # Pedidos base (16 registros en DRAFT)
│   ├── detalle_pedidos.csv  # Líneas de pedido (21 registros)
│   └── escenarios.csv       # Casos de prueba E01–E15
├── tests/
│   ├── test_domain.py       # Pruebas unitarias del modelo y reglas
│   └── test_api.py          # Pruebas de integración HTTP
├── cargar_csv.py            # Carga de datos inicial desde CSV
├── README.md
└── .gitignore 

```

## 1. Instalación y Ejecución

### Pasos de instalación
1. Crear y activar el entorno virtual dentro de la carpeta del proyecto:
   * **Windows:**
     ```bash
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   * **Linux/macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
2. Instalar las dependencias requeridas:
   ```bash
   python -m pip install fastapi uvicorn pytest httpx
   ```

### Comandos de ejecución
* **Cargar pedidos desde CSV (Punto de Control):**
  ```bash
  python cargar_csv.py
  ```
* **Ejecutar servidor web API:**
  ```bash
  uvicorn app.api:app --reload
  ```
  *Swagger UI disponible en: `http://127.0.0.1:8000/docs`*
* **Correr pruebas automatizadas:**
  ```bash
  python -m pytest -q
  ```
---

## 2. Reglas de Negocio Principales

1. **Dinero (`Money`):** Inmutable, con cantidades manejadas en `Decimal` en moneda MXN. Rechaza valores negativos o monedas distintas (`InvalidOrderData`).
2. **Límite de unidades:** Un pedido admite un máximo acumulado de **20 unidades físicas** sumando las cantidades de sus artículos. Superar este límite lanza `OrderItemLimitExceeded`.
3. **Regla de descuento del 10% (`ten_percent`):** Requiere cliente VIP (`is_vip=True`), monto total estrictamente mayor a 500 MXN, al menos 4 unidades acumuladas y ausencia de promoción activa (`has_promotion=False`).
4. **Regla de descuento del 5% (`five_percent`):** Requiere monto total estrictamente mayor a 5000 MXN y ausencia de promoción activa.
5. **Prioridad de descuentos:** Si un pedido cumple ambas reglas, se aplica primero el 10%. Las especificaciones evalúan el pedido sin modificarlo.

---

## 3. Máquina de Estados y Eventos de Dominio

### Flujo de transiciones
* `DRAFT` --confirm--> `CONFIRMED` --ship--> `SHIPPED` --deliver--> `DELIVERED`
* `CONFIRMED` --cancel--> `CANCELLED`
* `SHIPPED` --return--> `RETURNED`

---

## 4. Endpoints de la API REST

| Método | Endpoint | Descripción  |
| :--- | :--- | :--- | 
| **GET** | `/orders/{order_id}` | Consulta el estado, unidades y total de un pedido |
| **POST** | `/orders/{order_id}/confirm` | Confirma un pedido en borrador | 
| **POST** | `/orders/{order_id}/ship` | Registra el envío del pedido con su guía |
| **POST** | `/orders/{order_id}/cancel` | Cancela un pedido confirmado indicando motivo |

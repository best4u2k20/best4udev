def serialize_order(order):
    order_json = order.read(
        fields=[
            'id',
            'name',
            'currency_id',
            'order_line',
            'amount_untaxed',
            'amount_tax',
            'amount_total',
            'amount_undiscounted',
            'cart_quantity'
        ]
    )

    for order_elem in order_json:
        order_elem['order_line'] = [serialize_order_line(order_line) for order_line in order.order_line]

    return order_json


def serialize_order_line(order_line):
    order_line_json = order_line.read(
        fields=['id', 'name', 'price_unit', 'price_subtotal', 'product_id', 'qty_to_deliver']
    )
    return order_line_json

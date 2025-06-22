from odoo import models, fields


class SaleOrderReport(models.Model):
    _name = "sale.order.category.report"
    _description = "Sale Order Category Analysis"

    order_id = fields.Many2one("sale.order", string="Order")
    category_id = fields.Many2one("product.category", string="Category")
    products_count = fields.Integer(string="Products Count")
    total_qty = fields.Float(string="Total Quantity")
    total_amount = fields.Float(string="Total Amount")
    top_product = fields.Char(string="Top Products")

    def generate_report_data(self, order_id):
        """Генерує дані звіту по категоріях товарів для замовлення"""
        order = self.env["sale.order"].browse(order_id)
        self.search([("order_id", "=", order_id)]).unlink()

        if not order.order_line:
            return

        products_by_category = order.get_products_by_category()
        category_totals = order.calculate_category_totals()
        top_products = order.get_top_products()

        category_names = list(products_by_category.keys())
        categories = self.env["product.category"].search([("name", "in", category_names)])
        category_map = {cat.name: cat.id for cat in categories}

        qty_by_category = {}
        for line in order.order_line:
            category_name = line.product_id.categ_id.name
            qty_by_category[category_name] = qty_by_category.get(category_name, 0) + line.product_uom_qty

        for category_name, products in products_by_category.items():
            self.create({
                "order_id": order.id,
                "category_id": category_map.get(category_name, False),
                "products_count": len(products),
                "total_qty": qty_by_category.get(category_name, 0),
                "total_amount": category_totals.get(category_name, 0.0),
                "top_product": ", ".join(top_products.get(category_name, [])),
            })

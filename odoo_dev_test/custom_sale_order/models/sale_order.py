from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    total_products_count = fields.Integer(
        string="Total Products Count",
        compute="_compute_total_products_count",
        store=True,
    )

    categories_count = fields.Integer(
        string="Categories Count",
        compute="_compute_categories_count",
        store=True,
    )

    most_expensive_line_id = fields.Many2one(
        "sale.order.line",
        string="Most Expensive Line",
        compute="_compute_most_expensive_line",
        store=True,
    )

    discount_percentage = fields.Float(string="Discount (%)")

    order_priority = fields.Selection(
        [
            ("normal", "Normal"),
            ("high", "High"),
            ("urgent", "Urgent"),
        ],
        string="Order Priority",
    )

    delivery_notes = fields.Text(string="Delivery Notes")

    @api.depends("order_line.product_uom_qty")
    def _compute_total_products_count(self):
        """Обчислення загальної кількості товарів"""
        for order in self:
            order.total_products_count = sum(line.product_uom_qty for line in order.order_line)

    @api.depends("order_line.product_id.categ_id")
    def _compute_categories_count(self):
        """Підрахунок унікальних категорій"""
        for order in self:
            categories = {line.product_id.categ_id.id for line in order.order_line if line.product_id.categ_id}
            order.categories_count = len(categories)

    @api.depends("order_line.price_subtotal")
    def _compute_most_expensive_line(self):
        """Знаходження найдорожчої позиції"""
        for order in self:
            order.most_expensive_line_id = max(order.order_line, key=lambda l: l.price_subtotal, default=False)

    def get_products_by_category(self):
        """Повертає словник з товарами згрупованими по категоріях"""
        self.ensure_one()
        result = {}
        for line in self.order_line:
            prod_category = line.product_id.categ_id.name if line.product_id.categ_id else "No Category"
            result.setdefault(prod_category, []).append(line.product_id.name)
        return result

    def calculate_category_totals(self):
        """Розраховує загальну суму для кожної категорії"""
        self.ensure_one()
        result = {}
        for line in self.order_line:
            prod_category = line.product_id.categ_id.name if line.product_id.categ_id else "No Category"
            result[prod_category] = result.get(prod_category, 0.0) + line.price_subtotal
        return result

    def get_top_products(self, limit=2):
        """Повертає топ товарів за сумою для кожної категорії"""
        self.ensure_one()
        category_lines = {}
        for line in self.order_line:
            category = line.product_id.categ_id
            category_name = category.name if category else "No Category"
            category_lines.setdefault(category_name, []).append(line)

        result = {}
        for category_name, lines in category_lines.items():
            sorted_lines = sorted(lines, key=lambda l: l.price_subtotal, reverse=True)
            top_products = [line.product_id.name for line in sorted_lines[:limit]]
            result[category_name] = top_products
        return result

    @api.onchange("discount_percentage")
    def _onchange_discount_percentage(self):
        """Застосовуює знижку до всіх позицій замовлення"""
        discount = self.discount_percentage or 0.0
        for line in self.order_line:
            original_price = line.product_id.lst_price
            line.price_unit = original_price * (1 - discount / 100)

    @api.constrains("discount_percentage")
    def _check_discount_percentage(self):
        for order in self:
            if order.discount_percentage < 0 or order.discount_percentage > 100:
                raise ValidationError("Discount percentage must be between 0 and 100!")

    def action_open_category_report(self):
        """Генерує та відкриває звіт за категоріями товарів для поточного замовлення"""
        self.ensure_one()
        self.env["sale.order.category.report"].generate_report_data(self.id)
        return {
            "type": "ir.actions.act_window",
            "name": "Category Report",
            "res_model": "sale.order.category.report",
            "view_mode": "list",
            "domain": [("order_id", "=", self.id)],
            "target": "current",
        }

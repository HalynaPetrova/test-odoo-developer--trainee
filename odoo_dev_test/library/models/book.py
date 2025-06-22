from odoo import models, fields, api


class Book(models.Model):
    _name = "library.book"
    _description = "Library Book"

    name = fields.Char(string="Title", required=True)
    author_id = fields.Many2one(
        "library.author",
        string="Author",
        required=True
    )
    isbn = fields.Char(string="ISBN", required=True)
    publication_date = fields.Date(string="Publication Date")
    pages = fields.Integer(string="Pages")
    is_available = fields.Boolean(string="Is available")
    description = fields.Text(string="Description")

    _sql_constraints = [
        ("unique_isbn", "UNIQUE(isbn)", "ISBN must be unique!"),
    ]

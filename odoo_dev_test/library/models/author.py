from odoo import models, fields, api


class Author(models.Model):
    _name = "library.author"
    _description = "Library Author"

    name = fields.Char(string="Name", required=True)
    birth_date = fields.Date(string="Birth Date")
    country = fields.Char(string="Country")
    book_ids = fields.One2many(
        "library.book",
        "author_id",
        string="Books"
    )
    books_count = fields.Integer(
        string="Books Count",
        compute="_compute_book_count",
        store=True
    )

    @api.depends("book_ids")
    def _compute_book_count(self):
        for author in self:
            author.books_count = len(author.book_ids)

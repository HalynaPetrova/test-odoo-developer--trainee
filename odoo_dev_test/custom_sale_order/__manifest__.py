{
    "name": "Custom Sales Order",
    "version": "1.0",
    "summary": "Customizations for Sales Orders",
    "description": """
        Module to extend and customize Sales Order functionality.
        Adds new fields and features to sale.order model.
    """,
    "category": "Sales",
    "depends": ["base", "sale"],
    "data": [
        "security/ir.model.access.csv",

        "views/sale_order_report_view.xml",
        "views/sale_order_view.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,

    "license": "LGPL-3",
}

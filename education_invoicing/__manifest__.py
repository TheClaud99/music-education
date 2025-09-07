{
    "name": "Education Invoicing",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "category": "Sales",
    "sequence": 1,
    "complexity": "easy",
    "author": "PESOL, Odoo Community Association (OCA)",
    "website": "https://github.com/TheClaud99/music-education",
    "depends": [
        "education",
        "account",
    ],
    "data": [
        "views/education_invoicing_method_view.xml",
        "views/education_enrollment_view.xml",
        "views/education_course_view.xml",
        "views/account_invoice_view.xml",
        "security/education_invoicing_security.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}

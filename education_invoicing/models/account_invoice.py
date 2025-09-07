from dateutil.relativedelta import relativedelta

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    _order = "date_invoice, amount_total_signed asc"

    enrollment_id = fields.Many2one(
        comodel_name="education.enrollment", string="Enrollment"
    )
    planned_date = fields.Datetime(string="Planned Date")
    enrollment_invoicing_line_id = fields.Many2one(
        comodel_name="education.enrollment.invoicing.line", string="Invoicing Lines"
    )

    def action_invoice_paid(self):
        res = super().action_invoice_paid()
        for record in self:
            if record.state == "paid":
                for lines in record.enrollment_id.invoicing_line_ids:
                    # date = lines.date or self.date_invoice
                    # Mejor cambiar por fecha de factura
                    if (
                        lines.quantity == 1
                        and lines.invoiced
                        and lines.state == "invoiced"
                        and lines.subtotal == record.amount_total
                    ):
                        lines.write({"state": "paid"})
                        if lines.invoice_ids.type == "out_refund":
                            lines.write(
                                {"name": "refund", "subtotal": lines.subtotal * -1}
                            )
        return res

    def action_invoice_open(self):
        super().action_invoice_open()
        invoicing_method_line_obj = self.env["education.enrollment.invoicing.line"]
        line = self.enrollment_invoicing_line_id
        amount = self.amount_total
        date = line.date or fields.Date.today()
        if line.quantity > 1 or line.subtotal != amount:
            self.enrollment_invoicing_line_id = invoicing_method_line_obj.create(
                {
                    "quantity": 1,
                    "invoiced": True,
                    "state": "invoiced",
                    "name": line.name,
                    "subtotal": amount,
                    "date": date,
                    "recurring_interval": line.recurring_interval,
                    "enrollment_id": self.enrollment_id.id,
                }
            )

            line.write(
                {
                    "quantity": line.quantity - 1,
                    "date": fields.Date.from_string(date) + relativedelta(months=1),
                }
            )
        else:
            line.write({"invoiced": True, "state": "invoiced"})

    def paid_and_validate(self):
        self.action_invoice_open()
        journal_id = (
            self.env["account.journal"]
            .search([])
            .filtered(
                lambda t: t.type == "sale" and t.company_id.id == self.env.company.id
            )
        )
        self.pay_and_reconcile(journal_id.id)
        self.action_invoice_paid()

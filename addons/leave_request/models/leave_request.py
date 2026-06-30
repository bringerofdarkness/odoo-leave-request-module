from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LeaveRequest(models.Model):
    _name = "leave.request"
    _description = "Leave Request"
    _order = "id desc"

    name = fields.Char(string="Reference", default="New", readonly=True)

    employee_name = fields.Char(string="Employee Name", required=True)

    leave_type = fields.Selection([
        ("sick", "Sick Leave"),
        ("casual", "Casual Leave"),
        ("annual", "Annual Leave"),
        ("unpaid", "Unpaid Leave"),
    ], string="Leave Type", required=True)

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    reason = fields.Text(string="Reason")

    approver_name = fields.Char(string="Approver")

    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ], default="draft", string="Status")

    total_days = fields.Integer(
        string="Total Days",
        compute="_compute_total_days",
        store=True
    )

    @api.depends("start_date", "end_date")
    def _compute_total_days(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                rec.total_days = (rec.end_date - rec.start_date).days + 1
            else:
                rec.total_days = 0

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                if rec.end_date < rec.start_date:
                    raise ValidationError("End Date cannot be before Start Date")

    def action_submit(self):
        for rec in self:
            rec.state = "submitted"

    def action_approve(self):
        for rec in self:
            rec.state = "approved"

    def action_reject(self):
        for rec in self:
            rec.state = "rejected"

    def action_reset_draft(self):
        for rec in self:
            rec.state = "draft"
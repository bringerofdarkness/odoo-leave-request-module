from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LeaveRequest(models.Model):
    _name = "leave.request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Leave Request"
    _order = "id desc"

    # =====================
    # BASIC INFO
    # =====================
    name = fields.Char(
        string="Reference",
        default="New",
        readonly=True,
        copy=False,
        tracking=True
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        default=lambda self: self.env["hr.employee"].search([("user_id", "=", self.env.user.id)], limit=1),
        required=True,
        tracking=True
    )

    leave_type = fields.Selection([
        ("sick", "Sick Leave"),
        ("casual", "Casual Leave"),
        ("annual", "Annual Leave"),
        ("unpaid", "Unpaid Leave"),
    ], string="Leave Type", required=True, tracking=True)

    start_date = fields.Date(string="Start Date", required=True, tracking=True)
    end_date = fields.Date(string="End Date", required=True, tracking=True)

    reason = fields.Text(string="Reason")

    approver_id = fields.Many2one(
        "hr.employee",
        string="Approver",
        domain=lambda self: [("user_id.groups_id", "in", [self.env.ref("leave_request.group_leave_manager").id])],
        required=True,
        tracking=True
    )

  
    # Workflow 

    status = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ], default="draft", string="Status", tracking=True)

    # =====================
    # COMPUTED FIELD
    # =====================
    total_leave_days = fields.Integer(
        string="Total Leave Days",
        compute="_compute_total_leave_days",
        store=True,
        tracking=True
    )

    @api.depends("start_date", "end_date")
    def _compute_total_leave_days(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                if rec.end_date < rec.start_date:
                    rec.total_leave_days = 0
                else:
                    rec.total_leave_days = (rec.end_date - rec.start_date).days + 1
            else:
                rec.total_leave_days = 0


    # Dynamic UI date restriction 

    @api.onchange("start_date", "end_date")
    def _onchange_dates(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                self.end_date = self.start_date
                return {
                    "warning": {
                        "title": "Invalid Date Range",
                        "message": "End Date cannot be before Start Date. The End Date has been reset to match the Start Date.",
                    }
                }

    @api.constrains("start_date", "end_date", "employee_id")
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                if rec.end_date < rec.start_date:
                    raise ValidationError(
                        "End Date cannot be before Start Date."
                    )

    @api.constrains("start_date", "end_date", "employee_id", "status")
    def _check_overlapping_leaves(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.employee_id and rec.status in ["submitted", "approved"]:
                overlapping = self.env["leave.request"].search([
                    ("employee_id", "=", rec.employee_id.id),
                    ("id", "!=", rec.id),
                    ("status", "in", ["submitted", "approved"]),
                    ("start_date", "<=", rec.end_date),
                    ("end_date", ">=", rec.start_date),
                ])
                if overlapping:
                    raise ValidationError(
                        f"Overlapping leave request found! Employee '{rec.employee_id.name}' already has an approved or submitted "
                        f"leave request ({overlapping[0].name}) from {overlapping[0].start_date} to {overlapping[0].end_date}."
                    )

    @api.constrains("status", "total_leave_days")
    def _check_annual_leave_limit(self):
        for rec in self:
            if rec.status == "approved":
                current_year = fields.Date.today().year
                start_of_year = fields.Date.to_date(f"{current_year}-01-01")
                end_of_year = fields.Date.to_date(f"{current_year}-12-31")
                
                approved_leaves = self.env["leave.request"].search([
                    ("employee_id", "=", rec.employee_id.id),
                    ("status", "=", "approved"),
                    ("start_date", ">=", start_of_year),
                    ("end_date", "<=", end_of_year),
                    ("id", "!=", rec.id)
                ])
                total_approved_days = sum(approved_leaves.mapped("total_leave_days"))
                
                max_limit = 20
                if total_approved_days + rec.total_leave_days > max_limit:
                    remaining = max_limit - total_approved_days
                    raise ValidationError(
                        f"Leave request cannot be approved. Employee '{rec.employee_id.name}' has already used "
                        f"{total_approved_days} of their {max_limit} days annual leave limit. "
                        f"Remaining balance: {max(0, remaining)} days."
                    )


    # ORM overrides

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("leave.request") or "New"
        return super(LeaveRequest, self).create(vals_list)

    def write(self, vals):
        for rec in self:
            # Prevent non-managers from editing requests that are not in draft
            if rec.status != "draft" and not self.env.user.has_group("leave_request.group_leave_manager"):
                # Exception: Allow updating tracking/system fields or state transitions
                allowed_fields = {"status", "message_main_attachment_id"}
                if not set(vals.keys()).issubset(allowed_fields):
                    raise ValidationError(
                        "You can only edit leave requests in the 'Draft' state."
                    )
        return super(LeaveRequest, self).write(vals)

    def unlink(self):
        for rec in self:
            if rec.status != "draft" and not self.env.user.has_group("leave_request.group_leave_manager"):
                raise ValidationError(
                    "You can only delete leave requests in the 'Draft' state."
                )
        return super(LeaveRequest, self).unlink()


    # Workflow actions

    def action_submit(self):
        for rec in self:
            if rec.status != "draft":
                raise ValidationError("Only draft requests can be submitted.")
            rec.status = "submitted"
            
            # Post a message in the chatter
            rec.message_post(body="Leave request submitted for approval.")

            # Send Email Notification
            template = self.env.ref("leave_request.mail_template_leave_submitted", raise_if_not_found=False)
            if template:
                template.send_mail(rec.id, force_send=True)

            # Create a notification activity for the assigned approver
            if rec.approver_id and rec.approver_id.user_id:
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary="Leave Request Approval Required",
                    note=f"Please review the leave request submitted by {rec.employee_id.name}.",
                    user_id=rec.approver_id.user_id.id
                )

    def action_approve(self):
        for rec in self:
            if rec.status != "submitted":
                raise ValidationError("Only submitted requests can be approved.")
            
            # Strict Rule: Only the assigned approver can finalize approval
            is_approver = rec.approver_id.user_id == self.env.user
            if not is_approver and not self.env.user._is_admin():
                raise ValidationError("Only the assigned approver can finalize approval.")

            rec.status = "approved"
            rec.message_post(body=f"Leave request approved by {self.env.user.name}.")
            
            # Send email notification
            template = self.env.ref("leave_request.mail_template_leave_approved", raise_if_not_found=False)
            if template:
                template.send_mail(rec.id, force_send=True)

            rec._clear_pending_activities()

    def action_reject(self):
        for rec in self:
            if rec.status != "submitted":
                raise ValidationError("Only submitted requests can be rejected.")

            # Strict Rule: Only the assigned approver can finalize rejection
            is_approver = rec.approver_id.user_id == self.env.user
            if not is_approver and not self.env.user._is_admin():
                raise ValidationError("Only the assigned approver can finalize rejection.")

            rec.status = "rejected"
            rec.message_post(body=f"Leave request rejected by {self.env.user.name}.")

            # Send email 
            template = self.env.ref("leave_request.mail_template_leave_rejected", raise_if_not_found=False)
            if template:
                template.send_mail(rec.id, force_send=True)

            rec._clear_pending_activities()

    def action_reset_draft(self):
        for rec in self:
            rec.status = "draft"
            rec.message_post(body="Leave request reset to draft.")
            rec._clear_pending_activities()

    def _clear_pending_activities(self):
        for rec in self:
            activities = self.env["mail.activity"].search([
                ("res_model", "=", self._name),
                ("res_id", "=", rec.id)
            ])
            if activities:
                activities.action_feedback(feedback="Request processed.")
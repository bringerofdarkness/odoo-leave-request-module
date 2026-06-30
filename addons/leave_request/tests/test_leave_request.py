from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.fields import Date


class TestLeaveRequest(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestLeaveRequest, cls).setUpClass()

        # Get security groups
        cls.group_employee = cls.env.ref("leave_request.group_leave_employee")
        cls.group_manager = cls.env.ref("leave_request.group_leave_manager")

        # Create Test Users
        cls.user_employee = cls.env["res.users"].create({
            "name": "Test Employee",
            "login": "test_emp",
            "email": "emp@test.com",
            "groups_id": [(4, cls.group_employee.id)],
        })

        cls.user_approver = cls.env["res.users"].create({
            "name": "Test Approver Manager",
            "login": "test_app",
            "email": "app@test.com",
            "groups_id": [(4, cls.group_manager.id)],
        })

        cls.user_unauthorized = cls.env["res.users"].create({
            "name": "Test Unauthorized Manager",
            "login": "test_unauth",
            "email": "unauth@test.com",
            "groups_id": [(4, cls.group_manager.id)], # Still a manager, but not the assigned approver
        })

        # Create Corresponding Employee Profiles
        cls.employee_profile = cls.env["hr.employee"].create({
            "name": "Test Employee Profile",
            "user_id": cls.user_employee.id,
        })

        cls.approver_profile = cls.env["hr.employee"].create({
            "name": "Test Approver Profile",
            "user_id": cls.user_approver.id,
        })

        cls.unauth_profile = cls.env["hr.employee"].create({
            "name": "Test Unauth Profile",
            "user_id": cls.user_unauthorized.id,
        })

    def test_01_leave_days_computation_and_validation(self):
        """Test leaf duration computation and end_date validation"""
        # Create a valid request
        request = self.env["leave.request"].with_user(self.user_employee).create({
            "employee_id": self.employee_profile.id,
            "leave_type": "sick",
            "start_date": Date.to_date("2026-07-01"),
            "end_date": Date.to_date("2026-07-05"),
            "approver_id": self.approver_profile.id,
            "reason": "Test Sick Leave",
        })

        # Total days should compute to 5
        self.assertEqual(request.total_leave_days, 5, "Total leave days should compute to 5")

        # Test validation constraint (end_date < start_date)
        with self.assertRaises(ValidationError):
            self.env["leave.request"].with_user(self.user_employee).create({
                "employee_id": self.employee_profile.id,
                "leave_type": "casual",
                "start_date": Date.to_date("2026-07-05"),
                "end_date": Date.to_date("2026-07-01"), # Invalid end date
                "approver_id": self.approver_profile.id,
                "reason": "Invalid Request",
            })

    def test_02_workflow_transitions(self):
        """Test draft -> submitted -> approved flow & auto-activity"""
        # Create draft request
        request = self.env["leave.request"].with_user(self.user_employee).create({
            "employee_id": self.employee_profile.id,
            "leave_type": "annual",
            "start_date": Date.to_date("2026-07-10"),
            "end_date": Date.to_date("2026-07-12"),
            "approver_id": self.approver_profile.id,
        })
        self.assertEqual(request.status, "draft", "Initial status must be 'draft'")

        # Submit request
        request.action_submit()
        self.assertEqual(request.status, "submitted", "Status should transition to 'submitted'")

        # Check that a To-Do activity was generated and assigned to the approver user
        activity = self.env["mail.activity"].search([
            ("res_model", "=", "leave.request"),
            ("res_id", "=", request.id)
        ])
        self.assertTrue(activity, "An activity should be created upon submission")
        self.assertEqual(activity.user_id, self.user_approver, "Activity should be assigned to the approver")

        # Approve request (using the assigned approver user)
        request.with_user(self.user_approver).action_approve()
        self.assertEqual(request.status, "approved", "Status should transition to 'approved'")

        # Check that the activity is completed/deleted
        activity_check = self.env["mail.activity"].search([
            ("res_model", "=", "leave.request"),
            ("res_id", "=", request.id)
        ])
        self.assertFalse(activity_check, "Activity should be marked as completed (removed) after approval")

    def test_03_security_approver_restriction(self):
        """Ensure only the assigned approver can finalize approval/rejection"""
        request = self.env["leave.request"].with_user(self.user_employee).create({
            "employee_id": self.employee_profile.id,
            "leave_type": "unpaid",
            "start_date": Date.to_date("2026-07-20"),
            "end_date": Date.to_date("2026-07-22"),
            "approver_id": self.approver_profile.id,
        })
        request.action_submit()

        # An unauthorized manager (who is NOT the assigned approver) tries to approve
        with self.assertRaises(ValidationError):
            request.with_user(self.user_unauthorized).action_approve()

        # The assigned approver approves
        request.with_user(self.user_approver).action_approve()
        self.assertEqual(request.status, "approved", "Assigned approver should successfully approve")

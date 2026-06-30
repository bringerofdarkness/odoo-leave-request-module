{
    "name": "Leave Request Approval",
    "version": "1.0",
    "summary": "Employee Leave Request Management System",
    "author": "zk",
    "depends": ["base", "mail", "hr"],
    "data": [
        "security/leave_request_security.xml",
        "security/ir.model.access.csv",
        "data/leave_request_data.xml",
        "data/leave_request_mail_templates.xml",
        "views/leave_request_views.xml",
    ],
    "demo": [
        "data/leave_request_demo.xml",
    ],
    "installable": True,
    "application": True,
}
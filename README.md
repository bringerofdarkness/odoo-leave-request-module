```markdown
# 🚀 Leave Request Approval Module (Odoo 17)

A production-style **Odoo 17 custom module** that streamlines employee leave management with HR integration, role-based access control, automated approval workflows, and analytical reporting.

This project showcases practical Odoo development skills, including ORM modeling, workflow automation, security rules, XML views, Docker deployment, and reporting dashboards.

---

## 📋 Table of Contents

- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Project Workflow](#-project-workflow)
- [Installation](#-installation)
- [Usage](#-usage)
- [Technical Design](#-technical-design)
- [Security Model](#-security-model)
- [Reporting](#-reporting)
- [Author](#-author)

---

## ✨ Features

### 👨‍💼 Leave Management
- Create employee leave requests
- Multi-stage approval workflow
- Leave duration calculation
- Reset rejected requests back to draft

### 🏢 HR Integration
- Uses the built-in `hr.employee` model
- Links employees and approvers to HR records
- No duplicate employee data

### 🔒 Role-Based Security
- Employee access limited to their own requests
- Managers have full system access
- Record Rules enforce row-level security

### 🤖 Workflow Automation
- Automatic approval activities for approvers
- Chatter logs every workflow action
- Activities are automatically completed after approval or rejection

### 📊 Analytics
- Kanban workflow pipeline
- Pivot reports
- Graph reports
- Search filters for common scenarios

### 🐳 Deployment
- Fully Dockerized
- PostgreSQL database
- Odoo 17 environment
- Quick setup on any machine

---

## 🛠️ Technology Stack

- **Odoo 17**
- **Python (Odoo ORM)**
- **PostgreSQL**
- **Docker & Docker Compose**
- **XML Views**
- **Odoo Security (ACL & Record Rules)**
- **Mail Thread**
- **Mail Activities**

---

## 🔄 Project Workflow

```text
Draft
   │
   ▼
Submitted
   │
   ├────────► Approved
   │
   └────────► Rejected
                    │
                    ▼
             Reset to Draft
```

---

# 🖥️ Installation

## 1. Prerequisites

Install the following software:

- Docker Desktop
- Docker Compose
- Git (optional)

---

## 2. Clone the Repository

```bash
git clone https://github.com/bringerofdarkness/odoo-leave-request-module.git
cd odoo-leave-request-module
```

---

## 3. Start the Application

Run:

```bash
docker compose up -d
```

This starts:

- Odoo 17
- PostgreSQL

---

## 4. Open Odoo

Visit:

```text
http://localhost:8070
```

---

## 5. Create a Database (First Run Only)

Use the following values:

| Field | Value |
|-------|-------|
| Master Password | Check `docker-compose.yml` |
| Database Name | `leave_db` |
| Email | `admin` |
| Password | `admin` |

---

## 6. Install the Module

Inside Odoo:

1. Enable **Developer Mode**
2. Open **Apps**
3. Click **Update Apps List**
4. Search for **Leave Request Approval**
5. Click **Install**

---

# 🚀 Usage

## Employee

- Create a leave request
- Select leave type
- Choose start and end dates
- Submit for approval

## Approver

- Receive an activity notification
- Review the request
- Approve or reject

## Manager

- Access every leave request
- Approve or reject any request
- View analytics dashboards

---

# 🧠 Technical Design

## Model

```
leave.request
```

### Inherits

- `mail.thread`
- `mail.activity.mixin`

---

## Main Fields

| Field | Description |
|--------|-------------|
| `name` | Auto-generated sequence |
| `employee_id` | Employee requesting leave |
| `approver_id` | Assigned approver |
| `leave_type` | Leave category |
| `start_date` | Leave start date |
| `end_date` | Leave end date |
| `total_leave_days` | Computed leave duration |
| `status` | Workflow state |

---

## Business Logic

### Leave Duration

```python
(end_date - start_date).days + 1
```

### Validation Rules

- End date cannot be before the start date.
- Only the assigned approver or an HR manager can approve or reject requests.
- Workflow transitions follow predefined business rules.

---

# 🔐 Security Model

## User Groups

### Employee

- Can create leave requests
- Can view their own requests
- Can see requests assigned to them for approval

### Manager

- Full access to all records
- Can approve or reject any request

---

## Record Rules

### Employee Rule

```python
[
    '|',
    ('employee_id.user_id', '=', user.id),
    ('approver_id.user_id', '=', user.id)
]
```

### Manager Rule

```python
[(1, '=', 1)]
```

---

# 📈 Reporting

The module includes multiple reporting views:

### 📊 Pivot View

Analyze leave requests by:

- Employee
- Leave Type
- Status

### 📉 Graph View

Visualize:

- Leave distribution
- Approval trends
- Employee leave statistics

### 🔍 Search Filters

- My Requests
- Pending Approvals
- Assigned to Me

---

# 📂 Project Highlights

- ✅ Clean Odoo ORM implementation
- ✅ Production-style module architecture
- ✅ HR module integration
- ✅ Computed fields
- ✅ Business validations
- ✅ Role-based security
- ✅ Record Rules
- ✅ Mail Activities
- ✅ Chatter integration
- ✅ Kanban workflow
- ✅ Pivot reporting
- ✅ Graph reporting
- ✅ Dockerized deployment

---

# 👤 Author

**Md. Shahrul Zakaria**

Software Engineering Graduate | Odoo Developer | Python Developer

GitHub: https://github.com/bringerofdarkness

---
```
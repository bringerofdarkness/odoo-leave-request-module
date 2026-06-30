# 🚀 Leave Request Approval Module (Odoo 17)

A production-style **Odoo 17 custom module** that streamlines employee leave management with HR integration, role-based access control, automated approval workflows, and analytical reporting.

This project showcases practical Odoo development skills, including ORM modeling, workflow automation, security rules, XML views, Docker deployment, and reporting dashboards.

---

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Workflow](#project-workflow)
- [Installation](#installation)
- [Database Access (pgAdmin 4)](#database-access-pgadmin-4)
- [Usage](#usage)
- [Technical Design](#technical-design)
- [Security Model](#security-model)
- [Reporting](#reporting)
- [Author](#author)

---

## Features

### 👨💼 Leave Management
- Create employee leave requests
- Multi-stage approval workflow (Draft, Submitted, Approved, Rejected)
- Computed leave duration calculation
- Reset rejected requests back to draft

### 🏢 HR Integration
- Uses Odoo's native **`hr.employee`** model
- Links employees and approvers to official HR records
- Pre-populates the employee field based on the logged-in user profile

### 🔒 Role-Based Security (RBAC)
- Employee access limited to their own requests or requests assigned to them for approval
- Managers have full system access
- Buttons like **Approve** and **Reject** are dynamically hidden in the UI for regular employees using group constraints

### 🤖 Workflow Automation
- Automatic approval activities/tasks generated for approvers upon submission
- Chatter logs every workflow action and status change
- Activities are automatically marked as completed after approval or rejection

### 📊 Analytics & Dashboards
- Kanban workflow pipeline grouped by status
- Pivot table reports
- Graph chart reports
- Search filters for common scenarios (My Requests, Pending Approval)

### 🐳 Deployment
- Fully Dockerized (Odoo 17 + PostgreSQL 15)
- Quick setup on any machine with isolated volumes

---

## Technology Stack

- **Odoo 17**
- **Python (Odoo ORM)**
- **PostgreSQL 15**
- **Docker & Docker Compose**
- **XML Views**
- **Odoo Security (ACL & Record Rules)**
- **Mail Thread & Activities**

---

## Project Workflow

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

## Installation

### 1. Prerequisites
Install the following software:
- Docker Desktop
- Docker Compose
- pgAdmin 4 (optional, for database inspection)

---

### 2. Clone the Repository
```bash
git clone https://github.com/bringerofdarkness/odoo-leave-request-module.git
cd odoo-leave-request-module
```

---

### 3. Start the Application
Run:
```bash
docker compose up -d
```
This starts Odoo 17 on port `8070` and PostgreSQL on port `5435` in detached mode.

---

### 4. Open Odoo
Visit:
```text
http://localhost:8070
```

---

### 5. Create a Database (First Run Only)
Use the following values on the Odoo database creation page:

| Field | Value |
|-------|-------|
| Master Password | Copy the `admin_passwd` value from `config/odoo.conf` |
| Database Name | `leave_request_db` |
| Email / Login | `admin` |
| Password | `admin` |
| Load Demo Data | Check this box to load sample employee and leave data |

---

### 6. Install the Module
Inside Odoo:
1. Go to **Settings** > scroll to the bottom > click **Activate the developer mode**.
2. Open **Apps**.
3. Click **Update Apps List** in the top menu bar.
4. Search for `Leave Request Approval` (technical name: `leave_request`).
5. Click **Activate** to install.

---

## Database Access (pgAdmin 4)

To inspect the database tables using **pgAdmin 4** installed on your host machine:

1. Open **pgAdmin 4**.
2. Right-click **Servers** > **Register** > **Server...**
3. In the **General** tab, set Name to `Odoo Leave DB`.
4. In the **Connection** tab, input:
   - **Host name/address**: `localhost`
   - **Port**: `5435` (mapped in `docker-compose.yml` to avoid local host conflicts)
   - **Maintenance database**: `postgres`
   - **Username**: `odoo`
   - **Password**: `odoo`
5. Click **Save**.
6. Once connected, browse your tables under:
   `Databases` > `leave_request_db` > `Schemas` > `public` > `Tables` > `leave_request`

---

## Usage

### Employee
- Create a leave request (your Employee profile pre-populates automatically).
- Select leave type.
- Choose start and end dates (warnings trigger if end date is prior to start date).
- Select an approver and click **Submit**.

### Approver
- Receive an activity notification in Odoo.
- Review the request under **Pending Approvals**.
- Click **Approve** or **Reject** (buttons are hidden from regular employees).

### Manager
- Access every leave request in the system.
- View pivot tables, bar charts, and kanban pipelines.

---

## Technical Design

### Model Name
```text
leave.request
```

### Inherits
- `mail.thread`
- `mail.activity.mixin`

---

### Main Fields

| Field | Type | Description |
|--------|------|-------------|
| `name` | Char | Auto-generated sequence (`LR-00001`) |
| `employee_id` | Many2one (`hr.employee`) | Employee requesting leave |
| `approver_id` | Many2one (`hr.employee`) | Assigned approver (filtered to Managers only) |
| `leave_type` | Selection | Sick, Casual, Annual, or Unpaid |
| `start_date` | Date | Leave start date |
| `end_date` | Date | Leave end date |
| `total_leave_days` | Integer | Computed leave duration |
| `status` | Selection | Draft, Submitted, Approved, Rejected |

---

## Business Logic

### Leave Duration
Calculated dynamically in Python:
```python
(end_date - start_date).days + 1
```

### Validation Rules
- End date cannot be before the start date (enforced by python `@api.constrains` and UI-level `@api.onchange`).
- Only the assigned approver can approve or reject the request.

---

## Security Model

### User Groups
1. **Leave Employee** (`group_leave_employee`):
   - Can create and submit requests.
   - Can read and write only their own requests or requests where they are assigned as the approver.
2. **Leave Manager** (`group_leave_manager`):
   - Full read/write/delete access to all records.
   - Can view the Approve/Reject buttons.

---

### Record Rules

#### Employee Rule
```python
['|', ('employee_id.user_id', '=', user.id), ('approver_id.user_id', '=', user.id)]
```

#### Manager Rule
```python
[(1, '=', 1)]
```

---

## Reporting

The module includes multiple visual reporting dashboards:

### 📊 Pivot View
Analyze leave requests with excel-like pivot dimensions by:
- Employee
- Status
- Total leave days (measures)

### 📉 Graph View
Visualize:
- Leave distribution by employee
- Leave categories in bar charts

### 🔍 Search Filters
- My Requests (`[('employee_id.user_id', '=', uid)]`)
- Pending Approvals (`[('status', '=', 'submitted')]`)

---

## Author

**Md. Shahrul Zakaria**

GitHub: [https://github.com/bringerofdarkness](https://github.com/bringerofdarkness)
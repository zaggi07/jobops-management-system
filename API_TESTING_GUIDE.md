# JobOps API Testing Guide

## Base URL
```
http://localhost:8000
```

## 1. Authentication Endpoints

### 1.1 Login (Get JWT Token)
```bash
POST /auth/login/
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123"
}

# Response:
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 1.2 Refresh Token
```bash
POST /auth/refresh/
Content-Type: application/json

{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# Response:
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 2. User Management Endpoints

### 2.1 List Users (Role-based)
```bash
GET /api/users/
Authorization: JWT {access_token}

# Admin: sees all users
# Sales Agent: sees only technicians
# Technician: sees no users (403)
```

### 2.2 Create User (Admin Only)
```bash
POST /api/users/
Authorization: JWT {access_token}
Content-Type: application/json

# Create Admin:
{
    "username": "admin2",
    "email": "admin2@example.com",
    "password": "admin123",
    "role": "admin"
}

# Create Technician:
{
    "username": "tech1",
    "email": "tech1@example.com",
    "password": "tech123",
    "role": "technician"
}

# Create Sales Agent:
{
    "username": "sales1",
    "email": "sales1@example.com",
    "password": "sales123",
    "role": "sales_agent"
}
```

### 2.3 Get User Details
```bash
GET /api/users/{id}/
Authorization: JWT {access_token}
```

### 2.4 Update User (Admin Only)
```bash
PUT /api/users/{id}/
Authorization: JWT {access_token}
Content-Type: application/json

{
    "username": "tech1_updated",
    "email": "tech1@example.com",
    "role": "technician"
}

# Password is optional during update
```

### 2.5 Delete User (Admin Only)
```bash
DELETE /api/users/{id}/
Authorization: JWT {access_token}
```

---

## 3. Equipment Endpoints

### 3.1 List Equipment (with Pagination)
```bash
GET /api/equipment/
Authorization: JWT {access_token}

# With filters:
GET /api/equipment/?is_active=true
GET /api/equipment/?type=tool

# With pagination:
GET /api/equipment/?page=1&page_size=10

# Response:
{
    "count": 5,
    "next": "http://localhost:8000/api/equipment/?page=2",
    "previous": null,
    "results": [...]
}
```

### 3.2 Create Equipment
```bash
POST /api/equipment/
Authorization: JWT {access_token}
Content-Type: application/json

{
    "name": "Power Drill Pro",
    "type": "tool",
    "serial_number": "PD-2024-001",
    "is_active": true
}

# Machine Example:
{
    "name": "Excavator JCB",
    "type": "machine",
    "serial_number": "EXC-2024-001",
    "is_active": true
}

# Vehicle Example:
{
    "name": "Service Van",
    "type": "vehicle",
    "serial_number": "VAN-2024-001",
    "is_active": true
}

# Device Example:
{
    "name": "Laser Level",
    "type": "device",
    "serial_number": "LL-2024-001",
    "is_active": true
}
```

### 3.3 Get Equipment Details
```bash
GET /api/equipment/{id}/
Authorization: JWT {access_token}
```

### 3.4 Update Equipment
```bash
PUT /api/equipment/{id}/
Authorization: JWT {access_token}
Content-Type: application/json

{
    "name": "Power Drill Pro - Updated",
    "type": "tool",
    "serial_number": "PD-2024-001",
    "is_active": false
}
```

### 3.5 Delete Equipment
```bash
DELETE /api/equipment/{id}/
Authorization: JWT {access_token}
```

---

## 4. Job Endpoints

### 4.1 List Jobs (Role-based + Pagination)
```bash
GET /api/jobs/
Authorization: JWT {access_token}

# With pagination:
GET /api/jobs/?page=1&page_size=10

# Admin: sees all jobs
# Sales Agent: sees only created jobs
# Technician: sees only assigned jobs

# Response:
{
    "count": 10,
    "next": "http://localhost:8000/api/jobs/?page=2",
    "previous": null,
    "results": [...]
}
```

### 4.2 Create Job (Admin/Sales Agent Only)
```bash
POST /api/jobs/
Authorization: JWT {access_token}
Content-Type: application/json

{
    "title": "Security System Installation at ABC Corp",
    "description": "Complete security camera installation with alarm system integration",
    "client_name": "ABC Corporation",
    "assigned_to": 2,
    "priority": "high",
    "scheduled_date": "2025-10-20T09:00:00Z"
}

# Medium Priority Example:
{
    "title": "Network Infrastructure Setup",
    "description": "Setup complete network infrastructure including routers and switches",
    "client_name": "XYZ Technologies",
    "assigned_to": 2,
    "priority": "medium",
    "scheduled_date": "2025-10-21T10:00:00Z"
}

# Urgent Example:
{
    "title": "Emergency Repair - Power Outage",
    "description": "Fix electrical system causing power outages",
    "client_name": "DEF Industries",
    "assigned_to": 2,
    "priority": "urgent",
    "scheduled_date": "2025-10-19T08:00:00Z"
}

# Low Priority Example:
{
    "title": "Routine Maintenance Check",
    "description": "Regular quarterly maintenance inspection",
    "client_name": "GHI Services",
    "assigned_to": 2,
    "priority": "low",
    "scheduled_date": "2025-10-25T14:00:00Z"
}
```

### 4.3 Get Job Details
```bash
GET /api/jobs/{id}/
Authorization: JWT {access_token}

# Response includes nested tasks:
{
    "id": 1,
    "title": "Security System Installation",
    "description": "Complete installation",
    "client_name": "ABC Corp",
    "created_by": {...},
    "assigned_to": {...},
    "status": "pending",
    "priority": "high",
    "scheduled_date": "2025-10-20T09:00:00Z",
    "overdue": false,
    "job_tasks": [...]
}
```

### 4.4 Update Job
```bash
PUT /api/jobs/{id}/
Authorization: JWT {access_token}
Content-Type: application/json

{
    "title": "Security System Installation - Updated",
    "description": "Updated scope with additional cameras",
    "client_name": "ABC Corporation",
    "assigned_to": 2,
    "priority": "urgent",
    "status": "in_progress",
    "scheduled_date": "2025-10-20T09:00:00Z"
}
```

### 4.5 Mark Job as Completed (Technician Only)
```bash
POST /api/jobs/{id}/mark_completed/
Authorization: JWT {access_token}

# Success Response:
{
    "message": "Job marked as completed successfully."
}

# Error Response (if tasks incomplete):
{
    "error": "Cannot complete job. All tasks must be completed first."
}
```

### 4.6 Job Analytics (Admin Only)
```bash
GET /api/jobs/analytics/
Authorization: JWT {access_token}

# Response:
{
    "total_jobs": 15,
    "completed_jobs": 8,
    "pending_jobs": 5,
    "overdue_jobs": 2,
    "average_task_time": "2 days, 5:30:00",
    "most_used_equipment": [
        {
            "id": 1,
            "name": "Power Drill",
            "type": "tool",
            "usage_count": 12
        },
        {
            "id": 3,
            "name": "Service Van",
            "type": "vehicle",
            "usage_count": 8
        }
    ]
}
```

### 4.7 Delete Job
```bash
DELETE /api/jobs/{id}/
Authorization: JWT {access_token}
```

---

## 5. Job Tasks Endpoints (Nested)

### 5.1 List Job Tasks
```bash
GET /api/jobs/{job_id}/tasks/
Authorization: JWT {access_token}
```

### 5.2 Create Job Task
```bash
POST /api/jobs/{job_id}/tasks/
Authorization: JWT {access_token}
Content-Type: application/json

# Task 1 - Installation step:
{
    "title": "Install Security Cameras",
    "description": "Install 8 security cameras in designated locations",
    "step": "installation",
    "order": 1,
    "status": "pending",
    "equipment_ids": [1, 2]
}

# Task 2 - Testing step:
{
    "title": "System Testing",
    "description": "Complete system testing and verification",
    "step": "testing",
    "order": 2,
    "status": "pending",
    "equipment_ids": []
}

# Task 3 - Training step:
{
    "title": "Client Training",
    "description": "Train client staff on system usage",
    "step": "training",
    "order": 3,
    "status": "pending",
    "equipment_ids": []
}

# Available steps: inspection, installation, testing, configuration, training, maintenance, repair, other
# Note: 'step' categorizes the task type, 'order' maintains sequence
```

### 5.3 Get Task Details
```bash
GET /api/jobs/{job_id}/tasks/{task_id}/
Authorization: JWT {access_token}
```

### 5.4 Update Job Task
```bash
PUT /api/jobs/{job_id}/tasks/{task_id}/
Authorization: JWT {access_token}
Content-Type: application/json

{
    "title": "Install Security Cameras - Updated",
    "description": "Updated description with additional details",
    "step": "installation",
    "order": 1,
    "status": "in_progress",
    "equipment_ids": [1, 2, 3]
}
```

### 5.5 Mark Task as Completed
```bash
POST /api/jobs/{job_id}/tasks/{task_id}/mark_completed/
Authorization: JWT {access_token}

# Response:
{
    "message": "Task marked as completed successfully."
}
```

### 5.6 Add Equipment to Task
```bash
POST /api/jobs/{job_id}/tasks/{task_id}/add-equipment/
Authorization: JWT {access_token}
Content-Type: application/json

{
    "equipment_ids": [1, 3, 5]
}

# Response:
{
    "message": "3 equipment(s) added successfully."
}

# Error Response:
{
    "error": "equipment_ids required"
}
```

### 5.7 Remove Equipment from Task
```bash
POST /api/jobs/{job_id}/tasks/{task_id}/remove-equipment/
Authorization: JWT {access_token}
Content-Type: application/json

{
    "equipment_ids": [2]
}

# Response:
{
    "message": "1 equipment(s) removed successfully."
}
```

### 5.8 Delete Job Task
```bash
DELETE /api/jobs/{job_id}/tasks/{task_id}/
Authorization: JWT {access_token}
```

---

## 6. Job History Endpoints (Nested)

### 6.1 List Job Change History
```bash
GET /api/jobs/{job_id}/history/
Authorization: JWT {access_token}

# Response:
[
    {
        "id": 1,
        "job": 1,
        "task": null,
        "action": "created",
        "changed_by": {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "role": "admin"
        },
        "old_value": null,
        "new_value": {
            "title": "Security System Installation",
            "status": "pending",
            "priority": "high"
        },
        "timestamp": "2025-10-18T10:00:00Z"
    },
    {
        "id": 2,
        "job": 1,
        "task": 1,
        "action": "status_changed",
        "changed_by": {...},
        "old_value": {"status": "pending"},
        "new_value": {"status": "in_progress"},
        "timestamp": "2025-10-18T11:00:00Z"
    }
]
```

### 6.2 Get Specific History Entry
```bash
GET /api/jobs/{job_id}/history/{history_id}/
Authorization: JWT {access_token}
```

---

## 7. Technician Dashboard

### 7.1 Get Technician Dashboard (Technician Only)
```bash
GET /api/technician-dashboard/
Authorization: JWT {access_token}

# Response: Tasks grouped by scheduled date
[
    {
        "date": "2025-10-20",
        "tasks": [
            {
                "id": 1,
                "title": "Install Security Cameras",
                "description": "Install 8 cameras",
                "status": "pending",
                "job": {
                    "id": 1,
                    "title": "Security System Installation",
                    "client_name": "ABC Corp",
                    "scheduled_date": "2025-10-20T09:00:00Z"
                },
                "required_equipment": [
                    {
                        "id": 1,
                        "name": "Power Drill",
                        "type": "tool"
                    }
                ],
                "is_overdue": false
            }
        ]
    },
    {
        "date": "2025-10-21",
        "tasks": [...]
    }
]
```

---

## 8. Testing Sequence (Complete Flow)

### Step 1: Initial Setup
```bash
# 1. Create admin user (if not exists)
python manage.py setup_admin

# 2. Start server
python manage.py runserver

# 3. Login as admin
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Save the access token for next requests
export TOKEN="your_access_token_here"
```

### Step 2: Create Users
```bash
# Create Technician
curl -X POST http://localhost:8000/api/users/ \
  -H "Authorization: JWT $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "tech1",
    "email": "tech1@example.com",
    "password": "tech123",
    "role": "technician"
  }'

# Create Sales Agent
curl -X POST http://localhost:8000/api/users/ \
  -H "Authorization: JWT $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "sales1",
    "email": "sales1@example.com",
    "password": "sales123",
    "role": "sales_agent"
  }'
```

### Step 3: Create Equipment
```bash
# Create Power Drill
curl -X POST http://localhost:8000/api/equipment/ \
  -H "Authorization: JWT $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Power Drill",
    "type": "tool",
    "serial_number": "PD-001",
    "is_active": true
  }'

# Create Service Van
curl -X POST http://localhost:8000/api/equipment/ \
  -H "Authorization: JWT $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Service Van",
    "type": "vehicle",
    "serial_number": "VAN-001",
    "is_active": true
  }'

# Create Laser Level
curl -X POST http://localhost:8000/api/equipment/ \
  -H "Authorization: JWT $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laser Level",
    "type": "device",
    "serial_number": "LL-001",
    "is_active": true
  }'
```

### Step 4: Create Job
```bash
# Create job (technician_id = 2)
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Authorization: JWT $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Home Security Installation",
    "description": "Complete home security system installation",
    "client_name": "John Doe",
    "assigned_to": 2,
    "priority": "high",
    "scheduled_date": "2025-10-20T09:00:00Z"
  }'

# Note the job_id from response (e.g., 1)
```

### Step 5: Create Tasks
```bash
# Task 1 - Installation step with equipment
curl -X POST http://localhost:8000/api/jobs/1/tasks/ \
  -H "Authorization: JWT $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Install Cameras",
    "description": "Install all security cameras",
    "step": "installation",
    "order": 1,
    "status": "pending",
    "equipment_ids": [1]
  }'

# Task 2 - Configuration step without equipment initially
curl -X POST http://localhost:8000/api/jobs/1/tasks/ \
  -H "Authorization: JWT $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Setup Control Panel",
    "description": "Configure control panel",
    "step": "configuration",
    "order": 2,
    "status": "pending",
    "equipment_ids": []
  }'

# Add equipment to Task 2 later
curl -X POST http://localhost:8000/api/jobs/1/tasks/2/add-equipment/ \
  -H "Authorization: JWT $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_ids": [1, 3]
  }'
```

### Step 6: Login as Technician
```bash
# Login as technician
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"tech1","password":"tech123"}'

# Save tech token
export TECH_TOKEN="technician_access_token"

# View dashboard
curl -X GET http://localhost:8000/api/technician-dashboard/ \
  -H "Authorization: JWT $TECH_TOKEN"

# View assigned jobs
curl -X GET http://localhost:8000/api/jobs/ \
  -H "Authorization: JWT $TECH_TOKEN"
```

### Step 7: Complete Tasks
```bash
# Mark Task 1 as completed
curl -X POST http://localhost:8000/api/jobs/1/tasks/1/mark_completed/ \
  -H "Authorization: JWT $TECH_TOKEN"

# Mark Task 2 as completed
curl -X POST http://localhost:8000/api/jobs/1/tasks/2/mark_completed/ \
  -H "Authorization: JWT $TECH_TOKEN"

# Now mark job as completed
curl -X POST http://localhost:8000/api/jobs/1/mark_completed/ \
  -H "Authorization: JWT $TECH_TOKEN"
```

### Step 8: View History & Analytics
```bash
# View job history
curl -X GET http://localhost:8000/api/jobs/1/history/ \
  -H "Authorization: JWT $TOKEN"

# View analytics (admin only)
curl -X GET http://localhost:8000/api/jobs/analytics/ \
  -H "Authorization: JWT $TOKEN"
```

---

## 9. Common Status Codes

- **200 OK**: Successful GET/PUT request
- **201 Created**: Successful POST request
- **204 No Content**: Successful DELETE request
- **400 Bad Request**: Validation error or missing required fields
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: User doesn't have permission
- **404 Not Found**: Resource not found

---

## 10. Role Permissions Summary

| Endpoint | Admin | Sales Agent | Technician |
|----------|-------|-------------|------------|
| User Management | ✅ Full | ❌ | ❌ |
| User Listing | ✅ All | ✅ Techs Only | ❌ |
| Equipment (View) | ✅ | ✅ | ✅ |
| Equipment (CRUD) | ✅ | ✅ | ✅ |
| Job (Create) | ✅ | ✅ | ❌ |
| Job (View) | ✅ All | ✅ Own Only | ✅ Assigned Only |
| Job (Edit) | ✅ All | ✅ Own Only | ✅ Assigned Only |
| Job (Complete) | ✅ | ❌ | ✅ Assigned Only |
| Task (Create) | ✅ | ❌ | ✅ Assigned Only |
| Task (Edit) | ✅ | ❌ | ✅ Assigned Only |
| Task (Complete) | ✅ | ❌ | ✅ Assigned Only |
| Equipment (Add/Remove) | ✅ | ❌ | ✅ Assigned Only |
| Analytics | ✅ | ❌ | ❌ |
| Technician Dashboard | ✅ | ❌ | ✅ |
| Job History | ✅ | ✅ | ✅ |

---

## 11. Business Rules

### Job Completion
- Job can only be marked completed if **all tasks** are completed
- Attempting to complete with pending tasks returns 400 error

### Job Status Auto-Reset
- If a job is marked as "completed" and new tasks are added, job status automatically reverts to "pending"

### Overdue Detection
- Celery task runs daily to check if `scheduled_date` has passed
- Jobs with overdue tasks are automatically flagged with `overdue=True`

### Task Ordering & Steps
- Each job has multiple ordered tasks representing sequential steps
- **`step`** field categorizes task type: inspection, installation, testing, configuration, training, maintenance, repair, other
- **`order`** field maintains sequence (1, 2, 3...)
- Tasks are automatically sorted by `order` field in responses
- Allows clear workflow representation with defined steps
- Example: Job 1 → Task 1 (step: inspection, order: 1) → Task 2 (step: installation, order: 2) → Task 3 (step: testing, order: 3)

### Equipment Management
- Equipment can be added/removed from tasks anytime
- Only active equipment can be added to tasks
- Tasks can be created without equipment and equipment added later

### Audit Logging
- All job and task changes are automatically logged in `JobChangeHistory`
- Includes: creation, updates, status changes, assignments, completions

---

## 12. Pagination

Pagination is applied to:
- **Jobs** (`/api/jobs/`)
- **Equipment** (`/api/equipment/`)

### Usage
```bash
# Default (10 items per page)
GET /api/jobs/

# Custom page size
GET /api/jobs/?page=1&page_size=20

# Navigate pages
GET /api/jobs/?page=2
```

### Backward Compatibility
If no pagination parameters are provided, the API returns all results directly (no pagination wrapper).

---

## 13. Error Response Format

```json
{
    "error": "Error message here"
}
```

Or for validation errors:
```json
{
    "field_name": ["Error message for this field"]
}
```

---

## 14. Quick Reference

### Get All Endpoints
```bash
# As Admin
GET /api/users/                                    # All users
GET /api/equipment/                                # All equipment
GET /api/jobs/                                     # All jobs
GET /api/jobs/analytics/                           # Analytics
GET /api/jobs/{id}/                                # Job details
GET /api/jobs/{id}/tasks/                          # Job tasks
GET /api/jobs/{id}/history/                        # Job history

# As Technician
GET /api/technician-dashboard/                     # Dashboard
GET /api/jobs/                                     # Assigned jobs only
GET /api/jobs/{id}/tasks/                          # Job tasks
POST /api/jobs/{id}/tasks/{task_id}/mark_completed/ # Complete task
POST /api/jobs/{id}/mark_completed/                # Complete job
POST /api/jobs/{id}/tasks/{task_id}/add-equipment/ # Add equipment
POST /api/jobs/{id}/tasks/{task_id}/remove-equipment/ # Remove equipment

# As Sales Agent
POST /api/jobs/                                    # Create job
GET /api/jobs/                                     # Own jobs only
GET /api/users/                                    # Technicians only
```

---

**For more details, see README.md and DESIGN_DECISIONS.md**

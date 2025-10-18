# JobOps - Internal Operations Management System

A Django REST API system for managing internal operations with role-based access control and job lifecycle management.

## Features

- **User Management** with role-based access (Admin, Technician, Sales Agent)
- **Job Management** with lifecycle tracking
- **Task Management** with equipment assignment
- **Equipment Catalog** with Many-to-Many relationships
- **Technician Dashboard** with day-wise task grouping
- **Job Analytics** for administrators
- **Audit Logging** for all changes
- **JWT Authentication** with role-based permissions
- **Nested API Routes** for clean organization

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Admin User
```bash
python manage.py setup_admin
```

This creates an admin user:
- **Username:** admin
- **Password:** admin123
- **Role:** Admin

### 4. Start Server
```bash
python manage.py runserver
```

Server runs at: **http://localhost:8000**

## Testing the API

### Option 1: Swagger UI (Interactive)
```
http://localhost:8000/api/docs/
```
- Interactive API documentation
- Test endpoints directly in browser
- Authenticate with JWT token
- See request/response examples

### Option 2: ReDoc (Clean Documentation)
```
http://localhost:8000/api/redoc/
```
- Clean, readable API documentation
- All endpoints with descriptions
- Request/response schemas

### Option 3: cURL/Manual Testing

#### Get JWT Token
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

#### Use Token in Requests
```bash
curl http://localhost:8000/api/jobs/ \
  -H "Authorization: JWT YOUR_ACCESS_TOKEN"
```

## API Documentation

- **Swagger UI:** http://localhost:8000/api/docs/ (Interactive)
- **ReDoc:** http://localhost:8000/api/redoc/ (Clean docs)
- **API Testing Guide:** See **API_TESTING_GUIDE.md** for complete examples

## Project Structure

```
core/
├── core/                   # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── jobops/                 # Main application
│   ├── models.py           # User, Equipment, Job, JobTask, JobChangeHistory
│   ├── views.py            # API viewsets
│   ├── serializers.py      # DRF serializers
│   ├── permissions.py      # Role-based permissions
│   ├── signals.py          # Audit logging
│   ├── tasks.py            # Background jobs (optional)
│   ├── pagination.py       # Custom pagination
│   ├── urls.py             # Nested routers
│   ├── admin.py            # Django admin
│   ├── fixtures/           # Sample data
│   └── management/         # Custom commands
├── manage.py
├── requirements.txt
├── README.md
├── API_TESTING_GUIDE.md
├── SETUP_GUIDE.md
└── DESIGN_DECISIONS.md
```

## Admin Panel

Access Django admin at: **http://localhost:8000/admin**
- Login with admin credentials
- Manage all data through UI

## User Roles

### Admin
- Full access to all resources
- User management
- Job analytics
- All CRUD operations

### Sales Agent
- Create jobs
- View own jobs
- View technician list (for assignment)

### Technician
- View assigned jobs and tasks
- Update task progress
- Access technician dashboard
- Mark tasks as completed

## API Endpoints

### Authentication
- `POST /auth/login/` - Get JWT tokens
- `POST /auth/refresh/` - Refresh access token

### Users (Admin only for create/update/delete)
- `GET /api/users/` - List users (Admin: all, Sales: technicians only)
- `POST /api/users/` - Create user (Admin only)
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user (Admin only)
- `DELETE /api/users/{id}/` - Delete user (Admin only)

### Equipment
- `GET /api/equipment/` - List equipment (with pagination)
- `POST /api/equipment/` - Create equipment
- `GET /api/equipment/{id}/` - Get equipment details
- `PUT /api/equipment/{id}/` - Update equipment
- `DELETE /api/equipment/{id}/` - Delete equipment

### Jobs
- `GET /api/jobs/` - List jobs (with pagination, role-filtered)
- `POST /api/jobs/` - Create job (Admin/Sales Agent)
- `GET /api/jobs/{id}/` - Get job details
- `PUT /api/jobs/{id}/` - Update job
- `POST /api/jobs/{id}/mark_completed/` - Mark job completed
- `GET /api/jobs/analytics/` - Get analytics (Admin only)
- `DELETE /api/jobs/{id}/` - Delete job

### Job Tasks (Nested)
- `GET /api/jobs/{id}/tasks/` - List job tasks
- `POST /api/jobs/{id}/tasks/` - Create task
- `GET /api/jobs/{id}/tasks/{task_id}/` - Get task details
- `PUT /api/jobs/{id}/tasks/{task_id}/` - Update task
- `POST /api/jobs/{id}/tasks/{task_id}/mark_completed/` - Mark completed
- `POST /api/jobs/{id}/tasks/{task_id}/add-equipment/` - Add equipment
- `POST /api/jobs/{id}/tasks/{task_id}/remove-equipment/` - Remove equipment
- `DELETE /api/jobs/{id}/tasks/{task_id}/` - Delete task

### Job History (Nested)
- `GET /api/jobs/{id}/history/` - Get job change history

### Technician Dashboard
- `GET /api/technician-dashboard/` - Get day-wise tasks (Technician only)

## Database Models

### User (AbstractUser)
- username, email, password, role
- Roles: admin, technician, sales_agent

### Equipment
- name, type, serial_number, is_active

### Job
- title, description, client_name, created_by, assigned_to
- status, priority, scheduled_date, overdue

### JobTask
- title, description, status, required_equipment (M2M), completed_at

### JobChangeHistory
- job, task, action, changed_by, old_value, new_value, timestamp

## Optional: Celery Background Jobs

### Setup (Optional)
```bash
# Install Redis
sudo apt-get install redis-server

# Run Celery worker
celery -A core worker --loglevel=info

# Run Celery beat (scheduler)
celery -A core beat --loglevel=info
```

### Tasks
- `check_overdue_jobs` - Runs daily to flag overdue jobs
- `cleanup_old_change_history` - Runs weekly to clean old logs

## Load Sample Data

```bash
python manage.py loaddata jobops/fixtures/sample_data.json
```

## Common Commands

```bash
# Check for issues
python manage.py check

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser manually
python manage.py createsuperuser
```

## Production Deployment

### Settings to Update
- Set `DEBUG = False`
- Configure PostgreSQL database
- Set proper `SECRET_KEY`
- Update `ALLOWED_HOSTS`
- Configure `CORS_ALLOWED_ORIGINS`

### Environment Variables (Recommended)
```python
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
```

## Support

For detailed API documentation, see:
- **API_TESTING_GUIDE.md** - All endpoints with examples
- **DESIGN_DECISIONS.md** - Architecture decisions
- **SETUP_GUIDE.md** - Detailed setup instructions

---

**JobOps** - Built with Django REST Framework

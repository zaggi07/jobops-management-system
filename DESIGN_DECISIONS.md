# JobOps - Design Decisions & Architecture

## Overview
This document explains the key design decisions made during the development of the JobOps Internal Operations Management System.

---

## 1. Technology Stack

### Django REST Framework
**Decision:** Used Django REST Framework (DRF) for building the REST API.

**Rationale:**
- Industry-standard framework for building APIs in Django
- Built-in authentication, serialization, and viewsets
- Excellent documentation and community support
- Follows REST architectural principles
- Rapid development with ModelViewSet

### JWT Authentication (SimpleJWT)
**Decision:** Implemented JWT-based authentication using `djangorestframework-simplejwt`.

**Rationale:**
- Stateless authentication - no server-side session storage required
- Scalable for distributed systems
- Token-based approach suitable for mobile and web clients
- Built-in token refresh mechanism for better security
- Industry standard for modern API authentication
- Custom header type (`JWT` instead of `Bearer`) for flexibility

### SQLite for Development
**Decision:** Used SQLite for development database.

**Rationale:**
- Zero configuration required
- Perfect for development and testing
- Easy to migrate to PostgreSQL for production
- Included with Python, no additional installation needed

---

## 2. Database Design

### User Model - AbstractUser Override
**Decision:** Overrode Django's `AbstractUser` directly instead of using OneToOne relationship.

**Rationale:**
- Cleaner model structure - single table for all user data
- No redundant joins when accessing user information
- Direct access to role without extra query
- Follows Django recommendation for new projects
- Simplifies authentication and permissions
- No orphaned records - user and profile always in sync

**Implementation:**
```python
class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Job and JobTask Relationship
**Decision:** Implemented Job as parent entity with JobTask as child (ForeignKey relationship).

**Rationale:**
- Clear hierarchical structure: Job → Multiple Tasks
- Enforces business logic (job completion only when all tasks done)
- Easier to track task progress within a job
- Aligns with real-world workflow
- Status propagation: completed job requires all tasks completed

### Ordered Tasks (Sequential Steps)
**Decision:** Added `order` field to JobTask model for sequential task management.

**Rationale:**
- Tasks represent workflow steps (e.g., inspection → installation → testing)
- `order` field (PositiveIntegerField) maintains task sequence
- Automatic sorting by order in all API responses
- Supports clear project management with defined steps
- Flexible: tasks can be reordered if needed
- Simple integer ordering is more intuitive than complex dependencies

### Equipment Many-to-Many with Tasks
**Decision:** Equipment has M2M relationship with JobTask, not Job.

**Rationale:**
- Equipment is assigned at task level, not job level
- More granular control over equipment allocation
- Different tasks may require different equipment
- Prevents equipment conflicts across tasks
- Flexible equipment management with add/remove actions

**Features:**
- Tasks can be created without equipment
- Equipment can be added/removed anytime via dedicated endpoints
- Only active equipment can be assigned to tasks

### Audit Logging (JobChangeHistory)
**Decision:** Separate model for tracking all changes to Jobs and Tasks.

**Rationale:**
- Complete audit trail for compliance
- Non-intrusive - doesn't affect main models
- Scalable - can be archived/cleaned up separately
- Provides accountability for all actions
- JSONField for flexible old_value/new_value storage

**Logged Actions:**
- Job/Task creation, updates, deletions
- Status changes
- Assignment changes
- Task completions

---

## 3. API Design

### Nested Routers for Related Resources
**Decision:** Used `drf-nested-routers` for Tasks and History under Jobs.

**Rationale:**
- RESTful URL structure: `/api/jobs/{id}/tasks/`
- Clear parent-child relationship in URLs
- Better organization and intuitive API design
- Follows industry best practices
- Automatic parent-child context handling

**Example:**
```
/api/jobs/1/tasks/                     # Tasks for job 1
/api/jobs/1/tasks/5/                   # Specific task in job 1
/api/jobs/1/tasks/5/mark_completed/    # Complete task 5
/api/jobs/1/tasks/5/add-equipment/     # Add equipment to task 5
/api/jobs/1/history/                   # History for job 1
```

### Role-Based Permissions
**Decision:** Custom permission classes for each role type.

**Rationale:**
- Fine-grained access control
- Separation of concerns - each role has specific permissions
- Easy to maintain and extend
- Prevents unauthorized access at API level
- Composable permissions for complex scenarios

**Implemented Permissions:**
- `IsAdminUser` - Admin-only endpoints (user management, analytics)
- `IsAdminOrSalesAgent` - Job creation
- `IsTechnician` - Dashboard access
- `IsAssignedTechnician` - Task operations (only assigned technicians)
- `IsJobOwnerOrAssigned` - Job view/edit

**Access Matrix:**
| Resource | Admin | Sales Agent | Technician |
|----------|-------|-------------|------------|
| Users | Full CRUD | View Techs | None |
| Equipment | Full CRUD | Full CRUD | Full CRUD |
| Jobs (Create) | ✅ | ✅ | ❌ |
| Jobs (View) | All | Own | Assigned |
| Tasks | All | ❌ | Assigned |
| Analytics | ✅ | ❌ | ❌ |
| Dashboard | ✅ | ❌ | ✅ |

### Custom Pagination
**Decision:** Per-viewset pagination for Jobs and Equipment only.

**Rationale:**
- Not all endpoints need pagination
- Jobs and Equipment can grow large
- Other resources (users, tasks per job) remain small
- Backward compatibility: returns direct data if no pagination params
- 10 items per page default (configurable)

**Implementation:**
```python
class JobOpsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
```

---

## 4. Business Logic Implementation

### Job Completion Validation
**Decision:** Jobs can only be completed when all tasks are completed.

**Rationale:**
- Enforces workflow integrity
- Prevents premature job closure
- Aligns with project requirements
- Multi-layer validation: model + serializer + view

**Implementation:**
```python
def mark_completed(self):
    if self.can_be_completed:
        self.status = 'completed'
        self.save()
        return True
    return False
```

### Job Status Auto-Reset
**Decision:** If new tasks are added to a completed job, status reverts to 'pending'.

**Rationale:**
- Maintains data integrity
- Prevents completed jobs with incomplete tasks
- Automatic workflow management
- Reduces manual intervention

**Implementation:** Handled in `log_jobtask_changes` signal.

### Overdue Detection
**Decision:** Automatic overdue flagging with background jobs.

**Rationale:**
- Real-time flag in model (`is_overdue` property)
- Background job for batch updates (performance)
- Separates concerns - model logic vs. bulk operations
- Optional - system works without Celery
- Daily check keeps data current

### Technician Dashboard
**Decision:** Custom endpoint grouping tasks by scheduled date.

**Rationale:**
- Optimized for mobile/web dashboard views
- Pre-grouped data reduces client-side processing
- Follows UX best practices
- Only shows pending/in-progress tasks
- Uses job's scheduled_date for grouping

---

## 5. Signal-Based Architecture

### Automatic Audit Logging
**Decision:** Django signals for automatic change tracking.

**Rationale:**
- Decouples logging from business logic
- Automatic - no manual logging calls needed
- Captures all changes consistently
- Easy to enable/disable

**Signals Implemented:**
- `log_job_changes` - Tracks job creation and updates
- `log_jobtask_changes` - Tracks task changes + auto-reset job status
- `check_job_completion` - Validates job completion rules
- `check_task_completion` - Logs task completions

### Defense in Depth Validation
**Decision:** Validation at multiple layers (serializer, model, signals).

**Rationale:**
- Serializer: API-level validation (user input)
- Model: Data integrity (clean method)
- Signals: Business rules (workflow enforcement)
- No duplicate validations - each layer has specific purpose
- Comprehensive protection against invalid states

---

## 6. Background Tasks (Celery)

### Optional Implementation
**Decision:** Made Celery tasks optional, not mandatory.

**Rationale:**
- System works perfectly without Celery
- Reduces deployment complexity
- Optional as per project requirements
- Easy to enable when needed
- Suitable for small to medium deployments

### Scheduled Tasks
**Decision:** Two background tasks - overdue checking (daily) and history cleanup (weekly).

**Rationale:**
- Daily overdue check keeps data current without overwhelming system
- Weekly cleanup maintains database size
- Reasonable intervals for maintenance tasks
- Can be adjusted based on production needs

**Tasks:**
1. `check_overdue_jobs` - Runs daily at midnight
2. `cleanup_old_change_history` - Runs weekly (keeps last 90 days)

---

## 7. Security Decisions

### JWT Token Configuration
**Decision:** 60-minute access token, 7-day refresh token, custom "JWT" header.

**Rationale:**
- Balance between security and user experience
- Short access token reduces risk if compromised
- Long refresh token avoids frequent re-login
- Custom header type for flexibility
- Industry standard lifetimes

**Configuration:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('JWT',),
}
```

### CORS Configuration
**Decision:** Configured for localhost development with credentials support.

**Rationale:**
- Allows local frontend development
- Supports cookie-based authentication if needed
- Easy to update for production domains
- Follows secure defaults

### Password Management
**Decision:** Write-only password field with conditional requirement.

**Rationale:**
- Required for user creation
- Optional for updates (only update if provided)
- Never returned in responses (write_only=True)
- Hashed automatically by serializer
- Follows security best practices

### Model-Level Validation
**Decision:** Job assignment validation at model level.

**Rationale:**
- Ensures only technicians can be assigned to jobs
- Works with admin panel and API
- Raises ValidationError for invalid assignments
- Called automatically on save()

---

## 8. Code Organization

### App Structure
**Decision:** Single `jobops` app for all functionality.

**Rationale:**
- Cohesive functionality - all related to internal operations
- Easier to maintain with smaller project scope
- Clear separation from Django core app
- Can be split later if project grows

### File Organization
**Decision:** Separate files for models, views, serializers, permissions, signals, tasks, pagination.

**Rationale:**
- Better code organization
- Easy to locate specific functionality
- Follows Django best practices
- Improves maintainability
- Each file has single responsibility

### Management Commands
**Decision:** Custom `setup_admin` command for initial setup.

**Rationale:**
- Simplifies first-time setup
- Idempotent - only creates admin if no users exist
- Reduces manual work
- Useful for development and demos

**Usage:**
```bash
python manage.py setup_admin
```

---

## 9. Testing & Documentation

### Comprehensive API Guide
**Decision:** Detailed API_TESTING_GUIDE.md with all endpoints and examples.

**Rationale:**
- Easy reference for developers and testers
- Complete testing workflow
- Role-based testing scenarios
- cURL examples for command-line testing
- Includes all new features (equipment add/remove)

### Focused README
**Decision:** README.md focuses only on setup and quick start.

**Rationale:**
- Quick onboarding for new developers
- Separate concerns (setup vs API usage vs design)
- Clear project structure overview
- Links to detailed guides

### Design Documentation
**Decision:** Separate DESIGN_DECISIONS.md for architecture explanation.

**Rationale:**
- Explains "why" not just "what"
- Useful for code reviews
- Demonstrates thought process
- Helps future developers understand choices

---

## 10. Performance Optimizations

### Database Indexes
**Decision:** Added indexes on frequently queried fields.

**Rationale:**
- Faster queries on status, date, role fields
- Composite indexes for common query patterns
- Minimal impact on write performance
- Standard database optimization

**Indexed Fields:**
- User: role
- Equipment: type, is_active, serial_number
- Job: status, priority, scheduled_date, overdue, assigned_to
- JobTask: status, order (for efficient sorting)
- JobChangeHistory: job, action, timestamp, changed_by

### Query Optimization
**Decision:** Used `select_related` and `prefetch_related` in viewsets.

**Rationale:**
- Reduces N+1 query problems
- Improves API response time
- Better performance with nested relationships
- Best practice for Django ORM

**Example:**
```python
Job.objects.select_related('created_by', 'assigned_to')
            .prefetch_related('job_tasks')
```

### SQLite Compatibility
**Decision:** Manual calculation for datetime aggregations instead of database Avg().

**Rationale:**
- SQLite stores datetime as text, can't use Avg()
- Manual calculation works across all databases
- Still efficient for reasonable dataset sizes
- Maintains compatibility

---

## 11. Scalability Considerations

### Stateless Authentication
**Decision:** JWT tokens instead of session-based authentication.

**Rationale:**
- Horizontal scaling without shared session storage
- Works across multiple servers
- No database lookup for every request
- Can be cached on client side
- Load balancer friendly

### Background Job Separation
**Decision:** Heavy operations in Celery tasks, not API endpoints.

**Rationale:**
- API remains fast and responsive
- Long-running tasks don't block requests
- Can scale workers independently
- Better user experience
- Asynchronous processing

### Database Choice
**Decision:** SQLite for dev, PostgreSQL recommended for production.

**Rationale:**
- Simple local development
- PostgreSQL handles production load better
- Django ORM abstracts database differences
- Smooth migration path
- PostgreSQL supports advanced features

---

## 12. API Endpoint Decisions

### Equipment Management Actions
**Decision:** Separate `add-equipment` and `remove-equipment` actions instead of always requiring full update.

**Rationale:**
- More intuitive API for mobile/web clients
- Partial updates without fetching current state
- Clearer intent in API calls
- Reduces client complexity
- Follows RESTful action patterns

### Technician Dashboard
**Decision:** Separate endpoint instead of filtering jobs endpoint.

**Rationale:**
- Optimized response format (grouped by date)
- Specific to technician role
- Pre-processed data reduces client logic
- Better performance (only pending/in-progress)
- Clear separation of concerns

### Analytics Endpoint
**Decision:** Non-nested analytics endpoint at `/api/jobs/analytics/`.

**Rationale:**
- Analytics is aggregate data, not specific to one job
- Admin-only access
- Returns system-wide metrics
- Follows REST conventions for collection-level actions

---

## 13. Trade-offs & Future Improvements

### Trade-offs Made

1. **Single App Structure**
   - Pro: Simpler for small project, faster development
   - Con: May need splitting if project grows significantly

2. **SQLite in Development**
   - Pro: Zero setup, easy testing
   - Con: Different from production database (minor differences)

3. **Optional Celery**
   - Pro: Simpler deployment, works without Redis
   - Con: Some features manual without it (overdue checking)

4. **Custom Pagination Logic**
   - Pro: Flexible, backward compatible
   - Con: Slightly more complex than global pagination

### Potential Improvements

1. **WebSocket for Real-time Updates**
   - Would allow live dashboard updates
   - Requires Django Channels setup
   - Useful for multi-user scenarios

2. **File Upload for Job Attachments**
   - Could integrate AWS S3 or similar
   - Useful for job documentation
   - Photos, PDFs, etc.

3. **Email/SMS Notifications**
   - Alert technicians of new assignments
   - Job status change notifications
   - Requires email/SMS service integration

4. **Advanced Analytics**
   - More detailed reporting
   - Charts and graphs
   - Technician performance metrics
   - Equipment utilization trends

5. **Mobile App Optimization**
   - Optimized endpoints for mobile
   - Reduced payload sizes
   - Offline support with sync

6. **Geographic Features**
   - Job location tracking
   - Route optimization
   - Geofencing for task completion

---

## 14. Why This Architecture?

### Alignment with Requirements
- ✅ All PDF requirements implemented
- ✅ Role-based access control working
- ✅ Job lifecycle management enforced
- ✅ Technician dashboard optimized
- ✅ Audit logging for compliance
- ✅ Optional background tasks
- ✅ Equipment flexibility (add/remove)

### Professional Standards
- Industry-standard tech stack (Django + DRF)
- RESTful API design
- Security best practices (JWT, permissions, validation)
- Clean code organization
- Comprehensive documentation

### Maintainability
- Clear separation of concerns
- Well-documented code and decisions
- Easy to extend and modify
- Test-friendly architecture
- Follows Django conventions

### Production Ready
- Scalable design (stateless auth)
- Performance optimized (indexes, query optimization)
- Security hardened (multi-layer validation)
- Deployment guides included
- Database migration path defined

---

## Conclusion

The JobOps system was designed with a focus on:
1. **Simplicity** - Easy to understand, setup, and maintain
2. **Security** - Role-based access, JWT authentication, multi-layer validation
3. **Scalability** - Stateless design, background jobs, optimized queries
4. **Professional Standards** - Industry best practices throughout
5. **Flexibility** - Easy to extend, optional features, customizable

All design decisions were made to balance:
- Project requirements (PDF specifications)
- Development time (rapid implementation)
- Maintainability (clean code, good docs)
- Production readiness (security, performance, scalability)

The architecture demonstrates professional software engineering practices while keeping the implementation pragmatic and focused on delivering value.

---

**Document Version:** 1.0  
**Last Updated:** October 18, 2025  
**Project:** JobOps - Internal Operations Management System

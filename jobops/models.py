from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_TECHNICIAN = 'technician'
    ROLE_SALES_AGENT = 'sales_agent'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_TECHNICIAN, 'Technician'),
        (ROLE_SALES_AGENT, 'Sales Agent'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_TECHNICIAN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['role']),
        ]

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_technician(self):
        return self.role == self.ROLE_TECHNICIAN

    @property
    def is_sales_agent(self):
        return self.role == self.ROLE_SALES_AGENT

class Equipment(models.Model):
    EQUIPMENT_TYPES = [
        ('tool', 'Tool'),
        ('vehicle', 'Vehicle'),
        ('machine', 'Machine'),
        ('device', 'Device'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=50, choices=EQUIPMENT_TYPES)
    serial_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Job(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    client_name = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_jobs')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_jobs', limit_choices_to={'role': User.ROLE_TECHNICIAN})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    scheduled_date = models.DateTimeField()
    overdue = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['overdue']),
            models.Index(fields=['assigned_to']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.client_name}"

    def clean(self):
        super().clean()
        if self.assigned_to and self.assigned_to.role != User.ROLE_TECHNICIAN:
            raise ValidationError("Assigned user must be a technician.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def can_be_completed(self):
        return self.job_tasks.filter(status__in=['pending', 'in_progress']).count() == 0

    def mark_completed(self):
        if self.can_be_completed:
            self.status = 'completed'
            self.save()
            return True
        return False

class JobTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    STEP_CHOICES = [
        ('inspection', 'Inspection'),
        ('installation', 'Installation'),
        ('testing', 'Testing'),
        ('configuration', 'Configuration'),
        ('training', 'Training'),
        ('maintenance', 'Maintenance'),
        ('repair', 'Repair'),
        ('other', 'Other'),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_tasks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    step = models.CharField(max_length=50, choices=STEP_CHOICES, default='other')
    order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    required_equipment = models.ManyToManyField(Equipment, related_name='assigned_tasks', blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['order']),
        ]
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.job.title} - {self.title}"

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def is_overdue(self):
        return self.job.scheduled_date < timezone.now() and not self.is_completed

    def mark_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        self.job.mark_completed()

class JobChangeHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('status_changed', 'Status Changed'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed'),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='change_history')
    task = models.ForeignKey(JobTask, on_delete=models.CASCADE, null=True, blank=True, related_name='change_history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['job']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.job.title} - {self.get_action_display()}"

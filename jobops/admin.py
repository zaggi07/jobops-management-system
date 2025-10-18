from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Equipment, Job, JobTask, JobChangeHistory

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('JobOps Fields', {'fields': ('role', 'created_at', 'updated_at')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('JobOps Fields', {'fields': ('role',)}),
    )
    list_display = ['username', 'email', 'role', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'serial_number', 'is_active', 'created_at']
    list_filter = ['type', 'is_active']
    search_fields = ['name', 'serial_number']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'client_name', 'status', 'priority', 'assigned_to', 'scheduled_date', 'overdue']
    list_filter = ['status', 'priority', 'overdue']
    search_fields = ['title', 'client_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['created_by', 'assigned_to']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by', 'assigned_to')

@admin.register(JobTask)
class JobTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'job', 'step', 'order', 'status', 'completed_at']
    list_filter = ['status', 'step']
    search_fields = ['title', 'description', 'job__title']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    raw_id_fields = ['job']
    filter_horizontal = ['required_equipment']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job')

@admin.register(JobChangeHistory)
class JobChangeHistoryAdmin(admin.ModelAdmin):
    list_display = ['job', 'action', 'changed_by', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['job__title']
    readonly_fields = ['timestamp']
    raw_id_fields = ['job', 'task', 'changed_by']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job', 'changed_by')

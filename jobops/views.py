from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict

from .models import User, Equipment, Job, JobTask, JobChangeHistory
from .serializers import (
    UserSerializer, EquipmentSerializer, JobSerializer,
    JobTaskSerializer, JobChangeHistorySerializer,
    TechnicianDashboardSerializer, JobAnalyticsSerializer
)
from .permissions import (
    IsAdminUser, IsAdminOrSalesAgent, IsTechnician,
    IsAssignedTechnician, IsJobOwnerOrAssigned
)
from .pagination import JobOpsPagination

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return User.objects.all()
        elif user.is_sales_agent:
            return User.objects.filter(role=User.ROLE_TECHNICIAN)
        return User.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = JobOpsPagination

    def get_queryset(self):
        queryset = Equipment.objects.all()
        is_active = self.request.query_params.get('is_active')
        equipment_type = self.request.query_params.get('type')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if equipment_type:
            queryset = queryset.filter(type=equipment_type)
        return queryset

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, IsJobOwnerOrAssigned]
    pagination_class = JobOpsPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Job.objects.select_related('created_by', 'assigned_to').prefetch_related('job_tasks')
        elif user.is_sales_agent:
            return Job.objects.filter(created_by=user).select_related('created_by', 'assigned_to').prefetch_related('job_tasks')
        elif user.is_technician:
            return Job.objects.filter(assigned_to=user).select_related('created_by', 'assigned_to').prefetch_related('job_tasks')
        return Job.objects.none()

    def get_permissions(self):
        if self.action == 'analytics':
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action in ['create']:
            permission_classes = [IsAuthenticated, IsAdminOrSalesAgent]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsJobOwnerOrAssigned]
        else:
            permission_classes = [IsAuthenticated, IsJobOwnerOrAssigned]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAssignedTechnician])
    def mark_completed(self, request, pk=None):
        job = self.get_object()
        if job.mark_completed():
            return Response({'message': 'Job marked as completed successfully.'})
        else:
            return Response({'error': 'Cannot complete job. All tasks must be completed first.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminUser])
    def analytics(self, request):
        jobs = Job.objects.all()
        total_jobs = jobs.count()
        completed_jobs = jobs.filter(status='completed').count()
        pending_jobs = jobs.filter(status__in=['pending', 'in_progress']).count()
        overdue_jobs = jobs.filter(overdue=True).count()
        completed_tasks = JobTask.objects.filter(status='completed', completed_at__isnull=False, created_at__isnull=False)
        avg_time = None
        if completed_tasks.exists():
            total_duration = timedelta()
            count = 0
            for task in completed_tasks:
                if task.completed_at and task.created_at:
                    total_duration += (task.completed_at - task.created_at)
                    count += 1
            if count > 0:
                avg_time = total_duration / count
        equipment_usage = Equipment.objects.annotate(usage_count=Count('assigned_tasks')).order_by('-usage_count')[:5]
        most_used_equipment = [{'id': eq.id, 'name': eq.name, 'type': eq.type, 'usage_count': eq.usage_count} for eq in equipment_usage]
        analytics_data = {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'pending_jobs': pending_jobs,
            'overdue_jobs': overdue_jobs,
            'average_task_time': avg_time,
            'most_used_equipment': most_used_equipment
        }
        serializer = JobAnalyticsSerializer(analytics_data)
        return Response(serializer.data)

class JobTaskViewSet(viewsets.ModelViewSet):
    queryset = JobTask.objects.all()
    serializer_class = JobTaskSerializer
    permission_classes = [IsAuthenticated, IsAssignedTechnician]

    def get_queryset(self):
        user = self.request.user
        job_id = self.kwargs.get('job_pk')
        if job_id:
            queryset = JobTask.objects.filter(job_id=job_id)
        else:
            queryset = JobTask.objects.all()
        if user.is_admin:
            return queryset.select_related('job').prefetch_related('required_equipment')
        elif user.is_technician:
            return queryset.filter(job__assigned_to=user).select_related('job').prefetch_related('required_equipment')
        return JobTask.objects.none()

    def perform_create(self, serializer):
        job_id = self.kwargs.get('job_pk')
        job = Job.objects.get(id=job_id)
        serializer.save(job=job)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAssignedTechnician])
    def mark_completed(self, request, pk=None, job_pk=None):
        task = self.get_object()
        task.mark_completed()
        return Response({'message': 'Task marked as completed successfully.'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAssignedTechnician], url_path='add-equipment')
    def add_equipment(self, request, pk=None, job_pk=None):
        task = self.get_object()
        equipment_ids = request.data.get('equipment_ids', [])
        if not equipment_ids:
            return Response({'error': 'equipment_ids required'}, status=status.HTTP_400_BAD_REQUEST)
        equipment = Equipment.objects.filter(id__in=equipment_ids, is_active=True)
        task.required_equipment.add(*equipment)
        return Response({'message': f'{equipment.count()} equipment(s) added successfully.'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAssignedTechnician], url_path='remove-equipment')
    def remove_equipment(self, request, pk=None, job_pk=None):
        task = self.get_object()
        equipment_ids = request.data.get('equipment_ids', [])
        if not equipment_ids:
            return Response({'error': 'equipment_ids required'}, status=status.HTTP_400_BAD_REQUEST)
        equipment = Equipment.objects.filter(id__in=equipment_ids)
        task.required_equipment.remove(*equipment)
        return Response({'message': f'{equipment.count()} equipment(s) removed successfully.'})

class TechnicianDashboardView(generics.ListAPIView):
    serializer_class = TechnicianDashboardSerializer
    permission_classes = [IsAuthenticated, IsTechnician]

    def get_queryset(self):
        user = self.request.user
        tasks = JobTask.objects.filter(
            job__assigned_to=user,
            status__in=['pending', 'in_progress']
        ).select_related('job').prefetch_related('required_equipment')
        tasks_by_date = defaultdict(list)
        for task in tasks:
            task_date = task.job.scheduled_date.date()
            tasks_by_date[task_date].append(task)
        dashboard_data = []
        for date, date_tasks in sorted(tasks_by_date.items()):
            serializer = JobTaskSerializer(date_tasks, many=True)
            dashboard_data.append({'date': date, 'tasks': serializer.data})
        return dashboard_data

class JobChangeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JobChangeHistory.objects.all()
    serializer_class = JobChangeHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        job_id = self.kwargs.get('job_pk')
        if job_id:
            return JobChangeHistory.objects.filter(job_id=job_id).select_related('job', 'changed_by')
        return JobChangeHistory.objects.select_related('job', 'changed_by').all()

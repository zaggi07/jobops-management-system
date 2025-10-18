from rest_framework import serializers
from .models import User, Equipment, Job, JobTask, JobChangeHistory

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'type', 'serial_number', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class JobTaskSerializer(serializers.ModelSerializer):
    required_equipment = EquipmentSerializer(many=True, read_only=True)
    equipment_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = JobTask
        fields = ['id', 'title', 'description', 'step', 'order', 'status', 'required_equipment', 'equipment_ids', 'completed_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'completed_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        equipment_ids = validated_data.pop('equipment_ids', [])
        task = JobTask.objects.create(**validated_data)
        if equipment_ids:
            equipment = Equipment.objects.filter(id__in=equipment_ids, is_active=True)
            task.required_equipment.set(equipment)
        return task

    def update(self, instance, validated_data):
        equipment_ids = validated_data.pop('equipment_ids', None)
        task = super().update(instance, validated_data)
        if equipment_ids is not None:
            equipment = Equipment.objects.filter(id__in=equipment_ids, is_active=True)
            task.required_equipment.set(equipment)
        return task

class JobSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True)
    job_tasks = JobTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'client_name', 'created_by', 'assigned_to', 'assigned_to_id', 'status', 'priority', 'scheduled_date', 'overdue', 'job_tasks', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate_assigned_to_id(self, value):
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        if user.role != User.ROLE_TECHNICIAN:
            raise serializers.ValidationError("Assigned user must be a technician.")
        return value

    def create(self, validated_data):
        assigned_to_id = validated_data.pop('assigned_to_id')
        assigned_to = User.objects.get(id=assigned_to_id)
        validated_data['assigned_to'] = assigned_to
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        if assigned_to_id:
            assigned_to = User.objects.get(id=assigned_to_id)
            validated_data['assigned_to'] = assigned_to
        return super().update(instance, validated_data)

class JobChangeHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)

    class Meta:
        model = JobChangeHistory
        fields = ['id', 'job', 'task', 'action', 'changed_by', 'old_value', 'new_value', 'timestamp']
        read_only_fields = ['id', 'changed_by', 'timestamp']

class TechnicianDashboardSerializer(serializers.Serializer):
    date = serializers.DateField()
    tasks = JobTaskSerializer(many=True)

class JobAnalyticsSerializer(serializers.Serializer):
    total_jobs = serializers.IntegerField()
    completed_jobs = serializers.IntegerField()
    pending_jobs = serializers.IntegerField()
    overdue_jobs = serializers.IntegerField()
    average_task_time = serializers.DurationField()
    most_used_equipment = serializers.ListField(child=serializers.DictField())

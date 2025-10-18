from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Job, JobTask, JobChangeHistory

_job_original_state = {}
_task_original_state = {}

@receiver(pre_save, sender=Job)
def store_job_original_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_job = Job.objects.get(pk=instance.pk)
            _job_original_state[instance.pk] = {
                'title': old_job.title,
                'status': old_job.status,
                'priority': old_job.priority,
                'assigned_to': old_job.assigned_to.id if old_job.assigned_to else None
            }
        except Job.DoesNotExist:
            pass

@receiver(post_save, sender=Job)
def log_job_changes(sender, instance, created, **kwargs):
    if created:
        action = 'created'
        old_value = None
        new_value = {
            'title': instance.title,
            'status': instance.status,
            'priority': instance.priority,
            'assigned_to': instance.assigned_to.id if instance.assigned_to else None
        }
    else:
        action = 'updated'
        old_value = _job_original_state.get(instance.pk, None)
        new_value = {
            'title': instance.title,
            'status': instance.status,
            'priority': instance.priority,
            'assigned_to': instance.assigned_to.id if instance.assigned_to else None
        }
        if instance.pk in _job_original_state:
            del _job_original_state[instance.pk]
    JobChangeHistory.objects.create(
        job=instance,
        action=action,
        changed_by=instance.created_by,
        old_value=old_value,
        new_value=new_value
    )

@receiver(pre_save, sender=JobTask)
def store_task_original_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_task = JobTask.objects.get(pk=instance.pk)
            _task_original_state[instance.pk] = {
                'title': old_task.title,
                'status': old_task.status,
                'step': old_task.step,
                'order': old_task.order
            }
        except JobTask.DoesNotExist:
            pass

@receiver(post_save, sender=JobTask)
def log_jobtask_changes(sender, instance, created, **kwargs):
    if created:
        action = 'created'
        old_value = None
        new_value = {
            'title': instance.title,
            'status': instance.status,
            'step': instance.step,
            'order': instance.order
        }
        if instance.job.status == 'completed':
            instance.job.status = 'pending'
            instance.job.save(update_fields=['status'])
    else:
        action = 'updated'
        old_value = _task_original_state.get(instance.pk, None)
        new_value = {
            'title': instance.title,
            'status': instance.status,
            'step': instance.step,
            'order': instance.order
        }
        if instance.pk in _task_original_state:
            del _task_original_state[instance.pk]
    JobChangeHistory.objects.create(
        job=instance.job,
        task=instance,
        action=action,
        changed_by=instance.job.created_by,
        old_value=old_value,
        new_value=new_value
    )

@receiver(pre_save, sender=Job)
def check_job_completion(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_job = Job.objects.get(pk=instance.pk)
            if old_job.status != 'completed' and instance.status == 'completed':
                if not instance.can_be_completed:
                    from django.core.exceptions import ValidationError
                    raise ValidationError("Cannot complete job. All tasks must be completed first.")
        except Job.DoesNotExist:
            pass

@receiver(pre_save, sender=JobTask)
def check_task_completion(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_task = JobTask.objects.get(pk=instance.pk)
            if old_task.status != 'completed' and instance.status == 'completed':
                JobChangeHistory.objects.create(
                    job=instance.job,
                    task=instance,
                    action='completed',
                    changed_by=instance.job.assigned_to,
                    old_value={'status': old_task.status},
                    new_value={'status': instance.status}
                )
        except JobTask.DoesNotExist:
            pass

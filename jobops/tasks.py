from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Job, JobChangeHistory

@shared_task
def check_overdue_jobs():
    current_time = timezone.now()
    jobs_overdue = Job.objects.filter(
        scheduled_date__lt=current_time,
        status__in=['pending', 'in_progress']
    )
    updated_count = 0
    for job in jobs_overdue:
        if not job.overdue:
            job.overdue = True
            job.save(update_fields=['overdue'])
            updated_count += 1
    jobs_not_overdue = Job.objects.filter(overdue=True).exclude(id__in=jobs_overdue.values_list('id', flat=True))
    reset_count = 0
    for job in jobs_not_overdue:
        job.overdue = False
        job.save(update_fields=['overdue'])
        reset_count += 1
    return {
        'message': f'Overdue check completed. Updated {updated_count} jobs as overdue, reset {reset_count} jobs.',
        'updated_count': updated_count,
        'reset_count': reset_count
    }

@shared_task
def cleanup_old_change_history():
    cutoff_date = timezone.now() - timedelta(days=180)
    deleted_count, _ = JobChangeHistory.objects.filter(timestamp__lt=cutoff_date).delete()
    return {
        'message': f'Cleaned up {deleted_count} old change history records.',
        'deleted_count': deleted_count
    }

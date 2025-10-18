from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserViewSet, EquipmentViewSet, JobViewSet,
    JobTaskViewSet, TechnicianDashboardView, JobChangeHistoryViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'equipment', EquipmentViewSet)
router.register(r'jobs', JobViewSet)

jobs_router = routers.NestedSimpleRouter(router, r'jobs', lookup='job')
jobs_router.register(r'tasks', JobTaskViewSet, basename='job-tasks')
jobs_router.register(r'history', JobChangeHistoryViewSet, basename='job-history')

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/', include(jobs_router.urls)),
    path('api/technician-dashboard/', TechnicianDashboardView.as_view(), name='technician-dashboard'),
]

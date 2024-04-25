from django.urls import path
from . import views

urlpatterns = [
    path('', views.add_platform, name='add-platform'),
    path('update-platform/<int:p_id>', views.update_platform, name='update-platform'),
    path('delete-platform/<int:p_id>', views.delete_platform, name='delete-platform'),
]

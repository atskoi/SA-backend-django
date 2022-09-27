from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from rest_framework_swagger.views import get_swagger_view
from core import *
import pac.views as views
from django.contrib import admin
import pac.notification_view.notification as notification

admin.autodiscover()
SCHEMA_VIEW = get_swagger_view(title='PAC Management API')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('pac.pre_costing.urls')),
    url(r'^api/', include('pac.rrf.urls')),
    url(r'^api/', include('core.urls')),
    url(r'^schema/$', SCHEMA_VIEW),
    path("accounts/", include('rest_framework.urls')),

    path(
        'api/metadata/',
        views.get_metadata_pyodbc,
        name='metadata'
    ),

    # NOTIFICATIONS
    path(
        'api/notification/',
        notification.NotificationAPI.as_view(http_method_names=['get', 'put']),
        name='notification-fetch-update'
    ), 

    path('api/rrf/<str:rrf_id>/comments/',
         views.comment_handler,
         name='comments'),
    path('api/rrf/<str:rrf_id>/comments/<str:comment_id>/',
         views.comment_handler,
         name='comments-id'),
    path('api/rrf/<str:rrf_id>/comments/<str:comment_id>/file/<str:file_name>',
         views.comment_file_handler,
         name='comment-file'),
    path('api/rrf/<str:rrf_id>/cost-override/',
         views.add_cost_override,
         name='cost-override'),

    path('api/account/<str:external_erp_id>',
         views.account_handler,
         name='account_handler'),

    path('api/account/',
         views.account_handler,
         name='account_handler'),

    # TODO remove before production
    path('api/sl/migrate',
         views.service_service_migration,
         name='service_service_migration')
]

urlpatterns += staticfiles_urlpatterns()

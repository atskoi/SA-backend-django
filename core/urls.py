from django.conf import settings
from django.conf.urls import include, url
from django.urls import path
from rest_framework import routers

import core.views as views
import core.users.user_view as user_views
import core.default as default

router = routers.DefaultRouter()

urlpatterns = [
    path('user-admin/',
        user_views.UserAPI.as_view(),
        name='user-list'
    ),
    path('user-admin/header/',
        user_views.UserHeaderView.as_view(),
        name='user-header'
    )
]
urlpatterns += router.urls

if settings.DEVELOP:
     urlpatterns += [path('ping/',
        default.BackendPing.as_view(http_method_names=['get']),
        name='backend-ping-check'
     )]
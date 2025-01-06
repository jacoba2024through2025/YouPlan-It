"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static





urlpatterns = [
    path("", views.viewHomePage, name="home"),
    path("register/", views.viewRegistrationPage, name="register"),
    path("login/", views.viewLoginPage, name="login"),
    path("logout/", views.viewLogout, name="logout"),
    path("dashboard/<str:username>/", views.viewUserDashboard, name="user_dashboard"),
    path("profile/<str:username>/", views.viewUserProfile, name="profile"),
    path("dashboard/<str:username>/events/", views.EventPage, name="event_page"),
    path("dashboard/<str:username>/shared/", views.SharedEventPage, name="shared_events"),
    path("dashboard/<str:username>/events/create/", views.EventCreateView.as_view(), name="event_create"),
    path("dashboard/<str:username>/events/update/<str:ename>/", views.EventUpdateView.as_view(), name="event_update"),
    path("dashboard/<str:username>/events/<str:ename>/", views.EventDetail, name="event_detail"),
    path("dashboard/<str:username>/events/<str:ename>/delete/", views.deleteEvent, name="event_delete"),
    path("dashboard/<str:username>/invite/", views.InviteUser, name="invites"),
    path("dashboard/<str:username>/chat/", views.create_chat_room, name="create_chat_room"),  # Event selection for chat
    path("dashboard/<str:username>/chat/<int:event_id>/", views.chat_room, name="chats"),  # Chat room for specific event
    path("accept-invite/<str:username>/<str:ename>/", views.acceptInvite, name="accept"),
    path("decline-invite/<str:username>/<str:ename>/", views.declineInvite, name="decline"),
    
    path('event/<str:username>/<str:ename>/remove_member/', views.remove_member, name='remove_member'),
    path("admin/", admin.site.urls),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



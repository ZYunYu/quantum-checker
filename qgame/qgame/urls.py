from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from game.views import (
    GameLevelView, StartGameView, ApplyGateView,
    login_view, logout_view, session_view, signup_view, health_view, classrooms_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz/', health_view),
    path('api/gamelevels/', GameLevelView.as_view(), name='game-levels'),
    path('api/gamelevels/<int:level_id>/', GameLevelView.as_view(), name='game-level-detail'),
    path('api/gamelevels/<int:level_id>/session/', StartGameView.as_view()),
    path('api/applygate/<int:session_id>/', ApplyGateView.as_view()),
    path('api/login/', login_view),
    path('api/logout/', logout_view),
    path('api/session/', session_view),
    path('api/signup/', signup_view),
    path('api/classrooms/', classrooms_view),
    re_path(r'^(?!api/|admin/|static/|healthz/).*$', TemplateView.as_view(template_name='index.html')),
]

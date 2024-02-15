"""
URL configuration for qgame project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.template.defaulttags import url
from django.urls import include, path
from django.views.generic import TemplateView
from game.views import GameLevelView
from game.views import index


urlpatterns = [
    # path("test/", include("game.urls")),
    path('admin/', admin.site.urls),
    path('api/gamelevels/', GameLevelView.as_view(), name='game-levels'),
    path('api/gamelevels/<int:level_id>/', GameLevelView.as_view(), name='game-level-detail'),
    path('test/', TemplateView.as_view(template_name='game/index.html')),

]

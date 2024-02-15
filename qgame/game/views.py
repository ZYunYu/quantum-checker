from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializer import *


class GameLevelView(APIView):
    def get(self, request, level_id=None):
        if level_id is not None:
            try:
                level = GameLevel.objects.get(level=level_id)
                serializer = GameLevelSerializer(level)
                return Response(serializer.data)
            except GameLevel.DoesNotExist:
                return Response({'error': 'Game Level not found'}, status=404)
        else:
            levels = GameLevel.objects.all()
            serializer = GameLevelSerializer(levels, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = GameLevelSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


def index(request):
    return render(request, 'index.html')

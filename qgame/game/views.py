from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import *
from .models.game_session_model import GameSession
from .models.game_level_model import GameLevel
from .game_logic import QuantumGame
from django.contrib.auth import authenticate, login, logout
import json
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from rest_framework.permissions import IsAuthenticated


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


class GameSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id=None):
        session = get_object_or_404(GameSession, id=session_id, user=request.user)
        serializer = GameSessionSerializer(session)
        return Response(serializer.data)

    def post(self, request):
        level_id = request.data.get('level_id')
        game_level = get_object_or_404(GameLevel, level=level_id)
        session, created = GameSession.objects.update_or_create(
            user=request.user, game_level=game_level,
            defaults=request.data
        )
        return Response({"message": "Session created" if created else "Session updated", "session_id": session.id})

# class ApplyGateView(APIView):
#     def post(self, request, session_id):
#         gate_type = request.data.get('gate_type')
#         qubit_idx = request.data.get('qubit_idx')
#
#         try:
#             game_session = GameSession.objects.get(id=session_id)
#         except GameSession.DoesNotExist:
#             return Response({'error': 'Game session not found'}, status=404)
#
#         quantum_game = QuantumGame(initialize=game_session.applied_gates)
#         quantum_game.apply_gate(qubit_idx=qubit_idx, gate=gate_type)
#         quantum_game.run_circuit()
#
#         game_session.applied_gates = quantum_game.applied_gates
#         game_session.probabilities = quantum_game.probabilities
#         game_session.save()
#
#         front_end_data = {
#             'circle11': quantum_game.probabilities.get('ZI', 0),
#             'circle12': quantum_game.probabilities.get('XI', 0),
#             'circle23': quantum_game.probabilities.get('IX', 0),
#             'circle33': quantum_game.probabilities.get('IZ', 0),
#             'circle31': quantum_game.probabilities.get('ZZ', 0),
#             'circle21': quantum_game.probabilities.get('ZX', 0),
#             'circle22': quantum_game.probabilities.get('XX', 0),
#             'circle32': quantum_game.probabilities.get('XZ', 0),
#         }
#
#         serializer = GameSessionSerializer(game_session)
#         return Response(serializer.data)


@require_POST
def login_view(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({'detail': 'Login successful',
                             'userId': user.id})
    else:
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Invalid password'}, status=400)
        else:
            return JsonResponse({'error': 'User does not exist, please sign up'}, status=400)

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return JsonResponse({'message': 'Logout successful'})
    else:
        return JsonResponse({'error': 'You are not logged in'}, status=400)

@ensure_csrf_cookie
def session_view(request):
    if request.user.is_authenticated:
        return JsonResponse({"isauthenticated": True, "userId": request.user.id})
    else:
        return JsonResponse({"isauthenticated": False})


@require_POST
def signup_view(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')

    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already exists'}, status=400)

    User.objects.create_user(username=username, email=email, password=password)
    return JsonResponse({'detail': 'User created successfully'}, status=201)


def index(request):
    return render(request, 'index.html')

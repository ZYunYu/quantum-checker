import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .game_logic import CIRCLE_PAULIS, QuantumGame, SUPPORTED_GATES
from .models.game_level_model import GameLevel
from .models.game_session_model import GameSession
from .serializer import GameLevelSerializer


def level_snapshot(level):
    return {
        'initial_gates': level.initial_gates, 'allowed_gates': level.allowed_gates,
        'targets': {field: getattr(level, field) for field in CIRCLE_PAULIS},
        'win_conditions': level.win_conditions,
    }


def update_session(session, level, operations):
    game = QuantumGame(level.initial_gates + operations)
    session.applied_gates = operations
    session.probabilities = game.run_circuit()
    session.is_win = game.check_win(level)
    session.current_state = level_snapshot(level)
    session.save()
    return {'id': session.id, 'circles': session.probabilities, 'moves': len(operations), 'is_win': session.is_win}


class GameLevelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, level_id=None):
        if level_id is not None:
            return Response(GameLevelSerializer(get_object_or_404(GameLevel, level=level_id)).data)
        return Response(GameLevelSerializer(GameLevel.objects.all(), many=True).data)

    def post(self, request, level_id=None):
        if not request.user.has_perm('game.add_gamelevel'):
            return Response({'error': 'Only a level administrator can create levels.'}, status=403)
        if level_id is not None:
            return Response({'error': 'Edit levels in /admin/.'}, status=405)
        serializer = GameLevelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class StartGameView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, level_id):
        if 'reset' in request.data and type(request.data['reset']) is not bool:
            return Response({'error': 'reset must be a boolean.'}, status=400)
        with transaction.atomic():
            level = get_object_or_404(GameLevel, level=level_id)
            session, created = GameSession.objects.get_or_create(user=request.user, game_level=level)
            session = GameSession.objects.select_for_update().get(pk=session.pk)
            reset = created or request.data.get('reset') or session.current_state != level_snapshot(level)
            return Response(update_session(session, level, [] if reset else session.applied_gates))


class GateInputSerializer(serializers.Serializer):
    gate_type = serializers.ChoiceField(choices=SUPPORTED_GATES)
    qubit_idx = serializers.ChoiceField(choices=(0, 1), required=False)

    def validate(self, data):
        if data['gate_type'] != 'cz' and 'qubit_idx' not in data:
            raise serializers.ValidationError('Select a qubit for X, Z or H.')
        return data


class ApplyGateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        serializer = GateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            session = get_object_or_404(
                GameSession.objects.select_for_update().select_related('game_level'),
                pk=session_id, user=request.user,
            )
            level = session.game_level
            if session.current_state != level_snapshot(level):
                return Response({'error': 'This level was edited. Reload it to start the updated puzzle.'}, status=409)
            if serializer.validated_data['gate_type'] not in level.allowed_gates:
                return Response({'error': 'This gate is not allowed in this level.'}, status=400)
            if len(session.applied_gates) >= 256 - len(level.initial_gates):
                return Response({'error': 'Move limit reached. Reset the puzzle to continue.'}, status=400)
            operation = {'gate': serializer.validated_data['gate_type']}
            if operation['gate'] != 'cz':
                operation['qubit_idx'] = int(serializer.validated_data['qubit_idx'])
            return Response(update_session(session, level, session.applied_gates + [operation]))


def read_json(request):
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        raise ValueError('Invalid JSON.')
    if not isinstance(data, dict):
        raise ValueError('Send a JSON object.')
    return data


@require_POST
def login_view(request):
    try:
        data = read_json(request)
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    if not isinstance(data.get('username'), str) or not isinstance(data.get('password'), str):
        return JsonResponse({'error': 'Username and password are required.'}, status=400)
    user = authenticate(request, username=data['username'], password=data['password'])
    if user is None:
        return JsonResponse({'error': 'Invalid username or password.'}, status=400)
    login(request, user)
    return JsonResponse({'detail': 'Login successful', 'userId': user.id, 'isStaff': user.is_staff, 'csrfToken': get_token(request)})


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Logout successful'})


@never_cache
@ensure_csrf_cookie
def session_view(request):
    return JsonResponse({
        'isauthenticated': request.user.is_authenticated,
        'userId': request.user.id if request.user.is_authenticated else None,
        'isStaff': request.user.is_staff if request.user.is_authenticated else False,
        'csrfToken': get_token(request),
    })


@require_POST
def signup_view(request):
    try:
        data = read_json(request)
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    username, password, email = data.get('username'), data.get('password'), data.get('email', '')
    if not isinstance(username, str) or not username.strip() or len(username) > 150:
        return JsonResponse({'error': 'A username of at most 150 characters is required.'}, status=400)
    if not isinstance(password, str) or not isinstance(email, str):
        return JsonResponse({'error': 'Invalid password or email.'}, status=400)
    user = User(username=username.strip(), email=email)
    try:
        user.full_clean(exclude=['password'])
        validate_password(password, user=user)
    except ValidationError as exc:
        return JsonResponse({'error': ' '.join(exc.messages)}, status=400)
    try:
        User.objects.create_user(username=user.username, email=email, password=password)
    except IntegrityError:
        return JsonResponse({'error': 'Username already exists.'}, status=400)
    return JsonResponse({'detail': 'User created successfully'}, status=201)


def health_view(request):
    return JsonResponse({'status': 'ok'})

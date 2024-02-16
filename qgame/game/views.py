from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import *
from rest_framework import status
from .models.game_session_model import GameSession
from .models.game_level_model import GameLevel
from .game_logic import QuantumGame


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


class ApplyGateView(APIView):
    def post(self, request, session_id):
        gate_type = request.data.get('gate_type')
        qubit_idx = request.data.get('qubit_idx')

        try:
            game_session = GameSession.objects.get(id=session_id)
        except GameSession.DoesNotExist:
            return Response({'error': 'Game session not found'}, status=404)

        # 初始化QuantumGame实例，并应用门操作
        quantum_game = QuantumGame(initialize=game_session.applied_gates)
        quantum_game.apply_gate(qubit_idx=qubit_idx, gate=gate_type)
        quantum_game.run_circuit()

        # 更新GameSession实例
        game_session.applied_gates = quantum_game.applied_gates
        game_session.probabilities = quantum_game.probabilities
        game_session.save()

        # 映射概率到前端元素
        front_end_data = {
            'circle11': quantum_game.probabilities.get('ZI', 0),
            'circle12': quantum_game.probabilities.get('XI', 0),
            'circle23': quantum_game.probabilities.get('IX', 0),
            'circle33': quantum_game.probabilities.get('IZ', 0),
            'circle31': quantum_game.probabilities.get('ZZ', 0),
            'circle21': quantum_game.probabilities.get('ZX', 0),
            'circle22': quantum_game.probabilities.get('XX', 0),
            'circle32': quantum_game.probabilities.get('XZ', 0),
        }

        serializer = GameSessionSerializer(game_session)
        return Response(serializer.data)

class CreateGameSessionView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = GameSessionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def index(request):
    return render(request, 'index.html')

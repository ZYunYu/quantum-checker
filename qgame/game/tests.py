import json
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase, Client, SimpleTestCase, override_settings

from .game_logic import QuantumGame
from .models import GameLevel


class QuantumRulesTests(SimpleTestCase):
    def test_zero_state_and_local_x(self):
        game = QuantumGame()
        circles = game.run_circuit()
        self.assertEqual(circles['circle11'], 1)
        self.assertEqual(circles['circle33'], 1)
        self.assertEqual(circles['circle12'], 0.5)
        game.apply_gate(0, 'x')
        circles = game.run_circuit()
        self.assertEqual(circles['circle11'], 0)
        self.assertEqual(circles['circle33'], 1)
        self.assertEqual(circles['circle31'], 0)

    def test_h_z_and_inverse_gates(self):
        for gate in ('x', 'z', 'h', 'cz'):
            game = QuantumGame([{'gate': 'h', 'qubit_idx': 0}, {'gate': 'h', 'qubit_idx': 1}])
            initial = game.run_circuit()
            game.apply_gate(0, gate)
            game.apply_gate(0, gate)
            self.assertEqual(game.run_circuit(), initial)
        game = QuantumGame([{'gate': 'h', 'qubit_idx': 0}, {'gate': 'z', 'qubit_idx': 0}])
        self.assertEqual(game.run_circuit()['circle12'], 0)

    def test_bell_correlations_are_exact(self):
        game = QuantumGame([
            {'gate': 'h', 'qubit_idx': 0}, {'gate': 'h', 'qubit_idx': 1},
            {'gate': 'cz'}, {'gate': 'h', 'qubit_idx': 1},
        ])
        circles = game.run_circuit()
        for field in ('circle11', 'circle12', 'circle23', 'circle33'):
            self.assertEqual(circles[field], 0.5)
        self.assertEqual(circles['circle31'], 1)
        self.assertEqual(circles['circle22'], 1)
        self.assertEqual(circles['circle21'], 0.5)
        self.assertEqual(circles['circle32'], 0.5)


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class LevelAndSessionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('player', password='A-secure-test-password-98')
        self.client.force_login(self.user)

    def test_all_demo_levels_are_valid_and_solvable(self):
        self.assertEqual(GameLevel.objects.count(), 4)
        for level in GameLevel.objects.all():
            level.full_clean()

    def test_impossible_targets_are_rejected(self):
        level = GameLevel(level=20, circle11=1, circle12=1, gate_h=True, gate_x=True)
        with self.assertRaises(ValidationError):
            level.full_clean()

    def test_bad_initial_gates_and_conditions_are_rejected(self):
        for data in (
            {'initial_gates': [{'gate': 'h', 'qubit_idx': 2}]},
            {'win_conditions': {'IZ': 1}},
            {'win_conditions': [{'row': 1, 'column': 3, 'exact': 1}]},
            {'win_conditions': [{'row': 1, 'column': 1, 'min': 1, 'max': 0}]},
        ):
            level = GameLevel(level=20, circle11=1, **data)
            with self.assertRaises(ValidationError):
                level.full_clean()

    def test_players_cannot_create_levels(self):
        response = self.client.post('/api/gamelevels/', {'level': 10}, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(GameLevel.objects.filter(level=10).exists())

    def test_session_resume_solve_reset_and_gate_rules(self):
        response = self.client.post('/api/gamelevels/1/session/', {}, content_type='application/json')
        session = response.json()
        self.assertFalse(session['is_win'])
        response = self.client.post(f"/api/applygate/{session['id']}/", {'gate_type': 'h', 'qubit_idx': 0}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = self.client.post(f"/api/applygate/{session['id']}/", {'gate_type': 'x'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = self.client.post(f"/api/applygate/{session['id']}/", {'gate_type': 'x', 'qubit_idx': 0}, content_type='application/json')
        self.assertTrue(response.json()['is_win'])
        self.assertEqual(response.json()['circles']['circle11'], 0)
        resumed = self.client.post('/api/gamelevels/1/session/', {}, content_type='application/json').json()
        self.assertEqual(resumed['moves'], 1)
        reset = self.client.post('/api/gamelevels/1/session/', {'reset': True}, content_type='application/json').json()
        self.assertEqual(reset['moves'], 0)
        self.assertFalse(reset['is_win'])

    def test_other_player_cannot_change_session(self):
        session = self.client.post('/api/gamelevels/1/session/', {}, content_type='application/json').json()
        other = User.objects.create_user('other')
        self.client.force_login(other)
        response = self.client.post(f"/api/applygate/{session['id']}/", {'gate_type': 'x', 'qubit_idx': 0}, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_edited_level_invalidates_old_session(self):
        session = self.client.post('/api/gamelevels/1/session/', {}, content_type='application/json').json()
        level = GameLevel.objects.get(level=1)
        level.circle11 = None
        level.save()
        response = self.client.post(f"/api/applygate/{session['id']}/", {'gate_type': 'x', 'qubit_idx': 0}, content_type='application/json')
        self.assertEqual(response.status_code, 409)
        refreshed = self.client.post('/api/gamelevels/1/session/', {}, content_type='application/json')
        self.assertEqual(refreshed.status_code, 200)

    def test_admin_form_edits_level_and_api_reflects_changes(self):
        admin_user = User.objects.create_superuser('owner', password='A-secure-test-password-98')
        self.client.force_login(admin_user)
        level = GameLevel.objects.get(level=3)
        values = {field.name: getattr(level, field.name) for field in level._meta.fields if field.name != 'id'}
        values['initial_gates'] = 'h:0'
        values['win_conditions'] = json.dumps(values['win_conditions'])
        values['title'] = 'Edited in admin'
        response = self.client.post(f'/admin/game/gamelevel/{level.pk}/change/', values)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get('/api/gamelevels/3/').json()['title'], 'Edited in admin')
        self.assertEqual(GameLevel.objects.get(pk=level.pk).initial_gates, [{'gate': 'h', 'qubit_idx': 0}])

    def test_level_editor_has_only_required_permissions(self):
        call_command('bootstrap_admin', verbosity=0)
        editor = User.objects.create_user('editor', is_staff=True)
        editor.groups.add(Group.objects.get(name='Level editors'))
        self.assertTrue(editor.has_perm('game.change_gamelevel'))
        self.assertFalse(editor.has_perm('auth.change_user'))
        self.client.force_login(editor)
        level = GameLevel.objects.first()
        self.assertEqual(self.client.get(f'/admin/game/gamelevel/{level.pk}/change/').status_code, 200)
        self.assertEqual(self.client.get('/admin/auth/user/').status_code, 403)


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        User.objects.create_user('player', password='A-secure-test-password-98')

    def test_login_requires_csrf_and_refresh_preserves_session(self):
        credentials = {'username': 'player', 'password': 'A-secure-test-password-98'}
        self.assertEqual(self.client.post('/api/login/', credentials, content_type='application/json').status_code, 403)
        csrf = self.client.get('/api/session/').json()['csrfToken']
        response = self.client.post('/api/login/', credentials, content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(response.status_code, 200)
        session = self.client.get('/api/session/').json()
        self.assertTrue(session['isauthenticated'])
        self.assertEqual(self.client.get('/api/gamelevels/').status_code, 200)
        csrf = session['csrfToken']
        response = self.client.post('/api/gamelevels/1/session/', {}, content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.post('/api/gamelevels/1/session/', {}, content_type='application/json').status_code, 403)
        self.assertEqual(self.client.get('/api/logout/').status_code, 405)
        self.client.post('/api/logout/', {}, content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertFalse(self.client.get('/api/session/').json()['isauthenticated'])

    def test_signup_validates_password_and_never_grants_staff(self):
        csrf = self.client.get('/api/session/').json()['csrfToken']
        data = {'username': 'new-player', 'password': '123', 'is_staff': True}
        response = self.client.post('/api/signup/', data, content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(response.status_code, 400)
        data['password'] = 'A-secure-test-password-98'
        response = self.client.post('/api/signup/', data, content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(response.status_code, 201)
        self.assertFalse(User.objects.get(username='new-player').is_staff)

    def test_bad_login_input_and_anonymous_api_access(self):
        csrf = self.client.get('/api/session/').json()['csrfToken']
        self.assertEqual(self.client.post('/api/login/', '[]', content_type='application/json', HTTP_X_CSRFTOKEN=csrf).status_code, 400)
        self.assertEqual(self.client.get('/api/gamelevels/').status_code, 403)
        self.assertEqual(self.client.get('/healthz/').json(), {'status': 'ok'})

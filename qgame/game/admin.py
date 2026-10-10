from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .game_logic import CIRCLE_PAULIS, validate_gates
from .models.game_level_model import GameLevel
from .models.game_session_model import GameSession
from .models.user_model import UserGameLevel, Classroom, UserProfile


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class StudentProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    max_num = 1
    extra = 0


admin.site.unregister(User)


@admin.register(User)
class StudentUserAdmin(UserAdmin):
    inlines = (StudentProfileInline,)
    list_display = UserAdmin.list_display + ('student_id', 'classroom')
    list_filter = UserAdmin.list_filter + ('student_profile__classroom',)
    search_fields = UserAdmin.search_fields + ('student_profile__student_id',)
    list_select_related = ('student_profile', 'student_profile__classroom')

    def get_inline_instances(self, request, obj=None):
        return super().get_inline_instances(request, obj) if obj else []

    @admin.display(description='Student ID')
    def student_id(self, obj):
        profile = getattr(obj, 'student_profile', None)
        return profile.student_id if profile else None

    @admin.display(description='Classroom')
    def classroom(self, obj):
        profile = getattr(obj, 'student_profile', None)
        return profile.classroom if profile else None


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'classroom')
    list_filter = ('classroom',)
    search_fields = ('student_id', 'user__username')
    readonly_fields = ('user',)
    list_select_related = ('user', 'classroom')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class GateSequenceField(forms.Field):
    widget = forms.Textarea(attrs={'rows': 3, 'cols': 60})

    def prepare_value(self, value):
        if isinstance(value, list):
            return ', '.join('cz' if item['gate'] == 'cz' else f"{item['gate']}:{item['qubit_idx']}" for item in value)
        return value

    def to_python(self, value):
        operations = []
        for token in (value or '').lower().replace('\n', ',').split(','):
            token = token.strip()
            if not token:
                continue
            if token == 'cz':
                operations.append({'gate': 'cz'})
                continue
            parts = token.split(':')
            if len(parts) != 2 or parts[1] not in ('0', '1'):
                raise forms.ValidationError('Example: h:0, x:1, cz. Use 0 for the left qubit and 1 for the right qubit.')
            operations.append({'gate': parts[0], 'qubit_idx': int(parts[1])})
        try:
            validate_gates(operations)
        except ValueError as exc:
            raise forms.ValidationError(str(exc))
        return operations


class GameLevelForm(forms.ModelForm):
    initial_gates = GateSequenceField(
        required=False, label='Initial state',
        help_text='Operations run from |00〉. Leave blank to start at |00〉. Example: h:0, x:1, cz.',
    )

    class Meta:
        model = GameLevel
        fields = '__all__'
        widgets = {'instructions': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in CIRCLE_PAULIS:
            self.fields[field].help_text = 'Target: 1 = black, 0 = white, 0.5 = outline. Leave blank to accept any value.'
            self.fields[field].widget.attrs.update({'step': '0.5', 'min': '0', 'max': '1'})


@admin.register(GameLevel)
class GameLevelAdmin(admin.ModelAdmin):
    form = GameLevelForm
    list_display = ('level', 'title', 'display_gates')
    search_fields = ('title', 'instructions')
    fieldsets = (
        ('Level information', {'fields': ('level', 'title', 'instructions')}),
        ('Initial state and allowed gates', {'fields': ('initial_gates', ('gate_x', 'gate_z', 'gate_h', 'gate_cz'))}),
        ('Target circles', {'fields': (
            ('circle11', 'circle12'), ('circle23', 'circle33'),
            ('circle31', 'circle21', 'circle22', 'circle32'),
        ), 'description': 'Players must match the target. Saving checks that it is reachable with the allowed gates.'}),
        ('Advanced win conditions (optional)', {'fields': ('win_conditions',), 'classes': ('collapse',),
         'description': 'Usually leave this as []. Range example: [{"row":1,"column":1,"min":0.8,"max":1}]'}),
    )

    @admin.display(description='Allowed gates')
    def display_gates(self, obj):
        return ', '.join(gate.upper() for gate in obj.allowed_gates)


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'game_level', 'is_win')
    list_filter = ('is_win', 'game_level')
    readonly_fields = ('user', 'game_level', 'current_state', 'applied_gates', 'probabilities', 'is_win')

    def has_add_permission(self, request):
        return False


admin.site.register(UserGameLevel)
admin.site.site_header = 'Quantum Checkers Admin'
admin.site.site_title = 'Quantum Checkers'
admin.site.index_template = 'game/admin_index.html'

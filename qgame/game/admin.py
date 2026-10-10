from django import forms
from django.contrib import admin

from .game_logic import CIRCLE_PAULIS, validate_gates
from .models.game_level_model import GameLevel
from .models.game_session_model import GameSession
from .models.user_model import UserGameLevel


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
                raise forms.ValidationError('格式示例：h:0, x:1, cz。0 为左量子比特，1 为右量子比特。')
            operations.append({'gate': parts[0], 'qubit_idx': int(parts[1])})
        try:
            validate_gates(operations)
        except ValueError as exc:
            raise forms.ValidationError(str(exc))
        return operations


class GameLevelForm(forms.ModelForm):
    initial_gates = GateSequenceField(
        required=False, label='初始状态',
        help_text='从 |00〉开始执行。留空表示 |00〉；例如 h:0, x:1, cz。',
    )

    class Meta:
        model = GameLevel
        fields = '__all__'
        widgets = {'instructions': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in CIRCLE_PAULIS:
            self.fields[field].help_text = '目标：1 黑色，0 白色，0.5 空心。留空表示不要求匹配。'
            self.fields[field].widget.attrs.update({'step': '0.5', 'min': '0', 'max': '1'})


@admin.register(GameLevel)
class GameLevelAdmin(admin.ModelAdmin):
    form = GameLevelForm
    list_display = ('level', 'title', 'display_gates')
    search_fields = ('title', 'instructions')
    fieldsets = (
        ('关卡信息', {'fields': ('level', 'title', 'instructions')}),
        ('初始状态和允许使用的门', {'fields': ('initial_gates', ('gate_x', 'gate_z', 'gate_h', 'gate_cz'))}),
        ('目标圆点', {'fields': (
            ('circle11', 'circle12'), ('circle23', 'circle33'),
            ('circle31', 'circle21', 'circle22', 'circle32'),
        ), 'description': '保存时自动检查目标是否可达。玩家必须让当前棋盘匹配目标。'}),
        ('高级过关条件（可选）', {'fields': ('win_conditions',), 'classes': ('collapse',),
         'description': '通常保留 []。范围示例：[{"row":1,"column":1,"min":0.8,"max":1}]'}),
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

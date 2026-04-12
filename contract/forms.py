from django import forms
from django.core.exceptions import ValidationError
from .models import Departament, FixedAsset, Counterparty

class DepartamentFrom(forms.ModelForm):
    """Форма создания и редактирования подразделения"""
    class Meta:
        model = Departament
        fields = ['name','code']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Отдел информационных технологий'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: IT-01'
            }),
        }

        labels = {
            'name': 'Название подразделения',
            'code': 'Код подразделения',
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code and ' 'in code:
            raise ValidationError('Код подразделения не должен содержать пробелов')
        return code.upper() if code else code
    
class FixedAssetForm(forms.ModelForm):
    """Форма создания и редактирования основных средств"""
    class Meta:
        model = FixedAsset
        fields = ['name', 'Departament', 'internal_code']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Системный блок Dell OptiPlex'
            }),
            'Departament': forms.Select(attrs={
                'class': 'form-control',
                'id': 'Departament-select'  
            }),
            'internal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'internal-code-field', 
                'placeholder': 'Будет сгенерирован автоматически или введите вручную'
            }),
        }
        labels = {
            'name': 'Наименование основного средства',
            'Departament': 'Подразделение (место хранения)',
            'internal_code': 'Код внутреннего учета',
        }

    def clean_internal_code(self):
        '''Проверка уникальности'''
        internal_code = self.cleaned_data.get('internal_code')
        if internal_code:
            existing = FixedAsset.objects.exclude(
                pk=self.instance.pk if self.instance.pk else None
            ).filter(internal_code=internal_code)
            if existing.exists():
                raise ValidationError(
                    f'Код "{internal_code}" уже используется. '
                    f'Пожалуйста, используйте другой код или нажмите "Назначить внутренний код"'
                )
        return internal_code

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['Departament'].queryset = Departament.objects.all().order_by('code')
        self.fields['internal_code'].required = False


class CounterpartyForm(forms.ModelForm):
    '''Форма создания и редактирования контрагентов'''
    class Meta:
        model = Counterparty
        fields = ['name', 'inn']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: ООО "Ромашка"'
            }),
            'inn': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'inn-field', 
                'placeholder': '10 или 12 цифр',
                'maxlength': '12'
            }),
        }
        labels = {
            'name': 'Наименование контрагента',
            'inn': 'ИНН',
        }
    
    def clean_inn(self):
        '''Проверка ИНН'''
        inn = self.cleaned_data.get('inn').strip()
        if not inn or inn.strip()=='':
            raise ValidationError(
                'ИНН не может быть пустым. Заполните ИНН контрагента.'
            )
        if not inn.isdigit():
            raise ValidationError('ИНН должен содержать только цифры')
        
        return inn
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or name.strip() == '':
            raise ValidationError('Наименование контрагента не может быть пустым')
        return name.strip()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inn'].required = True


class DuplicateCheckForm(forms.Form):
    '''Форма для ручного ввода ИНН при проверкае дупликата'''
    inn  = forms.CharField(
        max_length=12,
        required=True,
        label='ИНН для проверки',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ИНН',
            'id': 'check-inn-field'
        }),
    )

    def clean_inn(self):
        inn = self.cleaned_data.get('inn').strip()
        if not inn or inn == '':
            raise ValidationError('Введите ИНН для проверки')
        if not inn.isdgit():
            raise ValidationError('ИНН должен содержать только цифры')
        return inn

class BullDeleteForm(forms.Form):
    '''Форма для массовой пометки контрагентов'''
    counterparty_ids = forms.ModelMultipleChoiceField(
        queryset=Counterparty.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'bulk-checkbox'}),
        required=False,
        label='Выберите контрагентов для пометки на удаление'
    )

    confirm = forms.BooleanField(
        required=True,
        label='Подтверждаю пометку на удаление выбранных контрагентов',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_counterparty_ids(self):
        counterparties = self.cleaned_data.get('counterparty_ids')
        if not counterparties:
            raise ValidationError('Выберите хотя бы одного контрагента')
        return counterparties


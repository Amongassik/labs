from django import forms
import datetime


class SubreportForm(forms.Form):
    date = forms.DateField(
        label="Дата отчета",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'date-input'}),
        initial=datetime.date.today
    )
    department = forms.CharField(
        label="Отдел",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Все отделы', 'class': 'dept-input'})
    )
    hide_zero_debt = forms.BooleanField(
        label="Скрыть нулевую задолженность",
        required=False,
        initial=True
    )
    sort_by = forms.ChoiceField(
        label="Сортировать по",
        choices=[
            ('debt_desc', 'Долгу (по убыванию)'),
            ('debt_asc', 'Долгу (по возрастанию)'),
            ('name', 'ФИО'),
        ],
        required=False,
        initial='debt_desc'
    )
    show_only_debtors = forms.BooleanField(
        label="Только должники",
        required=False,
        initial=False
    )
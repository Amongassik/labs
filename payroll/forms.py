from django import forms
from .models import EmployeeSalary

class EmployeeSalaryForm(forms.ModelForm):
    class Meta:
        model = EmployeeSalary
        fields = ['name', 'department', 'position', 'accrued_amount', 'accrual_date']
        labels = {
            'name': 'ФИО сотрудника',
            'department': 'Подразделение',
            'position': 'Должность',
            'accrued_amount': 'Начислено (руб.)',
            'accrual_date': 'Дата начисления',
        }
        widgets = {
            'accrual_date': forms.DateInput(attrs={'type': 'date'}),
        }
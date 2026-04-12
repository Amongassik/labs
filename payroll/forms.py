from django import forms
from .models import EmployeeSalary

class EmployeeSalaryForm(forms.ModelForm):
    class Meta:
        model = EmployeeSalary
        fields = '__all__'
        labels = {
            'employee_name': 'ФИО сотрудника',
            'accrued_amount': 'Начислено (руб.)',
        }

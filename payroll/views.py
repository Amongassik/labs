from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.db.models import Sum
from .models import EmployeeSalary
from .forms import EmployeeSalaryForm
from itertools import groupby

def employee_list(request: HttpRequest):
    employees = EmployeeSalary.objects.all()
    content = {
        'employees': employees,
        'title': 'Список сотрудников'
    }
    return render(request, 'payroll/index.html', content)

def employee_add(request: HttpRequest):
    if request.method == 'POST':
        form = EmployeeSalaryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = EmployeeSalaryForm()
    content = {
        'form': form,
        'title': 'Добавление сотрудника'
    }
    return render(request, 'payroll/add.html', content)

def employee_delete(request: HttpRequest, pk):
    employee = get_object_or_404(EmployeeSalary, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('index')
    content = {
        'employee': employee,
        'title': 'Удаление сотрудника'
    }
    return render(request, 'payroll/delete.html', content)

def print_salary_report(request: HttpRequest):
    # Группировка по подразделениям
    employees = EmployeeSalary.objects.all().order_by('department', 'name')
    
    # Создаем группы для отчета
    grouped_employees = []
    for department, group in groupby(employees, key=lambda x: x.department):
        dept_employees = list(group)
        dept_total = sum(e.accrued_amount for e in dept_employees)
        grouped_employees.append({
            'department': department,
            'employees': dept_employees,
            'dept_total': dept_total
        })
    
    total_sum = sum(e.accrued_amount for e in employees)
    total_employees = employees.count()
    
    content = {
        'grouped_employees': grouped_employees,
        'total_sum': total_sum,
        'total_employees': total_employees,
        'title': 'Отчет по всем сотрудникам',
        'high_threshold': 100000,
        'low_threshold': 30000,
        'multiple_of': 5000,
    }
    return render(request, 'payroll/print_report.html', content)
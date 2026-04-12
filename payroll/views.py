from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpRequest
from .models import EmployeeSalary
from .forms import EmployeeSalaryForm

# Create your views here.
def employee_list(request:HttpRequest):
    employees = EmployeeSalary.objects.all()
    content = {
        'employees':employees,
        'title':'писок сотрудников'
    }
    return render(request,'payroll/index.html',content)

def employee_add(request:HttpRequest):
    if request.method == 'POST':
        form = EmployeeSalaryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form =EmployeeSalaryForm()
    content ={
        'form':form,
        'title':'Добавление сотрудника'
    }
    return render(request,'payroll/add.html',content)

def employee_delete(request:HttpRequest,pk):
    employee = get_object_or_404(EmployeeSalary,pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('index')
    content = {
        'employee':employee,
        'title':'Удаление сотрудника'
    }
    return render(request,'payroll/delete.html',content)

def print_salary_report(request:HttpRequest):
    employees = EmployeeSalary.objects.all()
    total_sum = sum(e.accrued_amount for e in employees)
    content = {
        'employees': employees,
        'total_sum': total_sum,
        'title': 'Печатная форма',
        'high_threshold': 100000,
        'low_threshold': 30000,
        'multiple_of': 5000,
    }
    return render(request,'payroll/print_report.html',content)


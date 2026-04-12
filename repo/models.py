from django.db import models

class Employee(models.Model):
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    patronymic = models.CharField(max_length=50, blank=True, verbose_name="Отчество")
    position = models.CharField(max_length=100, verbose_name="Должность")
    department = models.CharField(max_length=100, blank=True, verbose_name="Отдел")

    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}".strip()
    
    def __str__(self):
        return self.full_name()

class CashAdvance(models.Model):
    date = models.DateField(verbose_name="Дата выдачи")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    basis = models.TextField(verbose_name="Основание", blank=True)

    class Meta:
        ordering = ['-date']

class AdvanceReport(models.Model):
    date = models.DateField(verbose_name="Дата отчета")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    expense_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма расхода")
    return_date = models.DateField(null=True, blank=True, verbose_name="Дата возврата")
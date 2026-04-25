from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class EmployeeSalary(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Сотрудник'
    )
    department = models.CharField(
        max_length=100,
        verbose_name='Подразделение',
        default='Основное'
    )
    position = models.CharField(
        max_length=100,
        verbose_name='Должность',
        default='Сотрудник'
    )
    accrued_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0, message='Сумма не может быть отрицательной'),
            MaxValueValidator(1000000, message='Сумма не может превышать 1 000 000')
        ],
        verbose_name='Начислено',
    )
    accrual_date = models.DateField(
        verbose_name='Дата начисления'
    )

    class Meta:
        verbose_name = 'Начисление зарплаты'
        verbose_name_plural = 'Начисления зарплаты'
        ordering = ['department', 'name']
        db_table = 'employee_salary'

    def __str__(self):
        return f"{self.name} ({self.department}) - {self.accrued_amount} руб."
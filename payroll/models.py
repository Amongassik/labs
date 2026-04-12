from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class EmployeeSalary(models.Model):
    name = models.CharField(max_length=200,verbose_name='Сотрудник')
    accrued_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0, message='Сумма не может быть отрицательной'),
            MaxValueValidator(1000000, message='Сумма не может превышать 1 000 000')
        ],
        verbose_name='Начислено',
    )
    accrual_date = models.DateField(auto_now_add=True,verbose_name='Дата начисления')

    class Meta:
        verbose_name = 'Начисление зарплаты'
        verbose_name_plural = 'Начисления зарплаты'
        ordering = ['-accrual_date', 'name']
        db_table = 'employee_salary'

    def __str__(self):
        return f"{self.name} - {self.accrued_amount} руб."
    
    def get_formatted_amount(self):
        return f"{self.accrued_amount:,.2f}".replace(',', ' ')
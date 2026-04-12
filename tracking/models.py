from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

class Employee(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    
    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Car(models.Model):
    brand = models.CharField(max_length=100, verbose_name='Марка')
    license_plate = models.CharField(max_length=20, unique=True, verbose_name='Гос.Номер')
    year = models.IntegerField(verbose_name='Год выпуска')
    fuel_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Расход топлива (л/км)')

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        ordering = ['brand']

    def __str__(self):
        return f"{self.brand} ({self.license_plate})"
    
    def clean(self):
        current_year = date.today().year
        if self.year and (self.year < 1950 or self.year > current_year):
            raise ValidationError({
                'year': f'Год выпуска должен быть между 1950 и {current_year}'
            })
        if self.fuel_rate and self.fuel_rate <= 0:
            raise ValidationError({
                'fuel_rate': 'Норма расхода топлива должна быть больше 0'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Driver(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name='Сотрудник',
    )
    cars = models.ManyToManyField(
        Car,
        verbose_name='Автомобиль',
        blank=True
    )

    class Meta:
        verbose_name = "Водитель"
        verbose_name_plural = "Водители"
        ordering = ['employee__last_name']
    
    def __str__(self):
        return f"{self.employee.last_name} {self.employee.first_name}"

    def get_total_mileage(self):
        """Суммарный пробег водителя по всем путевым листам"""
        waybills = self.waybill_set.all()
        total = 0
        for waybill in waybills:
            total += (waybill.end_mileage - waybill.start_mileage)
        return total
    
    def get_total_mileage_for_period(self, start_date=None, end_date=None):
        """Суммарный пробег за период"""
        waybills = self.waybill_set.all()
        if start_date:
            waybills = waybills.filter(date__gte=start_date)
        if end_date:
            waybills = waybills.filter(date__lte=end_date)
        
        total = 0
        for waybill in waybills:
            total += (waybill.end_mileage - waybill.start_mileage)
        return total


class Waybill(models.Model):
    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        verbose_name='Водитель'
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        verbose_name='Автомобиль'
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name='Дата документа'
    )
    departure_time = models.DateTimeField(verbose_name='Время выезда')
    return_time = models.DateTimeField(verbose_name='Время заезда')
    start_mileage = models.PositiveIntegerField(verbose_name='Начальный километраж')
    end_mileage = models.PositiveIntegerField(verbose_name='Конечный километраж')

    class Meta:
        verbose_name = "Путевой лист"
        verbose_name_plural = "Путевые листы"
        ordering = ['-date', '-departure_time']
        unique_together = ['driver', 'date', 'departure_time']
    
    def __str__(self):
        return f"Путевой лист №{self.id} - {self.driver} от {self.date}"
    
    @property
    def mileage(self):
        if self.end_mileage and self.start_mileage:
            return self.end_mileage - self.start_mileage
        return 0
    
    @property
    def fuel_consumption(self):
        if self.mileage and self.car and self.car.fuel_rate:
            return self.mileage * float(self.car.fuel_rate)
        return 0

    def clean(self):
        errors = {}
        
        if self.departure_time and self.return_time:
            if self.return_time <= self.departure_time:
                errors['return_time'] = 'Время заезда должно быть позже времени выезда'
        if self.start_mileage is not None and self.end_mileage is not None:
            if self.end_mileage <= self.start_mileage:
                errors['end_mileage'] = 'Конечный километраж должен быть больше начального'        
        if self.driver and self.car:
            if self.car not in self.driver.cars.all():
                errors['car'] = f'Автомобиль {self.car} не закреплен за водителем {self.driver}'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
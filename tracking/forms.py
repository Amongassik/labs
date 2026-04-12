from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Employee,Car,Driver,Waybill

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['last_name','first_name']
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите фамилию'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'}),
        }
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
        }
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].required = True

class  CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['brand', 'license_plate', 'year', 'fuel_rate']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Марка машины'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: А123ВС77'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Год выпуска'}),
            'fuel_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например: 0.12', 'step': '0.01'}),
        }
        labels = {
            'brand': 'Марка',
            'license_plate': 'Гос. номер',
            'year': 'Год выпуска',
            'fuel_rate': 'Норма расхода (л/км)',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = True

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['employee', 'cars']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'cars': forms.SelectMultiple(attrs={'class': 'form-control', 'size': 5}),
        }
        labels = {
            'employee': 'Сотрудник',
            'cars': 'Автомобили',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].required = True
        self.fields['cars'].help_text = 'Удерживайте Ctrl для выбора нескольких автомобилей'
        self.fields['cars'].queryset = Car.objects.all()

class WayBillForm(forms.ModelForm):
    class Meta:
        model = Waybill
        fields = ['driver', 'car', 'date', 'departure_time', 'return_time', 'start_mileage', 'end_mileage']
        widgets = {
            'driver': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_driver',
                'onchange': 'filterCars()'
            }),
            'car': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_car'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'departure_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'return_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'start_mileage': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_start_mileage',
                'oninput': 'calculateMileageAndFuel()'
            }),
            'end_mileage': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_end_mileage',
                'oninput': 'calculateMileageAndFuel()'
            }),
        }
        labels = {
            'driver': 'Водитель',
            'car': 'Автомобиль',
            'date': 'Дата документа',
            'departure_time': 'Время выезда',
            'return_time': 'Время заезда',
            'start_mileage': 'Начальный километраж',
            'end_mileage': 'Конечный километраж',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['car'].queryset = Car.objects.none()
        
        if 'driver' in self.data:
            try:
                driver_id = int(self.data.get('driver'))
                self.fields['car'].queryset = Driver.objects.get(id=driver_id).cars.all()
            except (ValueError, TypeError, Driver.DoesNotExist):
                pass
        elif self.instance.pk and self.instance.driver:
            self.fields['car'].queryset = self.instance.driver.cars.all()
        
        for field in self.fields:
            self.fields[field].required = True
        
        if not self.instance.pk and not self.data:
            self.fields['date'].initial = timezone.now().date()
    
    def clean(self):
        cleaned_data = super().clean()
        departure_time = cleaned_data.get('departure_time')
        return_time = cleaned_data.get('return_time')
        start_mileage = cleaned_data.get('start_mileage')
        end_mileage = cleaned_data.get('end_mileage')
        driver = cleaned_data.get('driver')
        car = cleaned_data.get('car')
        
        if departure_time and return_time:
            if return_time <= departure_time:
                raise ValidationError({
                    'return_time': 'Время заезда должно быть позже времени выезда'
                })
        
        if start_mileage is not None and end_mileage is not None:
            if end_mileage <= start_mileage:
                raise ValidationError({
                    'end_mileage': 'Конечный километраж должен быть больше начального'
                })
        
        if driver and car:
            if car not in driver.cars.all():
                raise ValidationError({
                    'car': f'Автомобиль {car.brand} ({car.license_plate}) не закреплен за водителем {driver}'
                })
        
        return cleaned_data

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        label='Дата с',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        label='Дата по',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    driver = forms.ModelChoiceField(
        queryset=Driver.objects.all(),
        required=False,
        label='Водитель',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise ValidationError('Дата начала не может быть позже даты окончания')
        return cleaned_data
    
class ReportFilterForm(forms.Form):
    """Универсальная форма для фильтрации отчётов по периоду"""
    start_date = forms.DateField(
        required=False,
        label='Начало периода',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        label='Конец периода',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            today = timezone.now().date()
            self.fields['start_date'].initial = today.replace(day=1)
            self.fields['end_date'].initial = today
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise ValidationError('Дата начала не может быть позже даты окончания')
        return cleaned_data

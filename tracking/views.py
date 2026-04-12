from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib import messages
from django.db.models import Sum, F, Avg
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Employee, Car, Driver, Waybill
from .forms import EmployeeForm, CarForm, DriverForm, WayBillForm, DateRangeForm, ReportFilterForm
from .utils import CarStats


# ==================== ГЛАВНАЯ СТРАНИЦА ====================

class HomeView(TemplateView):
    """Главная страница с дашбордом"""
    template_name = 'tracking/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['total_cars'] = Car.objects.count()
        context['total_drivers'] = Driver.objects.count()
        context['total_employees'] = Employee.objects.count()
        context['total_waybills'] = Waybill.objects.count()
        context['recent_waybills'] = Waybill.objects.all().select_related('driver__employee', 'car')[:5]
        
        # Исправлено: вычисляем пробег за сегодня в цикле
        today = timezone.now().date()
        today_waybills = Waybill.objects.filter(date=today)
        today_mileage = 0
        for waybill in today_waybills:
            today_mileage += (waybill.end_mileage - waybill.start_mileage)
        context['today_mileage'] = today_mileage
        
        return context


# ==================== СОТРУДНИКИ (EMPLOYEE) ====================

class EmployeeListView(ListView):
    model = Employee
    template_name = 'tracking/employee_list.html'
    context_object_name = 'employees'
    ordering = ['last_name', 'first_name']


class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'tracking/employee_form.html'
    success_url = reverse_lazy('tracking:employee_list_tr')
    
    def form_valid(self, form):
        messages.success(self.request, 'Сотрудник успешно добавлен')
        return super().form_valid(form)


class EmployeeUpdateView(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'tracking/employee_form.html'
    success_url = reverse_lazy('tracking:employee_list_tr')
    
    def form_valid(self, form):
        messages.success(self.request, 'Сотрудник успешно обновлен')
        return super().form_valid(form)


class EmployeeDeleteView(DeleteView):
    model = Employee
    template_name = 'tracking/employee_confirm_delete.html'
    success_url = reverse_lazy('tracking:employee_list_tr')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Сотрудник успешно удален')
        return super().delete(request, *args, **kwargs)


# ==================== АВТОМОБИЛИ (CAR) ====================

class CarListView(ListView):
    model = Car
    template_name = 'tracking/car_list.html'
    context_object_name = 'cars'
    ordering = ['brand']


class CarCreateView(CreateView):
    model = Car
    form_class = CarForm
    template_name = 'tracking/car_form.html'
    success_url = reverse_lazy('tracking:car_list_tr')
    
    def form_valid(self, form):
        messages.success(self.request, 'Автомобиль успешно добавлен')
        return super().form_valid(form)


class CarUpdateView(UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'tracking/car_form.html'
    success_url = reverse_lazy('tracking:car_list_tr')
    
    def form_valid(self, form):
        messages.success(self.request, 'Автомобиль успешно обновлен')
        return super().form_valid(form)


class CarDeleteView(DeleteView):
    model = Car
    template_name = 'tracking/car_confirm_delete.html'
    success_url = reverse_lazy('tracking:car_list_tr')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Автомобиль успешно удален')
        return super().delete(request, *args, **kwargs)


# ==================== ВОДИТЕЛИ (DRIVER) ====================

class DriverListView(ListView):
    model = Driver
    template_name = 'tracking/driver_list.html'
    context_object_name = 'drivers'
    
    def get_queryset(self):
        return Driver.objects.all().select_related('employee').prefetch_related('cars')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for driver in context['drivers']:
            driver.total_mileage = driver.get_total_mileage()
        return context


class DriverCreateView(CreateView):
    model = Driver
    form_class = DriverForm
    template_name = 'tracking/driver_form.html'
    success_url = reverse_lazy('tracking:driver_list_tr')
    
    def form_valid(self, form):
        messages.success(self.request, 'Водитель успешно добавлен')
        return super().form_valid(form)


class DriverUpdateView(UpdateView):
    model = Driver
    form_class = DriverForm
    template_name = 'tracking/driver_form.html'
    success_url = reverse_lazy('tracking:driver_list_tr')
    
    def form_valid(self, form):
        messages.success(self.request, 'Водитель успешно обновлен')
        return super().form_valid(form)


class DriverDeleteView(DeleteView):
    model = Driver
    template_name = 'tracking/driver_confirm_delete.html'
    success_url = reverse_lazy('tracking:driver_list_tr')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Водитель успешно удален')
        return super().delete(request, *args, **kwargs)


# ==================== ПУТЕВЫЕ ЛИСТЫ (WAYBILL) ====================

class WaybillListView(ListView):
    model = Waybill
    template_name = 'tracking/waybill_list.html'
    context_object_name = 'waybills'
    ordering = ['-date', '-departure_time']
    
    def get_queryset(self):
        return super().get_queryset().select_related('driver__employee', 'car')


class WaybillCreateView(CreateView):
    model = Waybill
    form_class = WayBillForm
    template_name = 'tracking/waybill_form.html'
    success_url = reverse_lazy('tracking:waybill_list_tr')
    
    def form_valid(self, form):
        messages.success(self.request, 'Путевой лист успешно создан')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание путевого листа'
        return context


class WaybillUpdateView(UpdateView):
    model = Waybill
    form_class = WayBillForm
    template_name = 'tracking/waybill_form.html'
    success_url = reverse_lazy('tracking:waybill_list_tr')
    
    def form_valid(self, form):
        messages.success(self.request, 'Путевой лист успешно обновлен')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование путевого листа'
        return context


class WaybillDeleteView(DeleteView):
    model = Waybill
    template_name = 'tracking/waybill_confirm_delete.html'
    success_url = reverse_lazy('tracking:waybill_list_tr')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Путевой лист успешно удален')
        return super().delete(request, *args, **kwargs)


class WaybillDetailView(DetailView):
    model = Waybill
    template_name = 'tracking/waybill_detail.html'
    context_object_name = 'waybill'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        waybill = context['waybill']
        context['mileage'] = waybill.mileage
        context['fuel_consumption'] = waybill.fuel_consumption
        return context


# ==================== ОТЧЁТЫ ====================

class DriverMileageReportView(TemplateView):
    template_name = 'tracking/report_driver_mileage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        form = ReportFilterForm(self.request.GET or None)
        context['form'] = form
        
        drivers = Driver.objects.all().select_related('employee')
        driver_data = []
        
        for driver in drivers:
            if form.is_valid():
                start_date = form.cleaned_data.get('start_date')
                end_date = form.cleaned_data.get('end_date')
                total_mileage = driver.get_total_mileage_for_period(start_date, end_date)
            else:
                total_mileage = driver.get_total_mileage()
            
            driver_data.append({
                'driver': driver,
                'total_mileage': total_mileage,
            })
        
        driver_data.sort(key=lambda x: x['total_mileage'], reverse=True)
        
        context['driver_data'] = driver_data
        context['total_mileage_all'] = sum(d['total_mileage'] for d in driver_data)
        
        return context


class CarFuelReportView(TemplateView):
    template_name = 'tracking/report_car_fuel.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        form = ReportFilterForm(self.request.GET or None)
        context['form'] = form
        
        cars = Car.objects.all()
        car_data = []
        
        for car in cars:
            if form.is_valid():
                start_date = form.cleaned_data.get('start_date')
                end_date = form.cleaned_data.get('end_date')
                total_fuel = CarStats.get_total_fuel_for_car_period(car, start_date, end_date)
            else:
                total_fuel = CarStats.get_total_fuel_for_car(car)
            
            car_data.append({
                'car': car,
                'total_fuel': total_fuel,
            })
        
        car_data.sort(key=lambda x: x['total_fuel'], reverse=True)
        
        context['car_data'] = car_data
        context['total_fuel_all'] = sum(d['total_fuel'] for d in car_data)
        
        return context


class WaybillJournalView(TemplateView):
    template_name = 'tracking/waybill_journal.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        form = DateRangeForm(self.request.GET or None)
        context['form'] = form
        
        waybills = Waybill.objects.all().select_related('driver__employee', 'car')
        
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            driver = form.cleaned_data.get('driver')
            
            if start_date:
                waybills = waybills.filter(date__gte=start_date)
            if end_date:
                waybills = waybills.filter(date__lte=end_date)
            if driver:
                waybills = waybills.filter(driver=driver)
        
        # Исправлено: вычисляем общий пробег в цикле
        total_mileage = 0
        for waybill in waybills:
            total_mileage += (waybill.end_mileage - waybill.start_mileage)
        
        context['waybills'] = waybills
        context['total_count'] = waybills.count()
        context['total_mileage'] = total_mileage
        
        return context


# ==================== ДИАГРАММЫ ====================

class DriverChartView(TemplateView):
    template_name = 'tracking/driver_chart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        drivers = Driver.objects.all().select_related('employee')
        driver_names = []
        driver_mileages = []
        
        for driver in drivers:
            total_mileage = driver.get_total_mileage()
            driver_names.append(str(driver))
            driver_mileages.append(float(total_mileage))
        
        avg_mileage = sum(driver_mileages) / len(driver_mileages) if driver_mileages else 0
        
        context['driver_names'] = driver_names
        context['driver_mileages'] = driver_mileages
        context['avg_mileage'] = avg_mileage
        
        return context


class CarChartView(TemplateView):
    template_name = 'tracking/car_chart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        cars = Car.objects.all()
        car_names = []
        car_fuel = []
        
        for car in cars:
            total_fuel = CarStats.get_total_fuel_for_car(car)
            car_names.append(str(car))
            car_fuel.append(float(total_fuel))
        
        avg_fuel = sum(car_fuel) / len(car_fuel) if car_fuel else 0
        
        context['car_names'] = car_names
        context['car_fuel'] = car_fuel
        context['avg_fuel'] = avg_fuel
        
        return context


# ==================== AJAX ENDPOINTS ====================

def get_driver_cars(request):
    """AJAX: возвращает список автомобилей для выбранного водителя"""
    driver_id = request.GET.get('driver_id')
    
    if not driver_id:
        return JsonResponse({'cars': []})
    
    try:
        driver = Driver.objects.get(id=driver_id)
        cars = driver.cars.all()
        cars_data = [
            {
                'id': car.id,
                'name': f"{car.brand} ({car.license_plate})",
                'fuel_rate': float(car.fuel_rate)
            }
            for car in cars
        ]
        return JsonResponse({'cars': cars_data})
    except Driver.DoesNotExist:
        return JsonResponse({'cars': [], 'error': 'Водитель не найден'})
from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    # Главная
    path('', views.HomeView.as_view(), name='home_tr'),
    
    # Сотрудники
    path('employees/', views.EmployeeListView.as_view(), name='employee_list_tr'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create_tr'),
    path('employees/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee_update_tr'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete_tr'),
    
    # Автомобили
    path('cars/', views.CarListView.as_view(), name='car_list_tr'),
    path('cars/create/', views.CarCreateView.as_view(), name='car_create_tr'),
    path('cars/<int:pk>/update/', views.CarUpdateView.as_view(), name='car_update_tr'),
    path('cars/<int:pk>/delete/', views.CarDeleteView.as_view(), name='car_delete_tr'),
    
    # Водители
    path('drivers/', views.DriverListView.as_view(), name='driver_list_tr'),
    path('drivers/create/', views.DriverCreateView.as_view(), name='driver_create_tr'),
    path('drivers/<int:pk>/update/', views.DriverUpdateView.as_view(), name='driver_update_tr'),
    path('drivers/<int:pk>/delete/', views.DriverDeleteView.as_view(), name='driver_delete_tr'),
    
    # Путевые листы (ВАЖНО: все маршруты для Waybill)
    path('waybills/', views.WaybillListView.as_view(), name='waybill_list_tr'),
    path('waybills/create/', views.WaybillCreateView.as_view(), name='waybill_create_tr'),
    path('waybills/<int:pk>/update/', views.WaybillUpdateView.as_view(), name='waybill_update_tr'),
    path('waybills/<int:pk>/delete/', views.WaybillDeleteView.as_view(), name='waybill_delete_tr'),
    path('waybills/<int:pk>/', views.WaybillDetailView.as_view(), name='waybill_detail_tr'),
    
    # Отчёты
    path('reports/driver-mileage/', views.DriverMileageReportView.as_view(), name='report_driver_mileage_tr'),
    path('reports/car-fuel/', views.CarFuelReportView.as_view(), name='report_car_fuel_tr'),
    path('reports/waybill-journal/', views.WaybillJournalView.as_view(), name='waybill_journal_tr'),
    
    # Диаграммы
    path('charts/drivers/', views.DriverChartView.as_view(), name='driver_chart_tr'),
    path('charts/cars/', views.CarChartView.as_view(), name='car_chart_tr'),
    
    # AJAX
    path('api/get_driver_cars/', views.get_driver_cars, name='get_driver_cars_tr'),
]
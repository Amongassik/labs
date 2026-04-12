from django.urls import path
from . import views

app_name = 'contract'

urlpatterns = [
    path('',views.index,name='index'),
    #Управление подразделениями
    path('departments/', views.departament_list, name='departament_list'),
    path('departments/create/', views.departament_create, name='departament_create'),
    path('departments/<int:pk>/edit/', views.departament_edit, name='departament_edit'),
    path('departments/<int:pk>/delete/', views.departament_delete, name='departament_delete'),
    #управление основными средствами
    path('assets/', views.fixed_asset_list, name='fixed_asset_list'),
    path('assets/create/', views.fixed_asset_create, name='fixed_asset_create'),
    path('assets/<int:pk>/edit/', views.fixed_asset_edit, name='fixed_asset_edit'),
    path('assets/<int:pk>/delete/', views.fixed_asset_delete, name='fixed_asset_delete'),
    #AJAX
    path('api/generate-code/', views.generate_internal_code, name='generate_internal_code'),
    path('api/check-inn/', views.check_inn, name='check_inn'),
    #Управление контрагентами
    path('counterparties/', views.counterparty_list, name='counterparty_list'),
    path('counterparties/create/', views.counterparty_create, name='counterparty_create'),
    path('counterparties/<int:pk>/edit/', views.counterparty_edit, name='counterparty_edit'),
    path('counterparties/<int:pk>/delete/', views.counterparty_delete, name='counterparty_delete'),
    path('counterparties/<int:pk>/restore/', views.counterparty_restore, name='counterparty_restore'),
    #Проверка дубликатов
    path('duplicates/', views.duplicate_groups, name='duplicate_groups'),
    path('check-inn-form/', views.check_duplicate_form, name='check_duplicate_form'),
    #Журнал изменений
    path('changelog/', views.changelog_list, name='changelog_list'),
]
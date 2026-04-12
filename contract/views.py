from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, JsonResponse, Http404
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import Departament, FixedAsset, Counterparty, ChangeLog
from .forms import (
    DepartamentFrom, FixedAssetForm, CounterpartyForm, 
    DuplicateCheckForm, BullDeleteForm
)
import json


# Create your views here.
def index(request: HttpRequest):
    context = {
        'title': 'Создание ИС'
    }
    return render(request, 'contract/index.html', context)


# ============================================================
# УПРАВЛЕНИЕ ПОДРАЗДЕЛЕНИЯМИ
# ============================================================

def departament_list(request: HttpRequest):
    departaments = Departament.objects.all().order_by('code')
    paginator = Paginator(departaments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'departaments': page_obj.object_list,
        'title': 'Список подразделений'
    }
    return render(request, 'contract/departament_list.html', context)


def departament_create(request: HttpRequest):
    if request.method == 'POST':
        form = DepartamentFrom(request.POST)
        if form.is_valid():
            departament = form.save()
            ChangeLog.objects.create(
                entity_type='Departament',
                entity_id=str(departament.pk),
                action='CREATE',
                description=f'Создано подразделение: {departament.name} (код: {departament.code})',
                changed_by=request.user.username if request.user.is_authenticated else 'admin'
            )
            messages.success(request, f'Подразделение "{departament.name}" успешно создано!')
            return redirect('contract:departament_list')
    else:
        form = DepartamentFrom()
    context = {
        'form': form,
        'title': 'Добавление подразделения'
    }
    return render(request, 'contract/Departament_form.html', context)


def departament_edit(request: HttpRequest, pk):
    try:
        departament = get_object_or_404(Departament, pk=pk)
    except Http404:
        messages.error(request, f'Подразделение с ID={pk} не найдено!')
        return redirect('contract:departament_list')
    
    if request.method == 'POST':
        form = DepartamentFrom(request.POST, instance=departament)
        if form.is_valid():
            form.save()
            ChangeLog.objects.create(
                entity_type='Departament',
                entity_id=str(departament.pk),
                action='UPDATE',
                description=f'Обновлено подразделение: {departament.name}',
                changed_by=request.user.username if request.user.is_authenticated else 'admin'
            )
            messages.success(request, f'Подразделение "{departament.name}" успешно обновлено!')
            return redirect('contract:departament_list')
    else:
        form = DepartamentFrom(instance=departament)
    context = {
        'form': form,
        'departament': departament,
        'title': 'Редактирование подразделения'
    }
    return render(request, 'contract/Departament_form.html', context)


def departament_delete(request: HttpRequest, pk):
    try:
        departament = get_object_or_404(Departament, pk=pk)
    except Http404:
        messages.error(request, f'Подразделение с ID={pk} не найдено! Возможно, оно уже было удалено.')
        return redirect('contract:departament_list')
    
    if request.method == 'POST':
        departament_name = departament.name
        departament.delete()
        ChangeLog.objects.create(
            entity_type='Departament',
            entity_id=str(pk),
            action='DELETE',
            description=f'Удалено подразделение: {departament_name}',
            changed_by=request.user.username if request.user.is_authenticated else 'admin'
        )
        messages.success(request, f'Подразделение "{departament_name}" успешно удалено!')
        return redirect('contract:departament_list')
    
    context = {
        'departament': departament,
        'title': 'Удаление подразделения'
    }
    return render(request, 'contract/Departament_confirm_delete.html', context)


# ============================================================
# УПРАВЛЕНИЕ ОСНОВНЫМИ СРЕДСТВАМИ
# ============================================================

def fixed_asset_list(request: HttpRequest):
    assets = FixedAsset.objects.select_related('Departament').all().order_by('Departament__code', 'internal_code')
    departament_id = request.GET.get('departament')
    if departament_id:
        assets = assets.filter(Departament_id=departament_id)
    paginator = Paginator(assets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departaments = Departament.objects.all().order_by('code')
    context = {
        'page_obj': page_obj,
        'assets': page_obj.object_list,
        'departments': departaments,
        'selected_department': departament_id,
        'title': 'Список основных средств'
    }
    return render(request, 'contract/fixedasset_list.html', context)


def fixed_asset_create(request: HttpRequest):
    if request.method == 'POST':
        form = FixedAssetForm(request.POST)
        if form.is_valid():
            asset = form.save()
            ChangeLog.objects.create(
                entity_type='FixedAsset',
                entity_id=str(asset.pk),
                action='CREATE',
                description=f'Создано ОС: {asset.name}, код: {asset.internal_code}',
                changed_by=request.user.username if request.user.is_authenticated else 'admin'
            )
            messages.success(request, f'Основное средство "{asset.name}" успешно создано! Код: {asset.internal_code}')
            return redirect('contract:fixed_asset_list')
    else:
        form = FixedAssetForm()
    context = {
        'form': form,
        'title': 'Добавление основного средства'
    }
    return render(request, 'contract/fixedasset_form.html', context)


def fixed_asset_edit(request: HttpRequest, pk):
    try:
        asset = get_object_or_404(FixedAsset, pk=pk)
    except Http404:
        messages.error(request, f'Основное средство с ID={pk} не найдено!')
        return redirect('contract:fixed_asset_list')
    
    if request.method == 'POST':
        form = FixedAssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            ChangeLog.objects.create(
                entity_type='FixedAsset',
                entity_id=str(asset.pk),
                action='UPDATE',
                description=f'Обновлено ОС: {asset.name}',
                changed_by=request.user.username if request.user.is_authenticated else 'admin'
            )
            messages.success(request, f'Основное средство "{asset.name}" успешно обновлено!')
            return redirect('contract:fixed_asset_list')
    else:
        form = FixedAssetForm(instance=asset)
    context = {
        'form': form,
        'asset': asset,
        'title': 'Редактирование основного средства'
    }
    return render(request, 'contract/fixedasset_form.html', context)


def fixed_asset_delete(request: HttpRequest, pk):
    try:
        asset = get_object_or_404(FixedAsset, pk=pk)
    except Http404:
        messages.error(request, f'Основное средство с ID={pk} не найдено!')
        return redirect('contract:fixed_asset_list')
    
    if request.method == 'POST':
        asset_name = asset.name
        asset.delete()
        ChangeLog.objects.create(
            entity_type='FixedAsset',
            entity_id=str(pk),
            action='DELETE',
            description=f'Удалено ОС: {asset_name}',
            changed_by=request.user.username if request.user.is_authenticated else 'admin'
        )
        messages.success(request, f'Основное средство "{asset_name}" успешно удалено!')
        return redirect('contract:fixed_asset_list')
    
    context = {
        'asset': asset,
        'title': 'Удаление основного средства'
    }
    return render(request, 'contract/fixedasset_confirm_delete.html', context)


# ============================================================
# AJAX-ОБРАБОТЧИКИ
# ============================================================

@require_http_methods(["POST"])
def generate_internal_code(request: HttpRequest):
    '''Обработчик AJAX для генерации внутреннего кода'''
    try:
        data = json.loads(request.body)
        departament_id = data.get('departament_id')
        if not departament_id:
            return JsonResponse({'error': 'Не выбран отдел'}, status=400)
        departament = get_object_or_404(Departament, pk=departament_id)
        temp_asset = FixedAsset(Departament=departament)
        generated_code = temp_asset.generate_internal_code()
        ChangeLog.objects.create(
            entity_type='FixedAsset',
            entity_id='temp',
            action='CODE_GENERATE',
            description=f'Сгенерирован код {generated_code} для отдела {departament.code}',
            changed_by=request.user.username if request.user.is_authenticated else 'system'
        )
        return JsonResponse({
            'success': True,
            'code': generated_code,
            'sequence_number': temp_asset.get_sequence_number()
        })
    except Departament.DoesNotExist:
        return JsonResponse({'error': 'Отдел не найден'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============================================================
# УПРАВЛЕНИЕ КОНТРАГЕНТАМИ
# ============================================================

def counterparty_list(request: HttpRequest):
    counterparties = Counterparty.objects.all().order_by('name')
    show_deleted = request.GET.get('show_deleted', 'false') == 'true'
    if not show_deleted:
        counterparties = counterparties.filter(deletion_mark=False)
    paginator = Paginator(counterparties, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'counterparties': page_obj.object_list,
        'show_deleted': show_deleted,
        'title': 'Список контрагентов'
    }
    return render(request, 'contract/counterparty_list.html', context)


def counterparty_create(request: HttpRequest):
    if request.method == 'POST':
        form = CounterpartyForm(request.POST)
        if form.is_valid():
            counterparty = form.save()
            ChangeLog.objects.create(
                entity_type='Counterparty',
                entity_id=str(counterparty.internal_code),
                action='CREATE',
                description=f'Создан контрагент: {counterparty.name}, ИНН: {counterparty.inn}',
                changed_by=request.user.username if request.user.is_authenticated else 'admin'
            )
            messages.success(request, f'Контрагент "{counterparty.name}" успешно создан!')
            return redirect('contract:counterparty_list')
    else:
        form = CounterpartyForm()
    context = {
        'form': form,
        'title': 'Добавление контрагента'
    }
    return render(request, 'contract/counterparty_form.html', context)


def counterparty_edit(request: HttpRequest, pk):
    try:
        counterparty = get_object_or_404(Counterparty, internal_code=pk)
    except Http404:
        messages.error(request, f'Контрагент с кодом {pk} не найден!')
        return redirect('contract:counterparty_list')
    
    if request.method == 'POST':
        form = CounterpartyForm(request.POST, instance=counterparty)
        if form.is_valid():
            form.save()
            ChangeLog.objects.create(
                entity_type='Counterparty',
                entity_id=str(counterparty.internal_code),
                action='UPDATE',
                description=f'Обновлён контрагент: {counterparty.name}',
                changed_by=request.user.username if request.user.is_authenticated else 'admin'
            )
            messages.success(request, f'Контрагент "{counterparty.name}" успешно обновлён!')
            return redirect('contract:counterparty_list')
    else:
        form = CounterpartyForm(instance=counterparty)
    context = {
        'form': form,
        'counterparty': counterparty,
        'title': 'Редактирование контрагента'
    }
    return render(request, 'contract/counterparty_form.html', context)


def counterparty_delete(request: HttpRequest, pk):
    try:
        counterparty = get_object_or_404(Counterparty, internal_code=pk)
    except Http404:
        messages.error(request, f'Контрагент с кодом {pk} не найден!')
        return redirect('contract:counterparty_list')
    
    if request.method == 'POST':
        counterparty.mark_as_deleted()
        ChangeLog.objects.create(
            entity_type='Counterparty',
            entity_id=str(counterparty.internal_code),
            action='MARK_DELETE',
            description=f'Помечен на удаление контрагент: {counterparty.name}',
            changed_by=request.user.username if request.user.is_authenticated else 'admin'
        )
        messages.success(request, f'Контрагент "{counterparty.name}" помечен на удаление!')
        return redirect('contract:counterparty_list')
    
    context = {
        'counterparty': counterparty,
        'title': 'Пометка на удаление контрагента'
    }
    return render(request, 'contract/counterparty_confirm_delete.html', context)


def counterparty_restore(request: HttpRequest, pk):
    try:
        counterparty = get_object_or_404(Counterparty, internal_code=pk)
    except Http404:
        messages.error(request, f'Контрагент с кодом {pk} не найден!')
        return redirect('contract:counterparty_list')
    
    counterparty.deletion_mark = False
    counterparty.save(update_fields=['deletion_mark', 'updated_at'])
    ChangeLog.objects.create(
        entity_type='Counterparty',
        entity_id=str(counterparty.internal_code),
        action='UPDATE',
        description=f'Восстановлен контрагент: {counterparty.name} (снята пометка удаления)',
        changed_by=request.user.username if request.user.is_authenticated else 'admin'
    )
    messages.success(request, f'Контрагент "{counterparty.name}" восстановлен!')
    return redirect('contract:counterparty_list')


# ============================================================
# AJAX-ОБРАБОТЧИК ДЛЯ ПРОВЕРКИ ИНН
# ============================================================

@require_http_methods(["POST"])
def check_inn(request: HttpRequest):
    '''AJAX обработчик для проверки ИНН на дубликаты'''
    try:
        data = json.loads(request.body)
        inn = data.get('inn', '').strip()
        current_id = data.get('current_id', None)
        if not inn:
            return JsonResponse({'error': 'ИНН не может быть пустым'}, status=400)
        
        exact_matches = Counterparty.objects.filter(
            inn=inn,
            deletion_mark=False
        )
        if current_id:
            exact_matches = exact_matches.exclude(internal_code=current_id)
        
        substring_matches = Counterparty.objects.filter(
            inn__contains=inn,
            deletion_mark=False
        ).exclude(inn=inn)
        if current_id:
            substring_matches = substring_matches.exclude(internal_code=current_id)
        
        result = {
            'exact': [
                {
                    'name': c.name,
                    'code': c.internal_code,
                    'inn': c.inn
                }
                for c in exact_matches
            ],
            'substring': [
                {
                    'name': c.name,
                    'code': c.internal_code,
                    'inn': c.inn
                }
                for c in substring_matches
            ]
        }
        
        ChangeLog.objects.create(
            entity_type='Counterparty',
            entity_id=current_id or 'unknown',
            action='DUPLICATE_CHECK',
            description=f'Проверка ИНН {inn}: найдено {len(exact_matches)} точных и {len(substring_matches)} частичных совпадений',
            changed_by=request.user.username if request.user.is_authenticated else 'system'
        )
        
        return JsonResponse({'success': True, 'result': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============================================================
# ПОИСК ДУБЛИКАТОВ
# ============================================================

def duplicate_groups(request: HttpRequest):
    duplicate_groups_data = Counterparty.find_all_duplicate_groups()
    if request.method == 'POST':
        form = BullDeleteForm(request.POST)
        if form.is_valid():
            counterparties = form.cleaned_data['counterparty_ids']
            count = 0
            for cp in counterparties:
                if not cp.deletion_mark:
                    cp.mark_as_deleted()
                    count += 1
                    ChangeLog.objects.create(
                        entity_type='Counterparty',
                        entity_id=str(cp.internal_code),
                        action='MARK_DELETE',
                        description=f'Помечен на удаление (массовая операция): {cp.name}',
                        changed_by=request.user.username if request.user.is_authenticated else 'admin'
                    )
            messages.success(request, f'Помечено на удаление {count} контрагентов!')
            return redirect('contract:duplicate_groups')
    else:
        form = BullDeleteForm()
    
    context = {
        'duplicate_groups': duplicate_groups_data,
        'form': form,
        'title': 'Поиск дубликатов по ИНН'
    }
    return render(request, 'contract/duplicate_groups.html', context)


def check_duplicate_form(request: HttpRequest):
    result = None
    searched_inn = None
    if request.method == 'POST':
        form = DuplicateCheckForm(request.POST)
        if form.is_valid():
            searched_inn = form.cleaned_data['inn']
            temp_counterparty = Counterparty(inn=searched_inn)
            exact = temp_counterparty.find_exact_inn_duplicates()
            substring = temp_counterparty.find_substring_duplicates()
            
            result = {
                'exact': exact,
                'substring': substring,
                'inn': searched_inn
            }
            ChangeLog.objects.create(
                entity_type='Counterparty',
                entity_id='form_check',
                action='DUPLICATE_CHECK',
                description=f'Ручная проверка ИНН {searched_inn}',
                changed_by=request.user.username if request.user.is_authenticated else 'user'
            )
    else:
        form = DuplicateCheckForm()
    context = {
        'form': form,
        'result': result,
        'searched_inn': searched_inn,
        'title': 'Проверка ИНН контрагента'
    }
    return render(request, 'contract/check_duplicate_form.html', context)


# ============================================================
# ЖУРНАЛ ИЗМЕНЕНИЙ
# ============================================================

def changelog_list(request: HttpRequest):
    logs = ChangeLog.objects.all().select_related()[:100]
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'logs': page_obj.object_list,
        'title': 'Журнал изменений'
    }
    return render(request, 'contract/changelog_list.html', context)
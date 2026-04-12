from django.db import models
from django.core.exceptions import ValidationError

# ============================================================

class Departament(models.Model):
    """
    Модель подразделения организации.
    Используется как место хранения основных средств.
    """
    name = models.CharField(
        max_length=200,
        verbose_name="Название подразделения",
    )
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Код подразделения",
    )
    
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    
    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# ============================================================

class FixedAsset(models.Model):
    """
    Модель основного средства (ОС).
    Содержит код внутреннего учета, генерируемый по правилу:
    Код подразделения + порядковый номер ОС в подразделении
    """
    name = models.CharField(
        max_length=250,
        verbose_name="Наименование основного средства",
    )
    
    Departament = models.ForeignKey(
        Departament,
        on_delete=models.CASCADE,
        related_name='fixed_assets',
        verbose_name="Подразделение (место хранения)",
    )
    
    internal_code = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Код внутреннего учета",
    )
    
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    
    class Meta:
        verbose_name = "Основное средство"
        verbose_name_plural = "Основные средства"
        ordering = ['Departament', 'internal_code']
    
    def __str__(self):
        return f"{self.internal_code or 'Без кода'} - {self.name}"
    
    def get_sequence_number(self):
        """
        Возвращает порядковый номер для нового ОС в данном подразделении.
        Номер = количество существующих ОС в подразделении + 1
        """
        count = FixedAsset.objects.filter(Departament=self.Departament).count()
        return count + 1
    
    def generate_internal_code(self):
        """
        Генерирует код внутреннего учета по правилу:
        Код подразделения + порядковый номер
        """
        if self.Departament:
            seq_num = self.get_sequence_number()
            return f"{self.Departament.code}{seq_num}"
        return None
    
    def save(self, *args, **kwargs):
        """
        Переопределяем save для автоматической генерации кода,
        если он не был установлен вручную.
        """
        if not self.internal_code and self.Departament:
            self.internal_code = self.generate_internal_code()
        super().save(*args, **kwargs)


# ============================================================

class Counterparty(models.Model):
    """
    Модель контрагента (юридического или физического лица).
    Содержит проверки ИНН и возможность пометки на удаление.
    """
    name = models.CharField(
        max_length=300,
        verbose_name="Наименование контрагента",
        help_text="Полное наименование организации или ФИО"
    )
    
    inn = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        verbose_name="ИНН",
    )
    
    internal_code = models.AutoField(
        primary_key=True,
        verbose_name="Внутренний код",
    )
    
    deletion_mark = models.BooleanField(
        default=False,
        verbose_name="Пометка удаления",
    )
    
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    
    class Meta:
        verbose_name = "Контрагент"
        verbose_name_plural = "Контрагенты"
        ordering = ['name']
    
    def __str__(self):
        inn_display = f" (ИНН: {self.inn})" if self.inn else " (ИНН не указан)"
        mark = " [УДАЛЕН]" if self.deletion_mark else ""
        return f"{self.name}{inn_display}{mark}"
    
    def is_inn_empty(self):
        """Проверяет, пустой ли ИНН"""
        return not self.inn or self.inn.strip() == ''
    
    def clean(self):
        """
        Валидация на уровне модели (вызывается при сохранении через form).
        Проверка: ИНН не может быть пустым.
        """
        from django.core.exceptions import ValidationError
        
        if self.is_inn_empty():
            raise ValidationError({'inn': 'ИНН не может быть пустым. Заполните ИНН контрагента.'})
    
    def find_exact_inn_duplicates(self):
        """
        Находит контрагентов с точно таким же ИНН (исключая себя)
        """
        if self.is_inn_empty():
            return Counterparty.objects.none()
        return Counterparty.objects.filter(
            inn=self.inn,
            deletion_mark=False
        ).exclude(internal_code=self.internal_code)
    
    def find_substring_duplicates(self):
        """
        Находит контрагентов, у которых ИНН содержит текущий ИНН как подстроку
        или текущий ИНН содержится в их ИНН (исключая точное совпадение и себя)
        """
        if self.is_inn_empty():
            return Counterparty.objects.none()
        
        from django.db.models import Q
        
        return Counterparty.objects.filter(
            Q(inn__contains=self.inn) | Q(inn=self.inn),
            deletion_mark=False
        ).exclude(
            internal_code=self.internal_code
        ).exclude(
            inn=self.inn  # убираем точные совпадения, чтобы не дублировать
        )
    
    def mark_as_deleted(self):
        """Помечает контрагента на удаление"""
        self.deletion_mark = True
        self.save(update_fields=['deletion_mark', 'updated_at'])
    
    @classmethod
    def find_all_duplicate_groups(cls):
        """
        Находит все группы контрагентов с одинаковым ИНН.
        """
        from django.db.models import Count
        
        duplicate_inns = cls.objects.filter(
            deletion_mark=False,
            inn__isnull=False
        ).exclude(
            inn=''
        ).values('inn').annotate(
            count=Count('internal_code')
        ).filter(count__gt=1)
        
        result = {}
        for item in duplicate_inns:
            inn_value = item['inn']
            counterparties = cls.objects.filter(
                inn=inn_value,
                deletion_mark=False
            ).order_by('name')
            result[inn_value] = list(counterparties)
        
        return result


# ============================================================

class ChangeLog(models.Model):
    """
    Модель для фиксации изменений (имитация реестра изменений из правил модификации).
    """
    ACTION_CHOICES = [
        ('CREATE', 'Создание'),
        ('UPDATE', 'Обновление'),
        ('DELETE', 'Удаление'),
        ('MARK_DELETE', 'Пометка на удаление'),
        ('CODE_GENERATE', 'Генерация кода'),
        ('DUPLICATE_CHECK', 'Проверка дубликатов'),
    ]
    TYPE_ENTITY=[
        ('FixedAsset','FixedAsset'),
        ('Counterparty','Counterparty'),
        ('Departament','Departament')
    ]
    
    entity_type = models.CharField(
        max_length=50,
        verbose_name="Тип сущности",
        choices=TYPE_ENTITY
    )
    
    entity_id = models.CharField(
        max_length=50,
        verbose_name="ID сущности",
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="Действие"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Описание изменения"
    )
    
    changed_by = models.CharField(
        max_length=100,
        default='system',
        verbose_name="Кто выполнил изменение"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время изменения"
    )
    
    class Meta:
        verbose_name = "Журнал изменений"
        verbose_name_plural = "Журнал изменений"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.created_at} - {self.entity_type} #{self.entity_id} - {self.action}"
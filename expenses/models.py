from django.db import models
from django.utils import timezone
import uuid


class Villa(models.Model):
    name = models.CharField(max_length=200, verbose_name='اسم الفيلا')
    code = models.CharField(max_length=50, unique=True, verbose_name='الكود')
    location = models.CharField(max_length=300, blank=True, null=True, verbose_name='الموقع')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'فيلا'
        verbose_name_plural = 'الفيلات'
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def get_total_direct(self):
        return self.allocations.filter(
            expense__expense_type='direct'
        ).aggregate(total=models.Sum('allocated_amount'))['total'] or 0

    def get_total_indirect(self):
        return self.allocations.filter(
            expense__expense_type='indirect'
        ).aggregate(total=models.Sum('allocated_amount'))['total'] or 0

    def get_grand_total(self):
        return self.allocations.aggregate(
            total=models.Sum('allocated_amount')
        )['total'] or 0


class ExpenseCategory(models.Model):
    CATEGORY_TYPE_CHOICES = [
        ('direct', 'مباشر'),
        ('indirect', 'غير مباشر'),
    ]

    name = models.CharField(max_length=200, verbose_name='اسم التصنيف')
    category_type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPE_CHOICES,
        verbose_name='نوع التصنيف'
    )

    class Meta:
        verbose_name = 'تصنيف مصروف'
        verbose_name_plural = 'تصنيفات المصروفات'
        ordering = ['category_type', 'name']
        unique_together = ['name', 'category_type']

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Expense(models.Model):
    EXPENSE_TYPE_CHOICES = [
        ('direct', 'مباشر'),
        ('indirect', 'غير مباشر'),
    ]

    reference_number = models.CharField(
        max_length=50, unique=True,
        verbose_name='رقم المرجع',
        editable=False
    )
    title = models.CharField(max_length=300, verbose_name='العنوان')
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        verbose_name='التصنيف',
        related_name='expenses'
    )
    expense_type = models.CharField(
        max_length=10,
        choices=EXPENSE_TYPE_CHOICES,
        verbose_name='نوع المصروف'
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name='المبلغ الإجمالي'
    )
    date = models.DateField(verbose_name='التاريخ')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    supplier_name = models.CharField(
        max_length=200, blank=True, null=True,
        verbose_name='اسم المورد'
    )
    invoice_image = models.FileField(
        upload_to='invoices/%Y/%m/',
        blank=True, null=True,
        verbose_name='صورة الفاتورة'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'مصروف'
        verbose_name_plural = 'المصروفات'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.reference_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self._generate_reference()
        super().save(*args, **kwargs)

    def _generate_reference(self):
        year = timezone.now().year
        prefix = f"EXP-{year}-"
        last = Expense.objects.filter(
            reference_number__startswith=prefix
        ).order_by('-reference_number').first()
        if last:
            try:
                last_num = int(last.reference_number.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1
        return f"{prefix}{new_num:05d}"

    def get_allocated_total(self):
        return self.allocations.aggregate(
            total=models.Sum('allocated_amount')
        )['total'] or 0

    def get_remaining_to_allocate(self):
        return self.total_amount - self.get_allocated_total()

    def is_image(self):
        if self.invoice_image:
            name = self.invoice_image.name.lower()
            return name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
        return False


class ExpenseAllocation(models.Model):
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name='allocations',
        verbose_name='المصروف'
    )
    villa = models.ForeignKey(
        Villa,
        on_delete=models.CASCADE,
        related_name='allocations',
        verbose_name='الفيلا'
    )
    allocated_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name='المبلغ المخصص'
    )

    class Meta:
        verbose_name = 'تخصيص مصروف'
        verbose_name_plural = 'تخصيصات المصروفات'
        unique_together = ['expense', 'villa']
        ordering = ['-expense__date']

    def __str__(self):
        return f"{self.expense.title} → {self.villa.name}: {self.allocated_amount}"

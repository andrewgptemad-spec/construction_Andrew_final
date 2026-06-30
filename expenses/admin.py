from django.contrib import admin
from .models import Villa, ExpenseCategory, Expense, ExpenseAllocation


@admin.register(Villa)
class VillaAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'location']
    search_fields = ['name', 'code']


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type']
    list_filter = ['category_type']


class AllocationInline(admin.TabularInline):
    model = ExpenseAllocation
    extra = 1
    fields = ['villa', 'allocated_amount']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'title', 'category', 'expense_type', 'total_amount', 'date']
    list_filter = ['expense_type', 'category', 'date']
    search_fields = ['title', 'reference_number', 'supplier_name']
    inlines = [AllocationInline]
    readonly_fields = ['reference_number', 'created_at', 'updated_at']


@admin.register(ExpenseAllocation)
class ExpenseAllocationAdmin(admin.ModelAdmin):
    list_display = ['expense', 'villa', 'allocated_amount']
    list_filter = ['villa']

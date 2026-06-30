from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import models as db_models, transaction
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from decimal import Decimal
import json

from .models import Villa, ExpenseCategory, Expense, ExpenseAllocation
from .forms import ExpenseForm, ExpenseFilterForm, ReportFilterForm, UserSignupForm


def user_can_manage_expenses(request):
    return request.user.is_staff or request.user.is_superuser


def ensure_manage_permission(request):
    if not user_can_manage_expenses(request):
        messages.error(request, 'ليس لديك صلاحية لتنفيذ هذا الإجراء.')
        return redirect('dashboard')
    return None


def ensure_admin_permission(request):
    if not request.user.is_superuser:
        messages.error(request, 'هذه الصفحة مخصصة للمسؤول فقط.')
        return redirect('dashboard')
    return None


# ─────────────────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    villas = Villa.objects.all()
    villa_data = []
    for villa in villas:
        villa_data.append({
            'villa': villa,
            'direct': villa.get_total_direct(),
            'indirect': villa.get_total_indirect(),
            'total': villa.get_grand_total(),
        })

    total_direct = ExpenseAllocation.objects.filter(
        expense__expense_type='direct'
    ).aggregate(t=Sum('allocated_amount'))['t'] or 0

    total_indirect = ExpenseAllocation.objects.filter(
        expense__expense_type='indirect'
    ).aggregate(t=Sum('allocated_amount'))['t'] or 0

    total_all = total_direct + total_indirect

    recent_expenses = Expense.objects.select_related('category').prefetch_related(
        'allocations__villa'
    ).order_by('-date', '-created_at')[:10]

    context = {
        'villa_data': villa_data,
        'total_direct': total_direct,
        'total_indirect': total_indirect,
        'total_all': total_all,
        'recent_expenses': recent_expenses,
    }
    return render(request, 'expenses/dashboard.html', context)


# ─────────────────────────────────────────────────────────
#  EXPENSE LIST
# ─────────────────────────────────────────────────────────
@login_required
def expense_list(request):
    form = ExpenseFilterForm(request.GET or None)
    qs = Expense.objects.select_related('category').prefetch_related(
        'allocations__villa'
    ).order_by('-date', '-created_at')

    if form.is_valid():
        q = form.cleaned_data.get('q')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        expense_type = form.cleaned_data.get('expense_type')
        category = form.cleaned_data.get('category')
        villa = form.cleaned_data.get('villa')
        supplier = form.cleaned_data.get('supplier')

        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(category__name__icontains=q) |
                Q(supplier_name__icontains=q) |
                Q(notes__icontains=q) |
                Q(reference_number__icontains=q)
            )
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if expense_type:
            qs = qs.filter(expense_type=expense_type)
        if category:
            qs = qs.filter(category=category)
        if villa:
            qs = qs.filter(allocations__villa=villa)
        if supplier:
            qs = qs.filter(supplier_name__icontains=supplier)

    qs = qs.distinct()
    paginator = Paginator(qs, 25)
    page = request.GET.get('page', 1)
    expenses = paginator.get_page(page)

    total_amount = qs.aggregate(t=Sum('total_amount'))['t'] or 0

    context = {
        'form': form,
        'expenses': expenses,
        'total_amount': total_amount,
        'total_count': qs.count(),
    }
    return render(request, 'expenses/expense_list.html', context)


# ─────────────────────────────────────────────────────────
#  ADD EXPENSE
# ─────────────────────────────────────────────────────────
@login_required
def expense_add(request):
    permission_redirect = ensure_manage_permission(request)
    if permission_redirect:
        return permission_redirect

    villas = Villa.objects.all()
    categories = list(ExpenseCategory.objects.values('id', 'name', 'category_type'))

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        allocation_mode = request.POST.get('allocation_mode', 'equal')
        selected_villas = request.POST.getlist('selected_villas')
        custom_amounts = {}

        for key, val in request.POST.items():
            if key.startswith('amount_villa_'):
                villa_id = key.replace('amount_villa_', '')
                try:
                    custom_amounts[int(villa_id)] = Decimal(val or '0')
                except Exception:
                    pass

        if not selected_villas:
            messages.error(request, 'يجب اختيار فيلا واحدة على الأقل.')
        elif form.is_valid():
            expense = form.save(commit=False)
            total = expense.total_amount

            # Calculate allocations
            allocations = {}
            if allocation_mode == 'equal':
                per_villa = (total / len(selected_villas)).quantize(Decimal('0.01'))
                for vid in selected_villas:
                    allocations[int(vid)] = per_villa
                # Fix rounding: add remainder to last villa
                remainder = total - (per_villa * len(selected_villas))
                if remainder != 0 and selected_villas:
                    last = int(selected_villas[-1])
                    allocations[last] = allocations[last] + remainder
            else:
                alloc_sum = Decimal('0')
                for vid in selected_villas:
                    vid_int = int(vid)
                    amt = custom_amounts.get(vid_int, Decimal('0'))
                    allocations[vid_int] = amt
                    alloc_sum += amt

                if alloc_sum != total:
                    messages.error(
                        request,
                        f'مجموع التخصيصات ({alloc_sum}) يجب أن يساوي المبلغ الإجمالي ({total}).'
                    )
                    context = {
                        'form': form,
                        'villas': villas,
                        'categories_json': json.dumps(categories),
                    }
                    return render(request, 'expenses/expense_form.html', context)

            # Validate all villa IDs exist
            villa_objects = Villa.objects.filter(id__in=[int(v) for v in selected_villas])
            if villa_objects.count() != len(selected_villas):
                messages.error(request, 'بعض الفيلات المختارة غير موجودة.')
            else:
                with transaction.atomic():
                    expense.save()
                    for villa_obj in villa_objects:
                        amt = allocations.get(villa_obj.id, Decimal('0'))
                        ExpenseAllocation.objects.create(
                            expense=expense,
                            villa=villa_obj,
                            allocated_amount=amt
                        )
                messages.success(
                    request,
                    f'تم إضافة المصروف بنجاح. رقم المرجع: {expense.reference_number}'
                )
                return redirect('expense_detail', pk=expense.pk)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = ExpenseForm()

    context = {
        'form': form,
        'villas': villas,
        'categories_json': json.dumps(categories),
    }
    return render(request, 'expenses/expense_form.html', context)


# ─────────────────────────────────────────────────────────
#  EXPENSE DETAIL
# ─────────────────────────────────────────────────────────
@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(
        Expense.objects.select_related('category').prefetch_related('allocations__villa'),
        pk=pk
    )
    context = {'expense': expense}
    return render(request, 'expenses/expense_detail.html', context)


# ─────────────────────────────────────────────────────────
#  EDIT EXPENSE
# ─────────────────────────────────────────────────────────
@login_required
def expense_edit(request, pk):
    permission_redirect = ensure_manage_permission(request)
    if permission_redirect:
        return permission_redirect

    expense = get_object_or_404(Expense, pk=pk)
    villas = Villa.objects.all()
    categories = list(ExpenseCategory.objects.values('id', 'name', 'category_type'))
    existing_allocations = {
        a.villa_id: a.allocated_amount
        for a in expense.allocations.all()
    }

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        allocation_mode = request.POST.get('allocation_mode', 'equal')
        selected_villas = request.POST.getlist('selected_villas')
        custom_amounts = {}

        for key, val in request.POST.items():
            if key.startswith('amount_villa_'):
                villa_id = key.replace('amount_villa_', '')
                try:
                    custom_amounts[int(villa_id)] = Decimal(val or '0')
                except Exception:
                    pass

        if not selected_villas:
            messages.error(request, 'يجب اختيار فيلا واحدة على الأقل.')
        elif form.is_valid():
            expense = form.save(commit=False)
            total = expense.total_amount
            allocations = {}

            if allocation_mode == 'equal':
                per_villa = (total / len(selected_villas)).quantize(Decimal('0.01'))
                for vid in selected_villas:
                    allocations[int(vid)] = per_villa
                remainder = total - (per_villa * len(selected_villas))
                if remainder != 0 and selected_villas:
                    last = int(selected_villas[-1])
                    allocations[last] = allocations[last] + remainder
            else:
                alloc_sum = Decimal('0')
                for vid in selected_villas:
                    vid_int = int(vid)
                    amt = custom_amounts.get(vid_int, Decimal('0'))
                    allocations[vid_int] = amt
                    alloc_sum += amt

                if alloc_sum != total:
                    messages.error(
                        request,
                        f'مجموع التخصيصات ({alloc_sum}) يجب أن يساوي المبلغ الإجمالي ({total}).'
                    )
                    context = {
                        'form': form,
                        'villas': villas,
                        'categories_json': json.dumps(categories),
                        'expense': expense,
                        'existing_allocations': existing_allocations,
                        'is_edit': True,
                    }
                    return render(request, 'expenses/expense_form.html', context)

            villa_objects = Villa.objects.filter(id__in=[int(v) for v in selected_villas])
            with transaction.atomic():
                expense.save()
                expense.allocations.all().delete()
                for villa_obj in villa_objects:
                    amt = allocations.get(villa_obj.id, Decimal('0'))
                    ExpenseAllocation.objects.create(
                        expense=expense,
                        villa=villa_obj,
                        allocated_amount=amt
                    )
            messages.success(request, 'تم تحديث المصروف بنجاح.')
            return redirect('expense_detail', pk=expense.pk)
    else:
        form = ExpenseForm(instance=expense)

    context = {
        'form': form,
        'villas': villas,
        'categories_json': json.dumps(categories),
        'expense': expense,
        'existing_allocations': existing_allocations,
        'is_edit': True,
    }
    return render(request, 'expenses/expense_form.html', context)


# ─────────────────────────────────────────────────────────
#  DELETE EXPENSE
# ─────────────────────────────────────────────────────────
@login_required
def expense_delete(request, pk):
    permission_redirect = ensure_manage_permission(request)
    if permission_redirect:
        return permission_redirect

    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        ref = expense.reference_number
        expense.delete()
        messages.success(request, f'تم حذف المصروف {ref} بنجاح.')
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})


# ─────────────────────────────────────────────────────────
#  VILLA DETAIL
# ─────────────────────────────────────────────────────────
@login_required
def villa_detail(request, pk):
    villa = get_object_or_404(Villa, pk=pk)
    q = request.GET.get('q', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    expense_type = request.GET.get('expense_type', '')
    category_id = request.GET.get('category', '')

    allocations = ExpenseAllocation.objects.filter(
        villa=villa
    ).select_related('expense__category').order_by('-expense__date', '-expense__created_at')

    if q:
        allocations = allocations.filter(
            Q(expense__title__icontains=q) |
            Q(expense__category__name__icontains=q) |
            Q(expense__supplier_name__icontains=q) |
            Q(expense__notes__icontains=q)
        )
    if date_from:
        allocations = allocations.filter(expense__date__gte=date_from)
    if date_to:
        allocations = allocations.filter(expense__date__lte=date_to)
    if expense_type:
        allocations = allocations.filter(expense__expense_type=expense_type)
    if category_id:
        allocations = allocations.filter(expense__category_id=category_id)

    total_direct = villa.get_total_direct()
    total_indirect = villa.get_total_indirect()
    grand_total = villa.get_grand_total()

    filtered_total = allocations.aggregate(t=Sum('allocated_amount'))['t'] or 0

    paginator = Paginator(allocations, 25)
    page = request.GET.get('page', 1)
    alloc_page = paginator.get_page(page)

    categories = ExpenseCategory.objects.all()

    context = {
        'villa': villa,
        'allocations': alloc_page,
        'total_direct': total_direct,
        'total_indirect': total_indirect,
        'grand_total': grand_total,
        'filtered_total': filtered_total,
        'q': q,
        'date_from': date_from,
        'date_to': date_to,
        'expense_type': expense_type,
        'category_id': category_id,
        'categories': categories,
    }
    return render(request, 'expenses/villa_detail.html', context)


# ─────────────────────────────────────────────────────────
#  VILLA LIST
# ─────────────────────────────────────────────────────────
@login_required
def villa_list(request):
    villas = Villa.objects.all()
    villa_data = []
    for villa in villas:
        villa_data.append({
            'villa': villa,
            'direct': villa.get_total_direct(),
            'indirect': villa.get_total_indirect(),
            'total': villa.get_grand_total(),
        })
    context = {'villa_data': villa_data}
    return render(request, 'expenses/villa_list.html', context)


# ─────────────────────────────────────────────────────────
#  GLOBAL SEARCH
# ─────────────────────────────────────────────────────────
@login_required
def global_search(request):
    q = request.GET.get('q', '')
    results = []
    total_found = 0

    if q:
        allocations = ExpenseAllocation.objects.filter(
            Q(expense__title__icontains=q) |
            Q(expense__category__name__icontains=q) |
            Q(expense__supplier_name__icontains=q) |
            Q(expense__notes__icontains=q)
        ).select_related('expense__category', 'villa').order_by(
            '-expense__date', '-expense__created_at'
        ).distinct()

        total_found = allocations.count()
        paginator = Paginator(allocations, 30)
        page = request.GET.get('page', 1)
        results = paginator.get_page(page)

    context = {
        'q': q,
        'results': results,
        'total_found': total_found,
    }
    return render(request, 'expenses/global_search.html', context)


# ─────────────────────────────────────────────────────────
#  REPORTS
# ─────────────────────────────────────────────────────────
@login_required
def reports(request):
    form = ReportFilterForm(request.GET or None)
    date_from = None
    date_to = None
    expense_type = ''

    if form.is_valid():
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        expense_type = form.cleaned_data.get('expense_type', '')

    # Base queryset
    base_alloc = ExpenseAllocation.objects.select_related('expense__category', 'villa')
    if date_from:
        base_alloc = base_alloc.filter(expense__date__gte=date_from)
    if date_to:
        base_alloc = base_alloc.filter(expense__date__lte=date_to)
    if expense_type:
        base_alloc = base_alloc.filter(expense__expense_type=expense_type)

    # Expenses by villa
    villa_report = base_alloc.values(
        'villa__name', 'villa__code'
    ).annotate(
        total=Sum('allocated_amount'),
        direct=Sum('allocated_amount', filter=Q(expense__expense_type='direct')),
        indirect=Sum('allocated_amount', filter=Q(expense__expense_type='indirect')),
    ).order_by('-total')

    # Expenses by category
    category_report = base_alloc.values(
        'expense__category__name',
        'expense__category__category_type'
    ).annotate(
        total=Sum('allocated_amount')
    ).order_by('-total')

    # Direct vs Indirect totals
    total_direct = base_alloc.filter(
        expense__expense_type='direct'
    ).aggregate(t=Sum('allocated_amount'))['t'] or 0

    total_indirect = base_alloc.filter(
        expense__expense_type='indirect'
    ).aggregate(t=Sum('allocated_amount'))['t'] or 0

    grand_total = total_direct + total_indirect

    direct_pct = (total_direct / grand_total * 100) if grand_total else 0
    indirect_pct = (total_indirect / grand_total * 100) if grand_total else 0

    context = {
        'form': form,
        'villa_report': villa_report,
        'category_report': category_report,
        'total_direct': total_direct,
        'total_indirect': total_indirect,
        'grand_total': grand_total,
        'direct_pct': round(direct_pct, 1),
        'indirect_pct': round(indirect_pct, 1),
        'date_from': date_from,
        'date_to': date_to,
        'expense_type': expense_type,
    }
    return render(request, 'expenses/reports.html', context)


# ─────────────────────────────────────────────────────────
#  USER MANAGEMENT
# ─────────────────────────────────────────────────────────
@login_required
def user_list(request):
    permission = ensure_admin_permission(request)
    if permission:
        return permission

    users = User.objects.filter(is_superuser=False).order_by('username')
    return render(request, 'expenses/user_list.html', {'users': users})


@login_required
def user_add(request):
    permission = ensure_admin_permission(request)
    if permission:
        return permission

    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.is_superuser = False
            user.save()
            messages.success(request, f'تم إنشاء المستخدم {user.username} بنجاح.')
            return redirect('user_list')
    else:
        form = UserSignupForm()

    return render(request, 'expenses/user_form.html', {'form': form})


# ─────────────────────────────────────────────────────────
#  AJAX: Get categories by type
# ─────────────────────────────────────────
@login_required
def get_categories(request):
    cat_type = request.GET.get('type', '')
    if cat_type:
        cats = ExpenseCategory.objects.filter(category_type=cat_type).values('id', 'name')
    else:
        cats = ExpenseCategory.objects.all().values('id', 'name', 'category_type')
    return JsonResponse({'categories': list(cats)})

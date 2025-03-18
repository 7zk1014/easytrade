
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import Report

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def admin_report_list(request):
    """Admin view for managing all reports"""
    reports = Report.objects.all()
    
    # 处理筛选
    status = request.GET.get('status')
    report_type = request.GET.get('type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if status:
        reports = reports.filter(status=status)
    if report_type:
        reports = reports.filter(report_type=report_type)
    if start_date:
        reports = reports.filter(created_at__gte=start_date)
    if end_date:
        reports = reports.filter(created_at__lte=end_date)
    
    reports = reports.order_by('-created_at')
    
    return render(request, 'reports/admin_report_list.html', {
        'reports': reports,
        'title': 'Administrator Dashboard'
    })

@user_passes_test(is_admin)
def update_report_status(request, report_id):
    """Update report status"""
    if request.method == 'POST':
        report = get_object_or_404(Report, id=report_id)
        new_status = request.POST.get('status')
        
        if new_status in ['pending', 'in_progress', 'resolved']:
            report.status = new_status
            report.save()
            messages.success(request, f'Report #{report_id} status has been updated to {new_status}')
        else:
            messages.error(request, 'Invalid status value')
            
        return redirect('reports:admin_report_list')
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def submit_report(request):
    """Submit a new report"""
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        description = request.POST.get('description')
        order_id = request.POST.get('order_id')
        
        if not description:
            messages.error(request, 'Please provide a description')
            return redirect('order_detail', order_id=order_id)
            
        report = Report.objects.create(
            reporter=request.user,
            report_type=report_type,
            description=description,
            order_id=order_id if order_id else None
        )
        
        messages.success(request, 'Your report has been submitted successfully')
        return redirect('order_detail', order_id=order_id)
        
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def report_list(request):
    """Display user's reports"""
    reports = Report.objects.filter(reporter=request.user).order_by('-created_at')
    return render(request, 'reports/report_list.html', {
        'reports': reports,
        'title': 'My Reports'
    })

def report_detail(request, report_id):
    """Display report details"""
    report = get_object_or_404(Report, id=report_id)
    
    # Check if user has permission to view this report
    if request.user != report.reporter and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this report')
        return redirect('reports:report_list')
        
    return render(request, 'reports/report_detail.html', {
        'report': report,
        'title': f'Report #{report.id}'
    })
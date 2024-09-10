from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import auth
from django.http import JsonResponse
from .utils import is_ajax, classify_face
import base64
from django.utils import timezone
from .models import Profile, Attendance
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from io import BytesIO
from PIL import Image
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from datetime import datetime
import pytz
now_local = timezone.now().astimezone(pytz.timezone('Asia/Ho_Chi_Minh')).replace(microsecond=0)
# Create your views here.

def user_register(request):
  title='Đăng Ký'
  if request.user.is_authenticated:
    return redirect('account')
  if request.POST:
    username = request.POST.get('username')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('useremail')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')
    if password1!=password2:
      messages.error(request, 'Mật Khẩu không khớp')
      return redirect('register')
    if User.objects.filter(username=username).exists():
      messages.error(request, 'Tên người dùng đã tồn tại')
      return redirect('register')
    if User.objects.filter(email=email).exists():
        messages.error(request, 'Email đã được sử dụng')
        return redirect('register')
    user = User.objects.create(username=username, first_name=first_name, last_name=last_name, email=email, password=password1)
    auth.login(request, user)
    messages.success(request, 'Đăng ký thành công')
    return redirect('home')
  return render(request, 'pages/register.html', {'title': title})

def user_login_fi(request):
  if request.user.is_authenticated:
    return redirect('account')
  title = 'Face ID'
  return render(request, 'pages/login_faceid.html', {'title': title})

def user_login_df(request):
  if request.user.is_authenticated:
    return redirect('account')
  title = 'Đăng Nhập'
  if request.POST:
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = auth.authenticate(username=username, password=password)
    if user is not None:
      auth.login(request,user)
      return redirect('home')
    else:
      messages.error(request,'Tài Khoản hoặc Mật Khẩu không đúng')
      return redirect('login-default')
  return render(request, 'pages/login_default.html', {'title': title})

def user_logout(request):
  auth.logout(request)
  return redirect('home')

def user_account(request):
  if request.user.is_authenticated:
    title = 'Tài Khoản'
    try:
      attendance = Attendance.objects.order_by('-date').filter(user = request.user).first()
    except Attendance.DoesNotExist:
      attendance=None
    if attendance:
      print(attendance.date)
      if attendance.date < now_local.date():
        attendance.checked_in = False
      if attendance.date == now_local.date():
        if attendance.check_in_time < now_local.time():
          attendance.checked_in = True
        if not attendance.check_out_time:
          attendance.checked_out = False
        else:
          attendance.checked_out = True
    return render(request, 'pages/account.html', {'title': title, 'attendance': attendance})     
  else:
    return redirect('login-default')

def home(request):
  title = 'Quản Lý Nhân Viên'
  return render(request, 'pages/home.html', {'title': title})

def user_profile(request, str):
  if request.user.is_superuser or request.user.username == str:
    title = f'Hồ Sơ của {str}'
    user = User.objects.get(username=str)
    return render(request, 'pages/profile.html', {'title': title, 'user': user})
  else:
    return redirect('account')

def create_faceid(request):
  title = 'Tạo Face ID'
  if is_ajax(request):
    photo = request.POST.get('photo')
    _, str_img = photo.split(';base64')
    decoded_file = base64.b64decode(str_img)
    profile = Profile.objects.get(user=request.user)
    profile.photo = ContentFile(decoded_file, 'upload.png')
    if not profile.start_date:
      profile.start_date = timezone.now()
    profile.save()
    messages.success(request, 'Cập nhật Face ID thành công')
    return JsonResponse({'success': True, 'redirect_url': '/account/'})
  return render(request, 'pages/create_faceid.html', {'title': title})

def find_user_view(request):
  if is_ajax(request):
    photo = request.POST.get('photo')
    _, str_img = photo.split(';base64')
    decoded_file = base64.b64decode(str_img)
    img = Image.open(BytesIO(decoded_file))
    img_io = BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    res = classify_face(img_io)
    user_exists = User.objects.filter(username=res).exists()
    if user_exists:
      user = get_object_or_404(User, username=res)
      auth.login(request, user)
      messages.success(request, 'Đăng Nhập thành công')
      return JsonResponse({'success': True, 'redirect_url': ''})
    return JsonResponse({'success': False})
  
def check_in(request):
  if request.user.is_authenticated and request.user.profile.photo:
    title = 'Check In'
    date = now_local.date()
    try:
      attendance = Attendance.objects.get(user=request.user, date=date)
    except Attendance.DoesNotExist:
      attendance = None
    if not attendance:
      if is_ajax(request):
        photo = request.POST.get('photo')
        _, str_img = photo.split(';base64')
        decoded_file = base64.b64decode(str_img)
        img = Image.open(BytesIO(decoded_file))
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        res = classify_face(img_io, username=request.user.username)
        if res == request.user.username:
          check_in_time = now_local.time()
          user = get_object_or_404(User, username=res)
          Attendance.objects.create(user=user, date=date, check_in_time=check_in_time)      
          messages.success(request, 'Check in thành công')
          return JsonResponse({'success': True, 'redirect_url': '/account/'})
        return JsonResponse({'success': False})
      return render(request, 'pages/check_in.html', {'title': title, 'date': date})
    else:
      return redirect('check-out')
  else:
    return redirect('login-default')
  
def check_out(request):
  if request.user.is_authenticated and request.user.profile.photo:
    title = 'Check Out'
    date = now_local.date()
    try:
      attendance = Attendance.objects.get(user=request.user, date=date)
    except Attendance.DoesNotExist:
      attendance = None
    if attendance and not attendance.check_out_time:
      check_in_datetime = datetime.combine(date, attendance.check_in_time)
      check_in_datetime = pytz.timezone('Asia/Ho_Chi_Minh').localize(check_in_datetime).replace(microsecond=0)
      time_work = now_local - check_in_datetime
      if is_ajax(request):
        photo = request.POST.get('photo')
        _, str_img = photo.split(';base64')
        decoded_file = base64.b64decode(str_img)
        img = Image.open(BytesIO(decoded_file))
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        res = classify_face(img_io, username=request.user.username)
        if res == request.user.username:
          check_out_time = now_local.time()
          attendance.check_out_time = check_out_time 
          attendance.save()    
          messages.success(request, 'Check out thành công')
          return JsonResponse({'success': True, 'redirect_url': '/account/'})
        return JsonResponse({'success': False})
      return render(request, 'pages/check_out.html', {'title': title, 'date':date, 'time': time_work})
    elif attendance and attendance.check_out_time:
      messages.warning(request, 'Bựa ni check out rồi, đừng có phá web')
      return redirect('account')
    else:
      messages.warning(request, 'Chưa đi làm mà đạ muốn nghỉ')
      return redirect('account')
  else:
    return redirect('login-default')
  
def time_sheet(request):
  if request.user.is_superuser:
    title = 'Bảng Chấm Công'
    attendances = Attendance.objects.all().order_by('-date')
    shift = request.GET.get('shift', '')
    status = request.GET.get('status', '')
    start_date = request.GET.get('start-date', '')
    end_date = request.GET.get('end-date','')
    if start_date and end_date:
      attendances = attendances.filter(date__range=[start_date, end_date])
    elif start_date:
      attendances = attendances.filter(date__range=[start_date, now_local.date()])
    elif end_date:
      attendances = attendances.filter(date__range=[attendances.earliest('date').date, now_local.date()])
    else:
      attendances = attendances
    if shift:
      attendances = attendances.filter(shift__name=shift)
    if status:
      attendances = attendances.filter(status=status)
    paginator = Paginator(attendances, 1)
    page_number = request.GET.get('page')
    try:
      page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
      page_obj = paginator.page(1)
    except EmptyPage:
      page_obj = paginator.page(paginator.num_pages)
    query_params = request.GET.copy()
    if 'page' in query_params:
      query_params.pop('page')
    return render(request, 'pages/time_sheet.html', {'title': title, 'page_obj': page_obj, 'start_date': start_date, 'end_date': end_date, 'shift': shift, 'status': status, 'query_params': query_params.urlencode()})
  else:
    return redirect('home')

def time_sheet_emp(request, str):
  if request.user.is_authenticated:
    title = f'Bảng Chấm Công {request.user.username}'
    attendances = Attendance.objects.filter(user__id=str).order_by('-date')
    if int(str) != request.user.id:
      return redirect('account')
    shift = request.GET.get('shift', '')
    status = request.GET.get('status', '')
    start_date = request.GET.get('start-date', '')
    end_date = request.GET.get('end-date','')
    if start_date and end_date:
      attendances = attendances.filter(date__range=[start_date, end_date])
    elif start_date:
      attendances = attendances.filter(date__range=[start_date, now_local.date()])
    elif end_date:
      attendances = attendances.filter(date__range=[attendances.earliest('date').date, now_local.date()])
    else:
      attendances = attendances
    if shift:
      attendances = attendances.filter(shift__name=shift)
    if status:
      attendances = attendances.filter(status=status)
    paginator = Paginator(attendances, 1)
    page_number = request.GET.get('page')
    try:
      page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
      page_obj = paginator.page(1)
    except EmptyPage:
      page_obj = paginator.page(paginator.num_pages)
    query_params = request.GET.copy()
    if 'page' in query_params:
      query_params.pop('page')
    return render(request, 'pages/time_sheet.html', {'title': title, 'page_obj': page_obj, 'start_date': start_date, 'end_date': end_date, 'shift': shift, 'status': status, 'query_params': query_params.urlencode()})
  else:
    return redirect('home')
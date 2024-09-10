from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  photo = models.ImageField(blank=True, upload_to='photos')
  phone_number = models.CharField(max_length=20, blank=True)
  dob = models.DateField(blank=True, null=True)
  position = models.CharField(max_length=25, choices=[('Trưởng Phòng', 'Trưởng Phòng'), ('Tổ Trưởng', 'Tổ Trưởng'), ('Nhân Viên', 'Nhân Viên')], default='Nhân Viên')
  start_date = models.DateField(blank=True, null=True)
  end_date = models.DateField(blank=True, null=True)
  created_date = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return f"Hồ sơ của {self.user.username}"
  
  
class Shift(models.Model):
  name = models.CharField(max_length=50)
  start_time = models.TimeField()
  end_time = models.TimeField()
  
  def __str__(self):
    return f"{self.name}"
  
  def is_within_shift(self, time):
    return self.start_time <= time <= self.end_time

  def is_before_shift(self, time):
    return time < self.start_time

  def is_after_shift(self, time):
    return time > self.end_time

class Attendance(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  date = models.DateField(default=timezone.now)
  check_in_time = models.TimeField(null=True, blank=True)
  check_out_time = models.TimeField(null=True, blank=True)
  shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True)
  status = models.CharField(max_length=20, choices=[('Đúng Giờ', 'Đúng Giờ'), ('Muộn', 'Muộn')], default='Đúng Giờ')
  total_hours = models.DecimalField(max_digits=5, decimal_places=0, blank=True, null=True)
  salary = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)

  def __str__(self):
    return f"{self.user.username} - {self.date}"

  def is_late(self):
    if self.check_in_time and self.shift:
      return self.check_in_time > self.shift.start_time
    return False
      
  def calculate_salary(self):
    profile = Profile.objects.get(user=self.user)
    if profile.position == 'Tổ Trưởng':
      rate = 1.5 * 30000
    elif profile.position == 'Trưởng Phòng':
      rate = 2 * 30000
    else:
      rate = 30000

    if self.total_hours is not None:
      self.salary = rate * self.total_hours
    else:
      self.salary = 0

  def save(self, *args, **kwargs):
    if self.check_in_time and self.check_out_time:
      check_in = timezone.datetime.combine(self.date, self.check_in_time)
      check_out = timezone.datetime.combine(self.date, self.check_out_time)
      self.total_hours = (check_out - check_in).seconds / 3600 

      potential_shifts = Shift.objects.all()
      if self.total_hours <= 8:
        shift_check_in = next((shift for shift in potential_shifts if shift.is_within_shift(self.check_in_time)), None)
        shift_check_out = next((shift for shift in potential_shifts if shift.is_within_shift(self.check_out_time)), None)
        if not shift_check_in:
          self.shift = shift_check_out
        if shift_check_out == shift_check_in:
          self.shift = shift_check_in
        if shift_check_out != shift_check_in:
          check_in_to_start = timezone.datetime.combine(self.date, shift_check_out.start_time) - check_in
          check_out_to_start = check_out - timezone.datetime.combine(self.date, shift_check_out.start_time)
                  # So sánh và chọn ca
          if check_out_to_start >= check_in_to_start:
            self.shift = shift_check_out
          else:
            self.shift = shift_check_in
      else:
        shift_check_in = next((shift for shift in potential_shifts if shift.is_within_shift(self.check_in_time)), None)
        shift_check_out = next((shift for shift in potential_shifts if shift.is_within_shift(self.check_out_time)), None)
        if not shift_check_in:
          self.shift = next(shift for shift in potential_shifts if shift != shift_check_out)
        else:
          check_in_to_start = timezone.datetime.combine(self.date, shift_check_out.start_time) - check_in
          check_out_to_start = check_out - timezone.datetime.combine(self.date, shift_check_out.start_time)
          if check_out_to_start >= check_in_to_start:
            self.shift = shift_check_out
          else:
            self.shift = shift_check_in
                  
                  
      if self.is_late():
        self.status = 'Muộn'
      else:
        self.status = 'Đúng Giờ'

    self.calculate_salary()
    super().save(*args, **kwargs)



  
  
class Leave(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  start_date = models.DateField()
  end_date = models.DateField()
  reason = models.TextField()
  status = models.CharField(max_length=20, choices=[('Chờ Duyệt', 'Chờ Duyệt'), ('Đã Chấp Nhận', 'Đã Chấp Nhận'), ('Đã Từ Chối', 'Đã Từ Chối')], default='Chờ Duyệt')
  
  def __str__(self):
    return f"{self.user.username} - {self.start_date} to {self.end_date} ({self.status})"
  

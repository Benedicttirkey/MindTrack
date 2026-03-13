# # Create your views here.

from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from .models import User  # 引入 User 模型
from django.http.response import JsonResponse
from .models import DailyRecord, ExerciseRecord, MoodRecord, SleepRecord, WorkStudyRecord
from django.core.mail import send_mail
from django.utils.dateparse import parse_date, parse_datetime
import random
import datetime
from datetime import timedelta
from django.db.models import Avg, Sum
from django.utils import timezone

def main(request):
    return render(request, 'register.html')


def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email_code = request.POST.get('email_code')

        # 获取session中保存的 邮箱 和 验证码 Retrieve the email and verification code that are saved in the session.
        session_email = request.session.get('email')
        session_email_code = request.session.get('email_code')
        code_expiry = request.session.get('code_expiry')

        # 验证验证码是否还有效 Verify whether the verification code is still valid
        t = code_expiry - datetime.datetime.now().timestamp()
        if t < 0:
            return JsonResponse({'code': 201, 'msg': 'The verification code has expired.'})
        if email != session_email or email_code != session_email_code:
            return JsonResponse({'code': 201, 'msg': 'Verification code error'})

        # 检查密码和确认密码是否一致 Check if the password and the confirmation password are the same.
        if password != password2:
            err_msg = "The passwords were inconsistent twice."
            return render(request, 'register.html', {'err_msg': err_msg})

        # 检查用户名是否已存在 Check whether the username already exists
        if User.objects.filter(email=email).exists():
            err_msg = "This email address has been registered."
            return render(request, 'register.html', {'err_msg': err_msg})

        # 保存用户信息 Check whether the username already exists
        new_user = User.objects.create(email=email)
        new_user.set_password(password)

        return redirect('login')
    else:
        return render(request, 'register.html')



# 验证码 Verification code
def send_email_captcha(request):
    email = request.GET.get('email')
    if not email:
        return JsonResponse({"code": 201, "msg": 'The email address must be provided.'})

    # 检测之前是否有获取过验证码, 为了防止用户重复获取验证码, 这里设置两次间隔不能超过20秒
    #Check if the user has previously obtained the verification code. To prevent the user from repeatedly obtaining the verification code, a two-time interval of no more than 20 seconds is set here.
    code_expiry = request.session.get('code_expiry')
    if code_expiry:
        # 验证验证码有效期, 两次发送间隔 需要20秒时间 Verify the validity period of the verification code and the time interval between two sends requires 20 seconds.
        t = code_expiry - datetime.datetime.now().timestamp()
        if t > (300 - 20):
            return JsonResponse({'code': 201, 'msg': 'You can resend after a 20-second interval.'})

    # 生成验证码（取随机的4位数字） Generate a verification code (select a random 4-digit number)
    captcha = "".join(random.sample("0123456789", 4))
    try:
        send_mail(subject="MindTrack", message=f"Your registration verification code is:{captcha}", recipient_list=[email],
                  from_email=None)
    except Exception as e:
        return JsonResponse({'code': 201, 'msg': 'The sending failed. Please check if your email is functioning properly.'})

    # 将邮箱和验证码保存到 session, 等下进行验证 Save the email address and verification code to the session, and we will proceed with the verification later.
    request.session['email'] = email
    request.session['email_code'] = captcha
    request.session['code_expiry'] = int(
        (datetime.datetime.now() + datetime.timedelta(seconds=300)).timestamp())  # 设置 code 的有效期为300秒 Set the validity period of the code to 300 seconds.

    request.session.set_expiry(300)  # 设置 session 有效期 Set the expiration time of the session

    return JsonResponse({"code": 200, "msg": "Email verification code sent successfully "})



# 登录功能 login
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email, password)
        user = User.objects.filter(email=email).first()
        if not user:
            return render(request, 'login.html', {'err_msg': 'The email address does not exist.'})
        if not user.check_password(password):
            return render(request, 'login.html', {'err_msg': 'Password incorrect'})

        # 登录成功，存储用户信息到 session Login successful. Store user information in the session.
        request.session['user_name'] = user.email
        request.session['user_id'] = user.user_id
        return redirect('home')

    else:
        # return render(request, 'index.html')
        print("Login page")
        return render(request, 'login.html')


def logout(request):
    request.session.flush()
    return redirect('login')




# 主页视图 Homepage, the first page accessed after successful login
def home(request):
    if 'user_name' not in request.session:
        return redirect('/')  # 如果没有登录，跳转到登录页面 If not logged in, redirect to the login page.

    user_name = request.session['user_name']
    return render(request, 'home.html', {'user_name': user_name})





#个人中心 personal center
#进入个人中心，用户可以看到user_id，修改 username / age / gender / sleep_preference（还没进行测试，不知道这个功能能不能正常运行）
#Enter the personal center, and users can view the user_id, and modify the username / age / gender / sleep_preference (not yet tested)
def profile(request):
    # 必须先登录 You must log in first.
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.filter(user_id=user_id).first()
    if not user:
        # session 里有 user_id 但数据库没这个人（极少见） In the session, there is a user_id, but the database does not have this person (this is extremely rare).
        request.session.flush()
        return redirect('login')

    if request.method == 'POST':
        # 取用户填写的资料（注册后再补） Retrieve the information filled out by the user (fill it in again after registration)
        user.username = request.POST.get('username') or None

        age_str = request.POST.get('age')
        if age_str:
            try:
                user.age = int(age_str)
            except ValueError:
                return render(request, 'profile.html', {'user': user, 'err_msg': 'The age must be a number.'})
        else:
            user.age = None

        user.gender = request.POST.get('gender') or None
        user.sleep_preference = request.POST.get('sleep_preference') or None

        user.save()
        return render(request, 'profile.html', {'user': user, 'ok_msg': 'Saved successfully'})

    return render(request, 'profile.html', {'user': user})





def _get_logged_in_user(request):
    if "user_name" not in request.session:
        return None

    user_id = request.session.get('user_id')
    user = User.objects.filter(user_id=user_id).first()
    if not user:
        request.session.flush()
    return user


def _selected_record_date(request):
    raw_date = request.POST.get('record_date') or request.GET.get('record_date') or ''
    return parse_date(raw_date) if raw_date else datetime.date.today()


def _get_existing_records(user, record_date):
    daily_record_obj = DailyRecord.objects.filter(user=user, record_date=record_date).first()
    return {
        'daily_record': daily_record_obj,
        'mood': MoodRecord.objects.filter(daily_record=daily_record_obj).first() if daily_record_obj else None,
        'sleep': SleepRecord.objects.filter(daily_record=daily_record_obj).first() if daily_record_obj else None,
        'exercise': ExerciseRecord.objects.filter(daily_record=daily_record_obj).first() if daily_record_obj else None,
        'workstudy': WorkStudyRecord.objects.filter(daily_record=daily_record_obj).first() if daily_record_obj else None,
    }


# daily record hub page
def daily_record(request):
    user = _get_logged_in_user(request)
    if not user:
        return redirect('login')

    record_date = _selected_record_date(request)
    return render(
        request,
        "daily_record.html",
        {'record_date': record_date.isoformat()}
    )


def mood_record(request):
    user = _get_logged_in_user(request)
    if not user:
        return redirect('login')

    record_date = _selected_record_date(request)
    existing = _get_existing_records(user, record_date)
    mood = existing['mood']
    context = {
        'record_date': record_date.isoformat(),
        'mood_rating': mood.mood_rating if mood else 3,
        'stress_rating': mood.stress_rating if mood else 3,
        'anxiety_rating': mood.anxiety_rating if mood else 3,
        'note_text': mood.note_text if mood else '',
    }

    if request.method == 'POST':
        daily_record_obj, _ = DailyRecord.objects.get_or_create(user=user, record_date=record_date)
        MoodRecord.objects.update_or_create(
            daily_record=daily_record_obj,
            defaults={
                'mood_rating': int(request.POST.get('mood_rating', 3)),
                'stress_rating': int(request.POST.get('stress_rating', 3)),
                'anxiety_rating': int(request.POST.get('anxiety_rating', 3)),
                'note_text': (request.POST.get('note_text') or '').strip() or None,
            }
        )
        context.update({
            'mood_rating': int(request.POST.get('mood_rating', 3)),
            'stress_rating': int(request.POST.get('stress_rating', 3)),
            'anxiety_rating': int(request.POST.get('anxiety_rating', 3)),
            'note_text': (request.POST.get('note_text') or '').strip(),
            'ok_msg': 'Mood record saved successfully.',
        })

    return render(request, "mood_record.html", context)


def lifestyle_record(request):
    user = _get_logged_in_user(request)
    if not user:
        return redirect('login')

    record_date = _selected_record_date(request)
    existing = _get_existing_records(user, record_date)
    sleep = existing['sleep']
    exercise = existing['exercise']
    workstudy = existing['workstudy']
    context = {
        'record_date': record_date.isoformat(),
        'sleep_time': sleep.sleep_time.strftime('%Y-%m-%dT%H:%M') if sleep and sleep.sleep_time else '',
        'wake_time': sleep.wake_time.strftime('%Y-%m-%dT%H:%M') if sleep and sleep.wake_time else '',
        'sleep_duration': sleep.sleep_duration if sleep and sleep.sleep_duration is not None else '',
        'did_exercise': exercise.did_exercise if exercise else False,
        'exercise_type': exercise.exercise_type if exercise and exercise.exercise_type else '',
        'exercise_duration': exercise.exercise_duration if exercise and exercise.exercise_duration is not None else '',
        'workstudy_hours': workstudy.workstudy_hours if workstudy else '',
    }

    if request.method == 'POST':
        daily_record_obj, _ = DailyRecord.objects.get_or_create(user=user, record_date=record_date)

        sleep_time_raw = request.POST.get('sleep_time') or ''
        wake_time_raw = request.POST.get('wake_time') or ''
        sleep_duration_raw = request.POST.get('sleep_duration') or ''
        sleep_time = parse_datetime(sleep_time_raw) if sleep_time_raw else None
        wake_time = parse_datetime(wake_time_raw) if wake_time_raw else None
        sleep_duration = int(sleep_duration_raw) if sleep_duration_raw else None

        if sleep_time and wake_time and sleep_duration is None:
            # sleep_duration = max(int((wake_time - sleep_time).total_seconds() // 60), 0)
            sleep_duration = round(max((wake_time - sleep_time).total_seconds() / 3600, 0), 2)

        if sleep_time:
            SleepRecord.objects.update_or_create(
                daily_record=daily_record_obj,
                defaults={
                    'status': 'complete' if wake_time else 'open',
                    'sleep_time': sleep_time,
                    'wake_time': wake_time,
                    'sleep_duration': sleep_duration,
                }
            )

        did_exercise = request.POST.get('did_exercise') == 'on'
        exercise_type = (request.POST.get('exercise_type') or '').strip()
        exercise_duration_raw = request.POST.get('exercise_duration') or ''
        exercise_duration = int(exercise_duration_raw) if exercise_duration_raw else None

        ExerciseRecord.objects.update_or_create(
            daily_record=daily_record_obj,
            defaults={
                'did_exercise': did_exercise,
                'exercise_type': exercise_type or None,
                'exercise_duration': exercise_duration,
            }
        )

        workstudy_hours_raw = request.POST.get('workstudy_hours') or ''
        try:
            workstudy_hours = Decimal(workstudy_hours_raw) if workstudy_hours_raw else Decimal('0.00')
        except InvalidOperation:
            context['err_msg'] = 'Work / study duration must be a valid number.'
            return render(request, "lifestyle_record.html", context)

        WorkStudyRecord.objects.update_or_create(
            daily_record=daily_record_obj,
            defaults={'workstudy_hours': workstudy_hours}
        )

        context.update({
            'sleep_time': sleep_time_raw,
            'wake_time': wake_time_raw,
            'sleep_duration': sleep_duration if sleep_duration is not None else '',
            'did_exercise': did_exercise,
            'exercise_type': exercise_type,
            'exercise_duration': exercise_duration if exercise_duration is not None else '',
            'workstudy_hours': workstudy_hours,
            'ok_msg': 'Lifestyle record saved successfully.',
        })

    return render(request, "lifestyle_record.html", context)


# data visualizations page
def data_visualizations(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = User.objects.filter(user_id=user_id).first()
    if not user:
        request.session.flush()
        return redirect('login')

    end_date = timezone.localdate()
    start_date = end_date - timedelta(days=6)
    date_list = [start_date + timedelta(days=i) for i in range(7)]
    labels = [d.strftime('%a') for d in date_list]

    mood_rows = MoodRecord.objects.filter(
        daily_record__user=user,
        daily_record__record_date__range=[start_date, end_date],
    ).select_related('daily_record')
    mood_map = {row.daily_record.record_date: row for row in mood_rows}

    sleep_rows = SleepRecord.objects.filter(
        daily_record__user=user,
        daily_record__record_date__range=[start_date, end_date],
        status='complete',
    ).select_related('daily_record')
    sleep_map = {row.daily_record.record_date: row for row in sleep_rows}

    exercise_rows = ExerciseRecord.objects.filter(
        daily_record__user=user,
        daily_record__record_date__range=[start_date, end_date],
    ).select_related('daily_record')
    exercise_map = {row.daily_record.record_date: row for row in exercise_rows}

    study_rows = WorkStudyRecord.objects.filter(
        daily_record__user=user,
        daily_record__record_date__range=[start_date, end_date],
    ).select_related('daily_record')
    study_map = {row.daily_record.record_date: row for row in study_rows}

    mood_data = []
    stress_data = []
    anxiety_data = []
    sleep_data = []
    exercise_data = []
    study_data = []

    for current_date in date_list:
        mood_row = mood_map.get(current_date)
        sleep_row = sleep_map.get(current_date)
        exercise_row = exercise_map.get(current_date)
        study_row = study_map.get(current_date)

        mood_data.append(mood_row.mood_rating if mood_row else None)
        stress_data.append(mood_row.stress_rating if mood_row else None)
        anxiety_data.append(mood_row.anxiety_rating if mood_row else None)

        if sleep_row and sleep_row.sleep_duration is not None:
            sleep_data.append(round(float(sleep_row.sleep_duration), 1))
        else:
            sleep_data.append(None)

        if exercise_row:
            if exercise_row.did_exercise:
                exercise_data.append(exercise_row.exercise_duration or 0)
            else:
                exercise_data.append(0)
        else:
            exercise_data.append(None)

        study_data.append(float(study_row.workstudy_hours) if study_row else None)

    avg_mood = mood_rows.aggregate(v=Avg('mood_rating'))['v']
    avg_sleep_hours = sleep_rows.filter(sleep_duration__isnull=False).aggregate(v=Avg('sleep_duration'))['v']
    total_study = study_rows.aggregate(v=Sum('workstudy_hours'))['v']
    exercise_days = exercise_rows.filter(did_exercise=True).count()

    context = {
        'week_labels': labels,
        'mood_data': mood_data,
        'stress_data': stress_data,
        'anxiety_data': anxiety_data,
        'sleep_data': sleep_data,
        'exercise_data': exercise_data,
        'study_data': study_data,
        'avg_mood': round(float(avg_mood), 1) if avg_mood is not None else None,
        'avg_sleep': round(float(avg_sleep_hours), 1) if avg_sleep_hours is not None else None,
        'exercise_days': exercise_days,
        'total_study': round(float(total_study), 1) if total_study is not None else 0,
    }
    return render(request, 'data_visualizations.html', context)
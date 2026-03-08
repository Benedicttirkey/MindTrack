# # Create your views here.

from django.shortcuts import render, redirect
from .models import User  # 引入 User 模型
from django.http.response import JsonResponse
import random, datetime
from django.core.mail import send_mail

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

        return redirect('/login/')
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
        return redirect('/home/')

    else:
        # return render(request, 'index.html')
        print("Login page")
        return render(request, 'login.html')


def logout(request):
    request.session.flush()
    return redirect('/login/')




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
        return redirect('/login/')

    user = User.objects.filter(user_id=user_id).first()
    if not user:
        # session 里有 user_id 但数据库没这个人（极少见） In the session, there is a user_id, but the database does not have this person (this is extremely rare).
        request.session.flush()
        return redirect('/login/')

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





# daily record page
def daily_record(request):
    if "user_name" not in request.session:
        return redirect('/login/')
    return render(request, "daily_record.html")


# data visualizations page
def data_visualizations(request):
    if "user_name" not in request.session:
        return redirect('/login/')
    return render(request, "data_visualizations.html")

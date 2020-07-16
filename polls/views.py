from django.db.models import Avg
from django.shortcuts import render, redirect
from .models import Subject, Teacher, User
from django.http import JsonResponse, HttpResponse, HttpRequest
from .utils import gen_random_code, Captcha, gen_md5_digest
import xlwt
from io import BytesIO
from urllib.parse import quote
import hashlib
# Create your views here.


def show_subjects(request):
    print(request.session)
    subjects = Subject.objects.all().order_by('no')
    return render(request, 'subjects.html', {'subjects': subjects})


def show_teachers(request):
    try:
        sno = int(request.GET.get('sno'))
        teachers = []
        if sno:
            subject = Subject.objects.only('name').get(no=sno)
            teachers = Teacher.objects.filter(subject=subject).order_by('no')
        return render(request, 'teachers.html', {
            'subject': subject,
            'teachers': teachers
        })
    except (ValueError, Subject.DoesNotExist):
        return redirect('/')


def praise_or_criticize(request: HttpRequest) -> HttpResponse:
    if request.session.get('userid'):
        try:
            tno = int(request.GET.get('tno'))
            teacher = Teacher.objects.get(no=tno)
            if request.path.startswith('/praise/'):
                teacher.good_count += 1
                count = teacher.good_count
            else:
                teacher.bad_count += 1
                count = teacher.bad_count
            teacher.save()
            data = {'code': 20000, 'mesg': '投票成功', 'count': count}
        except (ValueError, Teacher.DoesNotExist):
            data = {'code': 20001, 'mesg': '投票失败'}
    else:
        data = {'code': 20002, 'mesg': '请先登录'}
    return JsonResponse(data)


def get_captcha(request: HttpRequest) -> HttpResponse:
    """验证码"""
    captcha_text = gen_random_code()
    request.session['captcha'] = captcha_text
    image_data = Captcha.instance().generate(captcha_text)
    return HttpResponse(image_data, content_type='image/png')


def login(request: HttpRequest) -> HttpResponse:
    hint = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            password = gen_md5_digest(password)
            user = User.objects.filter(username=username, password=password).first()
            if user:
                request.session['userid'] = user.no
                request.session['username'] = user.username
                return redirect('/')
            else:
                hint = '用户名或密码错误'
        else:
            hint = '请输入有效的用户名和密码'
    return render(request, 'login.html', {'hint': hint})


def register(request: HttpRequest) -> HttpResponse:
    hint = '填入注册信息'
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_again = request.POST.get('password_again')
        tel = request.POST.get('tel')
        if all([username, password, password_again, tel]):
            try:
                user = User.objects.get(username=username)
                hint = '此用户名已存在'
                request.session.flush()
            except User.DoesNotExist:
                if password == password_again:
                    md = hashlib.md5()
                    md.update(password.encode('utf-8'))
                    passwd = md.hexdigest()
                    user = User(username=username, password=passwd, tel=tel)
                    user.save()
                    hint = ''
                    return render(request, 'login.html', {'hint': hint})
                else:
                    hint = '两次输入的密码不一致'
        else:
            hint = '请填入全部信息'
    return render(request, 'register.html', {'hint': hint})


def logout(request):
    """注销"""
    request.session.flush()
    return redirect('/')


def export_teachers_excel(request):
    #  制作工作报表
    # 创建工作簿
    wb = xlwt.Workbook()
    # 添加工作表
    sheet = wb.add_sheet('老师信息表')
    # 查询所有老师的信息
    queryset = Teacher.objects.all().select_related('subject')
    # 向Excel表单中写入表头
    colnames = ('姓名', '介绍', '好评数', '差评数', '学科')
    for index, name in enumerate(colnames):
        sheet.write(0, index, name)
    # 向单元格中写入老师的数据
    props = ('name', 'intro', 'good_count', 'bad_count', 'subject')
    for row, teacher in enumerate(queryset):
        for col, prop in enumerate(props):
            value = getattr(teacher, prop, '')
            if isinstance(value, Subject):
                value = value.name
            sheet.write(row + 1, col, value)
    # 保存Excel
    buffer = BytesIO()
    wb.save(buffer)
    # 将二进制数据写入响应的消息体中并设置MIME类型
    resp = HttpResponse(buffer.getvalue(), content_type='text/csv')
    # 中文文件名需要处理成百分号编码
    filename = quote('老师.xls')
    # 通过响应头告知浏览器下载该文件以及对应的文件名
    resp['Content-Disposition'] = 'attachment; filename={}'.format(filename)
    return resp


def get_teachers_data(request):
    # 生成前端图表
    queryset = Teacher.objects.all().only('name', 'good_count', 'bad_count')
    # 查询平均数
    queryset1 = Teacher.objects.values('subject__name').annotate(good=Avg('good_count'), bad=Avg('bad_count'))
    for key, value in enumerate(queryset1):
        print(str(key) + ':' + str(value))
    names = [teacher.name for teacher in queryset]
    good_counts = [teacher.good_count for teacher in queryset]
    bad_counts = [teacher.bad_count for teacher in queryset]
    return JsonResponse({'names': names, 'good': good_counts, 'bad': bad_counts})


def teacher_data_show(request):
    # 返回显示数据的模板
    return render(request, 'teacher_data.html',)


def show_subjects_api(request):
    # 前后端分离，编写数据接口来传递json数据。
    queryset = Subject.objects.all()
    subjects = []
    for subject in queryset:
        subjects.append({
            'no': subject.no,
            'name': subject.name,
            'intro': subject.intro,
            'isHot': subject.is_hot
        })
    return JsonResponse(subjects, safe=False)


def subjects_show(request):
    return render(request, 'subjects_show.html',)


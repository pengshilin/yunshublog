from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required   #引入验证登录的装饰器
from .forms import ProfileForm
from .models import Profile

def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            data = user_login_form.cleaned_data     #cleaned_data 清洗出合法的数据
            #检验账号、密码是否正确匹配数据库中某个用户，如果均匹配则返回这个 user 对象
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                #将用户数据保存在 session 中，即实现了登录动作。session会话控制，存储特定用户会话所需的属性及配置信息
                login(request,user)
                return redirect("article:article_list")
            else:
                return HttpResponse("账号或密码有误，请重新输入")
        else:
            return HttpResponse('账号或密码输入不合法')
    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        context = {'form': user_login_form}
        return render(request, 'userprofile/login.html', context)
    else:
        return HttpResponse('请使用GET或POST请求数据')

def user_logout(request):
    logout(request)
    return redirect("article:article_list")

def user_register(request):
    '''用户注册'''
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save(commit=False)
            new_user.set_password(user_register_form.cleaned_data['password'])   #set_password 对密码字段进行加密
            new_user.save()
            login(request, new_user)
            return redirect('article:article_list')
        else:
            return HttpResponse('注册表单输入有误，请重新输入')
    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        context = {'form': user_register_form}
        return render(request, 'userprofile/register.html', context)
    else:
        return HttpResponse('请使用GET或POST请求数据')

@login_required(login_url='/userprofile/login/')
def user_delete(request, id):
    '''删除用户数据'''
    user = User.objects.get(id=id)
    if request.user == user:
        logout(request)
        user.delete()     #删除用户数据
        return redirect('article:article_list')
    else:
        return HttpResponse("你没有删除操作的权限")

@login_required(login_url='/userprofile/login')
def profile_edit(request, id):
    '''编辑用户信息'''
    user = User.objects.get(id=id)
    # profile = Profile.objects.get(user_id=id)   #user_id是OneToOneField自动生成的字段
    if Profile.objects.filter(user_id=id).exists(): #exists()判断是否存在，存在返回False
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)


    if request.method == 'POST':
        if request.user != user:
            return HttpResponse('你没有权限修改此用户信息')
        #上传的文件保存在 request.FILES 中，通过参数传递给表单类
        profile_form = ProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            #取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd['avatar']
            profile.save()
            return redirect('userprofile:edit', id=id)
        else:
            return HttpResponse('注册表单输入有误，请重新输入')

    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {'profile_form': profile_form, 'profile': profile, 'user': user}
        return render(request, 'userprofile/edit.html', context)
    else:
        return HttpResponse('请使用GET或POST请求数据')
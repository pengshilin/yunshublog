#!/usr/bin/env python 
# -*- coding:utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserLoginForm(forms.Form):    #forms.Form适用于不与数据库进行直接交互的功能
    username = forms.CharField()
    password = forms.CharField()


class UserRegisterForm(forms.ModelForm):    #forms.ModelForm 适用于需要与数据库直接交互的功能
    '''注册用户表单'''
    password = forms.CharField()
    password2 = forms.CharField()   #输入两次密码

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):      #def clean_[字段] 这种写法DJANGO会自动调用对单个字段的数据进行验证清洗
        data = self.cleaned_data    #cleaned_data访问清洗后的数据
        if data.get('password') == data.get('password2'):
            return data.get('password')
        else:
            raise forms.ValidationError("密码输入不一致，请重试")

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone', 'avatar', 'bio')
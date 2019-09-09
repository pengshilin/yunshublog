#!/usr/bin/env python 
# -*- coding:utf-8 -*-
from django import forms
from .models import ArticlePost

class ArticlePostForm(forms.ModelForm):
    class Meta:
        model = ArticlePost     #指明数据模型来源
        fields = ('title', 'body', 'tags', 'avatar')
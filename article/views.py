from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ArticlePost
import markdown
from .forms import ArticlePostForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment
from comment.forms import CommentForm
from .models import ArticleColumn
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import ListView

def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')
    article_list = ArticlePost.objects.all()

    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''

    if column is not None and column.isdigit():     #str.isdigit()检测字符串是只包含数字，是返回True
        article_list = article_list.fliter(column=column)

    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])    #filter(tags__name__in=[tag])在tags字段中过滤name为tag的数据条目，赋值的字符串tag用方括号包起来

    # if order == 'total_views':
    #     article_list = article_list.order_by('-total_views')
    #     if order == 'total_views':
    #         #用Q对象，进行联合搜索
    #         article_list = ArticlePost.objects.filter(
    #             Q(title__icontains=search)|
    #             Q(body__icontains=search)
    #         ).order_by('-total_views')
    #     else:
    #         article_list = ArticlePost.objects.filter(
    #             Q(title__icontains=search)|
    #             Q(body__icontains=search)
    #         )
    # else:
    #     search = ''
    #     if order == 'total_views':
    #         article_list = ArticlePost.objects.all().order_by('-total_views')
    #     else:
    #         article_list = ArticlePost.objects.all()

    paginator = Paginator(article_list, 3)  #每页显示3篇文章
    page = request.GET.get('page')  #在GET请求中，在url的末尾附上?key=value的键值对，视图中就可以通过request.GET.get('key)来查询value的值
    articles = paginator.get_page(page)
    context = {'articles': articles, 'order': order, 'search': search, 'column': column, 'tag': tag,}
    return render(request, 'article/list.html', context)

def article_detail(request, id):
    '''文章详情页'''
    # article = ArticlePost.objects.get(id=id)
    article = get_object_or_404(ArticlePost, id=id)
    comments = Comment.objects.filter(article=id)
    article.total_views += 1
    article.save(update_fields=['total_views']) #update_fields=[]指定了数据库只更新tatal_views字段，优化执行效率
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',   #包含 缩写、表格等常用扩展
            'markdown.extensions.codehilite',  #语法高亮扩展
            'markdown.extensions.toc',  #目录扩展
        ])
    article.body = md.convert(article.body)
    comment_form = CommentForm()
    #过滤出所有的id比当前文章小的文章
    pre_article = ArticlePost.objects.filter(id__lt=article.id).order_by('-id') #lt过滤出所有id比当前文章小的文章
    #过滤出id大的文章
    next_article = ArticlePost.objects.filter(id__gt=article.id).order_by('id') #gt过滤出id大的
    if pre_article.count() > 0:   #取出上一篇
        pre_article = pre_article[0]
    else:
        pre_article = None

    if next_article.count() > 0:  #取出下一篇
        next_article = next_article[0]
    else:
        next_article = None
    context = {"article": article, 'toc': md.toc, 'comments': comments, 'comment_form': comment_form,
               'pre_article': pre_article, 'next_article': next_article,}
    return render(request, 'article/detail.html', context)

@login_required(login_url='account_login')
def article_create(request):
    '''写文章'''
    if request.method == "POST":
        article_post_form = ArticlePostForm(request.POST, request.FILES)    #request.FILES绑定表单，否则图片无法正确保存
        if article_post_form.is_valid():    #判断提交的数据是否满足模型的要求
            new_article = article_post_form.save(commit=False)  #保存数据，但暂时不保存到数据库
            new_article.author = User.objects.get(id=request.user.id)
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()
            article_post_form.save_m2m()    #保存tags 的多对多关系
            return redirect("article:article_list")     #完成后重定向到文章列表
        else:
            return HttpResponse('表单内容有误，请重新填写')
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {'article_post_form': article_post_form, 'columns': columns}
        return render(request, 'article/create.html',context)

@login_required(login_url='account_login')
def article_delete(request, id):
    article = ArticlePost.objects.get(id=id)
    if article.author == User.objects.get(id=request.user.id):
        article.delete()
        return redirect('article:article_list')
    else:
        HttpResponse('你没有权限删除')

@login_required(login_url='account_login')
def article_update(request, id):
    article = ArticlePost.objects.get(id=id)
    if article.author == User.objects.get(id=request.user.id):
        if request.method == 'POST':
            article_post_form = ArticlePostForm(data=request.POST)
            if article_post_form.is_valid():
                article.title = request.POST['title']
                article.body = request.POST['body']
                if request.POST['column'] != 'none':
                    article.column = ArticleColumn.objects.get(id=request.POST['column'])
                else:
                    article.column = None
                if request.FILES.get('avatar'):
                    article.avatar = request.FILES.get('avatar')
                article.tags.set(*request.POST.get('tags').split(','), clear=True)  #split()分割字符串
                article.save()
                return redirect('article:article_detail', id=id)
            else:
                HttpResponse('表单内容有误，请重新输入')
        else:
            article_post_form = ArticlePostForm()
            columns = ArticleColumn.objects.all()
            context = {'article': article, 'article_post_form': article_post_form,'columns': columns,
                       'tags': ','.join([x for x in article.tags.names()]),}
            return render(request, 'article/update.html', context)
    else:
        HttpResponse('你没有权限修改')



class IncreaseLikesView(View):
    '''类视图：点赞数+1'''
    def post(self, request, *args, **kwargs):
        article = ArticlePost.objects.get(id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from PIL import Image


class ArticleColumn(models.Model):
    '''栏目的Model'''
    title = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class ArticlePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    created = models.DateTimeField(default=timezone.now)    #default=timezone.now指定在创建数据时将默认写入当前时间
    updated = models.DateTimeField(auto_now=True)       #auto_now=True指定每次数据更新时自动写入当前时间
    total_views = models.PositiveIntegerField(default=0)    #浏览量，PositiveIntegerField是用于存储正整数的字段，default=0设定初始值从0开始
    column = models.ForeignKey(     #文章栏目的一对多外键
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )
    tags = TaggableManager(blank=True)
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)
    likes = models.PositiveIntegerField(default=0)  #点赞数统计
    class Meta:     #元数据，指除了字段外的所有内容，如排序方式、数据库表名等，元数据选项能给予极大的帮助
        ordering = ('-created',)    #ordering指定模型返回数据的排列方式,-created表示倒序排列，保证最新的文章在最上方

    def __str__(self):  #调用对象的str()
        return self.title

    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])

    def save(self, *args, **kwargs):    #save()是model内置的方法，他会在model实例每次保存时调用,这里改写他保存时处理图片的逻辑塞进去
        article = super(ArticlePost, self).save(*args, **kwargs)    #条用父类中原有的save()方法

        if self.avatar and not kwargs.get('update_fields'): #统计浏览量用了save(update_fields=['total_views']，这里时为了排除没有标题图的文章和为了统计浏览量调用的save(),避免每次浏览都处理标题图
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)   #调整图片大小
            resized_image.save(self.avatar.path)    #覆盖保存
        return article      #将父类save()返回的结果原封不动的返回去

    def was_created_recently(self):
        #若文章是最新发表的，则返回True
        diff = timezone.now() - self.created
        if diff.days == 0 and diff.seconds >=0 and diff.seconds < 60:
            return True
        else:
            return False

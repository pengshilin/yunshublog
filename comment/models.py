from django.db import models
from article.models import ArticlePost
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from mptt.models import MPTTModel, TreeForeignKey

class Comment(MPTTModel):
    body = RichTextField()
    created = models.DateTimeField(auto_now_add=True)   #auto_now=True 创建及更新时都会更新当前时间，auto_now_add=True,创建时更新为当前时间
    article = models.ForeignKey(
        ArticlePost,
        on_delete=models.CASCADE,
        related_name='comments'     #related_name 定义子表Comment在主表ArticlePost中对应的外键属性comments
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    parent = TreeForeignKey(    #mptt树形结构
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    reply_to = models.ForeignKey(   #记录二级评论回复给谁,null=True是针对数据库的，表示数据库的该字段可以为空。blank=True是针对表单，表示表单此字段可以为空。
        User,
        null=True,
        blank=True,
        on_delete= models.CASCADE,
        related_name= 'replyers'
    )

    # class Meta:
    #     ordering=('created',)
    class MPTTMeta:
        order_insertion_by = ['created']

    def __str__(self):
        return self.body[:20]

from django.test import TestCase
import datetime
from django.utils import timezone
from article.models import ArticlePost
from django.contrib.auth.models import User
from time import sleep
from django.urls import reverse

class ArticlePostModelTests(TestCase):
    def test_was_created_recently_with_future_article(self):
        #若 文章创建时间为未来，返回False
        author = User(username='user', password='test_password')
        author.save()

        future_article = ArticlePost(
            author=author,
            title='test',
            body='test',
            created=timezone.now() + datetime.timedelta(days=30)
        )

        self.assertIs(future_article.was_created_recently(), False)

    def test_was_created_recently_with_seconds_before_article(self):
        #若文章创建时间为1分钟内, 返回True
        author = User(username='user1', password='test_password')
        author.save()
        seconds_before_article = ArticlePost(
            author=author,
            title='test1',
            body='test1',
            created=timezone.now() - datetime.timedelta(seconds=45)
        )
        self.assertIs(seconds_before_article.was_created_recently(), True)

    def test_was_created_recently_with_hours_before_article(self):
        author = User(username='user2', password='test_password')
        author.save()
        seconds_before_article = ArticlePost(
            author=author,
            title='test2',
            body='test2',
            created=timezone.now() - datetime.timedelta(hours=3)
        )
        self.assertIs(seconds_before_article.was_created_recently(), False)

    def test_was_created_recently_with_days_before_article(self):
        author = User(username='user3', password='test_password')
        author.save()
        seconds_before_article = ArticlePost(
            author=author,
            title='test3',
            body='test3',
            created=timezone.now() - datetime.timedelta(days=5)
        )
        self.assertIs(seconds_before_article.was_created_recently(), False)


    class ArticlePostViewTests(TestCase):
        def test_increase_views(self):
            author = User(username='user4', password='test_password')
            author.save()
            article = ArticlePost(
                author=author,
                title='test4',
                body='test4',
            )
            article.save()
            self.assertIs(article.total_views, 0)

            url = reverse('article: article_detail', args=(article.id,))
            response = self.client.get(url)     #TestCase类提供了测试使用的client来模拟用户通过请求和视图层代码的交互

            viewed_article = ArticlePost.objects.get(id=article.id)
            self.assertIs(viewed_article.total_views, 1 )

        def test_increase_views_but_not_change_update_field(self):
            author = User(username='user5', password='test_password')
            author.save()
            article = ArticlePost(
                author=author,
                title='test5',
                body='test5',
            )
            article.save()

            sleep(0.5)

            url = reverse('article:article_detail', args=(article.id,))
            response = self.client.get(url)

            viewed_article = ArticlePost.objects.get(id=article.id)
            self.assertIs(viewed_article.updated - viewed_article.created < timezone.timedelta(seconds=0.1), True)
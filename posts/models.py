from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='Заголовок', max_length=200,
                             help_text='Дайте краткое название группе')
    slug = models.SlugField(verbose_name='Слаг', unique=True,
                            help_text='Укажите ключ адреса страницы группы')
    description = models.TextField(verbose_name='Описание группы',
                                   help_text='Опишите группу')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Здесь напишите текст записи')
    pub_date = models.DateTimeField(verbose_name='date published',
                                    auto_now_add=True,)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group, blank=True, null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Здесь писать комментарий')
    created = models.DateTimeField(verbose_name='date published',
                                   auto_now_add=True,
                                   help_text='Здесь укажите дату публикации')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE, unique=False,
                               related_name='following')

    def __str__(self):
        return f'User:{self.user} following to {self.author}'

# Generated by Django 2.2.6 on 2021-02-20 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_follow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(
                help_text='Укажите ключ адреса страницы группы',
                unique=True, verbose_name='Слаг'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True,
                                       verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Здесь напишите текст записи',
                                   verbose_name='Текст поста'),
        ),
    ]
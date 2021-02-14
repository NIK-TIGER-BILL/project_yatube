from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {
            'group': 'Группа',
            'text': 'Текст записи',
        }
        help_texts = {
            'group': 'При желании выберите группу',
            'text': 'Здесь напишите текст записи',
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Здесь напишите комментарий',
        }

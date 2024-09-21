from django.forms import ModelForm
from .models import Diary, DiaryTemp
from django import forms

class PreviewFileWidght(forms.ClearableFileInput):
    # def render(self, name. val)
    pass

class DiaryForm(ModelForm):
    class Meta:
        model = Diary
        fields = ['diary_img']

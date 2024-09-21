from django.contrib import admin
from .models import Dataset,Diary,DiaryTemp,Emotion_Category,Genre_Category,Movie_Drama_Recommend,Recommend_Youtube
from .models import ModelValidDataset, UserSelectGenreForEmotion
# Register your models here.

admin.site.register(Dataset)
admin.site.register(Diary)
admin.site.register(DiaryTemp)
admin.site.register(Movie_Drama_Recommend)
admin.site.register(Recommend_Youtube)

class Emotion_Category_Admin(admin.ModelAdmin):
    model = Emotion_Category
    prepopulated_fields = {'slug' :   ('name', )}


    
admin.site.register(Emotion_Category, Emotion_Category_Admin)
admin.site.register(Genre_Category)
admin.site.register(ModelValidDataset)
admin.site.register(UserSelectGenreForEmotion)
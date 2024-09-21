from django.db import models
from Account.models import Account
# Create your models here.

#감정 테이블
class Emotion_Category(models.Model):
    name = models.CharField(max_length=10, unique=True)
    slug = models.SlugField(max_length=20, unique=True, allow_unicode=True)
    emotion_image = models.ImageField(upload_to='images/', blank=True, null=True)
    
    #일기를 감정별로 보고싶을 때 사용할듯.
    def get_absolute_url(self):
        return f"/board/list/{self.slug}/"
    
    #캘린더 및 detailView에 감정에 대한 이미지 뿌리기 위한 함수. Diary테이블에서 이것을 사용한다.
    def get_emotion_image(self):
        return self.emotion_image.url
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Emotion_Category"
        
        
#장르 테이블
class Genre_Category(models.Model):
    name = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Genre_Category"
        

#일기 최종 저장
class Diary(models.Model):
    author = models.ForeignKey(Account, null=True, on_delete=models.CASCADE)
    diary_title = models.CharField(max_length=50, null=False)
    diary_img = models.ImageField(upload_to='images/', blank=True, null=True)
    diary_content = models.TextField(null=False)
    angry_percent = models.FloatField(default=0.0) #분노
    terror_percent = models.FloatField(default=0.0) #두려움
    sadness_percent = models.FloatField(default=0.0) #슬픔
    loathing_percent = models.FloatField(default=0.0) #혐오
    shock_percent = models.FloatField(default=0.0) #놀람
    expect_percent = models.FloatField(default=0.0) #기대
    pleasure_percent = models.FloatField(default=0.0) #기쁨
    calmness_percent = models.FloatField(default=0.0) #평온
    main_emotion = models.ForeignKey(Emotion_Category, null=True, on_delete=models.CASCADE)
    user_select_emotion = models.ForeignKey(Emotion_Category, null=True, on_delete=models.CASCADE, related_name="user_select_emotion")
    write_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.author} -- {self.diary_title} -- {self.write_date}"
    
    @property
    def get_html_url(self):
        return f'<a href="/board/calendar_detail/{self.pk}/"><img src="{self.user_select_emotion.get_emotion_image()}" style="height:50px"></img></a>'
    
    def get_details_url(self):
        return f'/board/calendar_details/{self.pk}/'    
    
    @property
    def get_emotion_image(self):
        # url = reverse('cal:index',)
        return self.user_select_emotion.get_emotion_image()
    
    @property    
    def get_list_details(self):
        return f'/board/diary_details/{self.pk}/' 
    
    @property
    def get_main_url(self):
        return f'<a href="/board/"></a>'
    
    
    def get_absolute_url(self):
        return f'/board/diary_detail/{self.pk}/'
    
    class Meta:
        verbose_name_plural = "Diary"
        

#일기 임시저장
class DiaryTemp(models.Model):
    author = models.ForeignKey(Account, null=True, on_delete=models.CASCADE)
    diary_title = models.CharField(max_length=50, null=False)
    diary_img = models.ImageField(upload_to='images/', blank=True)
    diary_content = models.TextField(null=False)
    write_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.author} -- {self.diary_title}"
    
    class Meta:
        verbose_name_plural = "DiaryTemp"

#유튜브 컨텐츠 테이블
class Recommend_Youtube(models.Model):
    title = models.CharField(max_length=200, null=False, default="")
    thumnail = models.CharField(max_length=200, null=False, default="")
    link_url = models.TextField(null=False, default="")
    emotion = models.ForeignKey(Emotion_Category, null=True, on_delete=models.CASCADE)
    goodCount = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.title} -- {self.emotion}"
    
    class Meta:
        verbose_name_plural = "Recommend_Youtube"
        
        
class Movie_Drama_Recommend(models.Model):
    title = models.CharField(max_length=50, null=False, default="")
    thumnail = models.CharField(max_length=200, null=False, default="")
    released_date = models.CharField(max_length=30)
    genre = models.ManyToManyField(Genre_Category, blank=True)
    
    def __str__(self):
        return f"{self.title} -- {self.thumnail}"
    
    class Meta:
        verbose_name_plural = "Movie_Drama_Recommend"
    

class Dataset(models.Model):
    text = models.TextField()
    final_emotion = models.CharField(max_length=10)
    
    def __str__(self):
        return f"DatasetEmotion -- {self.final_emotion}"
    
    class Meta:
        verbose_name_plural = "Dataset"
        
class ModelValidDataset(models.Model):
    model_return_emotion = models.CharField(max_length=10, null=True, default="")
    user_select_emotion = models.CharField(max_length=10, null=True, default="")
    comment = models.TextField()
    
    def __str__(self):
        return f'{self.model_return_emotion} -- {self.user_select_emotion}'
    

class UserSelectGenreForEmotion(models.Model):
    genre = models.ManyToManyField(Genre_Category, blank=True)
    emotion = models.ForeignKey(Emotion_Category, null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.emotion} -- select_genre_list"
    
    class Meta:
        verbose_name_plural = "User_Select_Genre_For_Emotion"
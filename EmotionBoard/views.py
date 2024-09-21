from django.shortcuts import render, redirect
from django.urls import path
from django.views.generic import TemplateView,CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Movie_Drama_Recommend, Genre_Category, Diary, DiaryTemp, Recommend_Youtube, Emotion_Category, ModelValidDataset, Dataset, UserSelectGenreForEmotion
from EmotionBoard.forms import DiaryForm
from datetime import datetime, timedelta, date
from scripts.process import predictSenti
from django.contrib.auth import logout
from django.utils.safestring import mark_safe
from .utils import Calendar
import calendar
from django.core.paginator import Paginator
from dateutil import relativedelta
# Create your views here.

emotion_dict = {
    "angry":['코미디','드라마','애니메이션','음악'],
    "terror":['모험','판타지','SF', '로맨스'],
    "sadness":['코미디','애니메이션','음악'],
    "loathing":['액션','모험','코미디','가족'],
    "shock":['코미디','드라마','애니메이션','음악'],
    "expect":['코미디','로맨스','SF'],
    "pleasure":['모험','드라마','판타지','SF'],
    "calmness":['코미디','가족','음악','애니메이션']
}

emotion_select_dict = {
    "1" : "angry",
    "2" : "terror",
    "3" : "sadness",
    "4" : "loathing",
    "5" : "shock",
    "6" : "expect",
    "7" : "pleasure",
    "8" : "calmness"
}

emotion_to_kor = {
    "angry" : "화남",
    "calmness" : "평온",
    "expect" : "기대",
    "loathing" : "혐오",
    "pleasure" : "기쁨",
    "sadness" : "슬픔",
    "shock" : "놀람",
    "terror" : "두려움",
}

genre_list = ['모험','판타지','애니메이션','드라마','액션','코미디','SF','음악','로맨스','가족','TV 영화']

def genre_recommend(main_emotion):
    emotion_count = {}
    recommend_genre = []
    for i in UserSelectGenreForEmotion.objects.filter(emotion = Emotion_Category.objects.get(name = main_emotion)).all():
        for j in i.genre.all():
            if emotion_count.get(j.name) == None:
                emotion_count[j.name] = 1
            else:
                emotion_count[j.name] += 1

    
    for key, value in sorted(emotion_count.items(), key = lambda item:item[1], reverse=True):
        recommend_genre.append(key)
        if len(recommend_genre) == 3:
            break
    return recommend_genre

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def get_date(req_month):
    if req_month:
        year, month = (int(x) for x in req_month.split('-'))
        return date(year, month, day=1)
    return datetime.today()    
    
class CalendarView(TemplateView):
    model = Diary
    template_name = 'EmotionBoard/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None),)
        cal = Calendar(d.year, d.month, user=self.request.user)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context
    
#캘린더에서 이모티콘 클릭했을 때 나오는 일기 부분
class CalendarDetail(DetailView):
    model = Diary
    template_name ="EmotionBoard/calendar_detail.html"
    
    def get_context_data(self, **kwargs):       
        context = super(CalendarDetail,self).get_context_data()
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month, user=self.request.user)
        html_cal = cal.formatmonth(withyear=True)
        
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        
        return context

#캘린더에서 이모티콘 누르고 그 일기에서 상세 페이지 넘어갈 때 나오는 부분
class CalendarDetails(DetailView):
    model = Diary
    template_name ="EmotionBoard/calendar_details.html"
    
    def get_context_data(self, **kwargs):       
        context = super(CalendarDetails,self).get_context_data()
        print(Diary.objects.get(pk = self.kwargs['pk'])) #이렇게 해서 DetailView에서도 해당 pk값을 이용해 값을 뽑을 수 있음.
        user_select_emotion = Diary.objects.get(pk = self.kwargs['pk']).user_select_emotion
        print(Emotion_Category.objects.get(name = user_select_emotion).pk)
        context["youtube_list"] = Recommend_Youtube.objects.filter(emotion_id = Emotion_Category.objects.get(name = user_select_emotion).pk).order_by("?")[:10]
        print(context["youtube_list"])
        context['data'] = ['angry', 'calmness', 'expect', 'loathing', 'pleasure', 'sadness', 'shock', 'terror']

        return context
    

def calendar_list_detail(request, pk):
    print(pk)
    context = None
    main_emotion = Diary.objects.get(pk = pk).user_select_emotion.name
    data = ['angry', 'calmness', 'expect', 'loathing', 'pleasure', 'sadness', 'shock', 'terror']
    angry_percent = Diary.objects.get(pk=pk).angry_percent
    calmness_percent = Diary.objects.get(pk=pk).calmness_percent
    expect_percent = Diary.objects.get(pk=pk).expect_percent
    loathing_percent = Diary.objects.get(pk=pk).loathing_percent
    pleasure_percent = Diary.objects.get(pk=pk).pleasure_percent
    sadness_percent = Diary.objects.get(pk=pk).sadness_percent
    shock_percent = Diary.objects.get(pk=pk).shock_percent
    terror_percent = Diary.objects.get(pk=pk).terror_percent
    get_emotion_image = Emotion_Category.objects.get(name = Diary.objects.get(pk=pk).user_select_emotion).emotion_image.url
    youtube_list = Recommend_Youtube.objects.filter(emotion_id = Emotion_Category.objects.get(name = main_emotion).pk).order_by("?")[:10]
    print(main_emotion)
    print(emotion_dict.get(main_emotion))
    print(UserSelectGenreForEmotion.objects.filter(emotion = Emotion_Category.objects.get(name = main_emotion)).all())
    emotion_count = {}
    for i in UserSelectGenreForEmotion.objects.filter(emotion = Emotion_Category.objects.get(name = main_emotion)).all():
        for j in i.genre.all():
            print(j.name)
            if emotion_count.get(j.name) == None:
                emotion_count[j.name] = 1
            else:
                emotion_count[j.name] = emotion_count[j.name]+1
    print(sorted(emotion_count.items(), key = lambda item:item[1], reverse=True))
    recommend_genre = []
    for key, value in sorted(emotion_count.items(), key = lambda item:item[1], reverse=True):
        recommend_genre.append(key)
        if len(recommend_genre) == 3:
            break
    context = {
        "main_emotion" : main_emotion,
        "data" : emotion_to_kor.values(),
        "angry_percent" : angry_percent,
        "calmness_percent": calmness_percent,
        "expect_percent" : expect_percent,
        "loathing_percent" : loathing_percent,
        "pleasure_percent" : pleasure_percent,
        "sadness_percent" : sadness_percent,
        "shock_percent" : shock_percent,
        "terror_percent" : terror_percent,
        "get_emotion_image" : get_emotion_image,
        "youtube_list" : youtube_list,
        "genre_list" : genre_list,
        "movie_genre_list" : genre_recommend(main_emotion)
    }
    if request.method == "POST":
        print("selected : ",request.POST.getlist('selected'))
        genre_select_list = request.POST.getlist('selected')

        
        movie_drama_recommend_list = []
        for i in genre_select_list:
            movie_drama_recommend_list.append(Movie_Drama_Recommend.objects.filter(genre__name__startswith=i).order_by("?")[:5].values())
        context["recomment_list"] = movie_drama_recommend_list
        context["selected_list"] = genre_select_list
    return render(request, "EmotionBoard/diary_details.html", context=context)



class MainView(LoginRequiredMixin, UserPassesTestMixin, CalendarView):
    template_name = 'EmotionBoard/mainPage.html'
    
    def test_func(self):
        print(self.request.user)
        return self.request.user.is_superuser or self.request.user.is_staff or self.request.user.is_authenticated
    
    def get_context_data(self, **kwargs):
        context = super(MainView,self).get_context_data()
        #print(Diary.objects.filter(author = self.request.user).order_by("-write_date","-pk")[0])
        #print(datetime.today().day)
        if Diary.objects.filter(author = self.request.user).count() == 0:
            pass
        elif Diary.objects.filter(author = self.request.user).order_by("-write_date")[0].write_date.day < datetime.today().day:
            print("오늘 일기 없음")
        else:
            context['diary_title'] = Diary.objects.filter(author = self.request.user).order_by("-write_date","-pk")[0].diary_title
            context['diary_image'] = Diary.objects.filter(author = self.request.user).order_by("-write_date","-pk")[0].diary_img
            context['diary_content'] = Diary.objects.filter(author = self.request.user).order_by("-write_date","-pk")[0].diary_content
        return context
        # context['diary'] = Diary.objects.filter(author = self.request.user).filter()
        
        
    
    
    
    # #해당 장르 영화 가져오는 코드
    # def get_context_data(self, **kwargs):
    #     context = super(MainView,self).get_context_data()
    #     context['categories'] = Movie_Drama_Recommend.objects.filter(genre__name__startswith="로맨스")
    #     print(context['categories'])
    #     return context
    

    
def post_diary(request):
    print(f"request : {request.POST}")
    if not request.user.is_authenticated:
        return redirect("/board/")
    else:
        if request.POST:
            
            #일기 임시저장 버튼 눌렀을 시
            if request.method == "POST" and 'diary_temp' in request.POST:
                print(len(DiaryTemp.objects.filter(author = request.user)))
                response = DiaryTemp()
                print(request.FILES.get('image'))
                print(request.POST.get('image_other'))
                if request.FILES.get('image') == None:
                    if request.POST.get("image_other") == None:
                        # diary_img = DiaryTemp.objects.get(author = request.user).diary_img
                        response.diary_img = None
                    else:
                        diary_img = str(request.POST.get("image_other"))
                        find_index = diary_img.find("images")
                        print(find_index)
                        diary_img = diary_img[find_index:]
                        print(diary_img)
                        response.diary_img = diary_img
                        # response.diary_img = str(request.POST.get("image_other")).split("/")[:2]
                    # print(diary_img)
                else:
                    print(request.FILES.get('image'))
                    response.diary_img = request.FILES.get('image')
                if len(DiaryTemp.objects.filter(author = request.user)) > 0 :
                    delete_DB = DiaryTemp.objects.filter(author = request.user)
                    delete_DB.delete()
                response.diary_title = request.POST['title']
                # response.diary_img = request.FILES['image']
                response.diary_content = str(request.POST['content']).strip()
                response.author = request.user
                year = request.POST['current_date'][0:4]
                month = request.POST['current_date'][5:7]
                day = request.POST['current_date'][8:10]
                write_date = datetime(year = int(year), month = int(month), day = int(day))
                response.write_date = write_date
                response.save()
                print("temp")
                return redirect("/board/post_diary")
            
            #일기 불러오기 버튼 눌렀을 시
            elif request.method == "POST" and 'load_diary' in request.POST:
                if DiaryTemp.objects.filter(author = request.user).count() == 0:
                    return render(request, "EmotionBoard/post_diary.html")
                else:
                    get_DB = DiaryTemp.objects.get(author = request.user)
                    diary_img = None
                    print(get_DB.diary_title)
                    if get_DB.diary_img != None:
                        diary_img = get_DB.diary_img
                    # print(get_DB.diary_img)
                    print(get_DB.diary_content)
                    diary_day = []
                    for day in Diary.objects.filter(author = request.user).values("write_date"):
                        # print(diary_day)
                        # print(type(day["write_date"]))
                        if day["write_date"].strftime("%Y-%m-%d") not in diary_day:
                            diary_day.append(day["write_date"].strftime("%Y-%m-%d"))
                            # print("중복안됨")
                        else:
                            pass
                            # print("중복됨")
                            
                    d = get_date(request.GET.get('month', None))
                    cal = Calendar(d.year, d.month, user=request.user)
                    html_cal = cal.formatmonth(withyear=True)
                    context = {
                        "prev_month" : prev_month(d),
                        "next_month" : next_month(d),
                        "calendar" :  mark_safe(html_cal),
                        "diary" : Diary.objects.all(),
                        "diary_title" : get_DB.diary_title,
                        "diary_img" : diary_img,
                        "diary_content" : get_DB.diary_content,
                        "write_date" : get_DB.write_date.strftime("%Y-%m-%d"),
                        "form" : DiaryForm(),
                        "diary_day" : diary_day
                    }
                    return render(request, "EmotionBoard/post_diary_temp.html", context=context)
            
            
            #일기 저장 버튼 클릭 시
            elif request.method == "POST" and 'final_save' in request.POST:
                # main_emotion = Diary.objects.filter(author=request.user).order_by("-write_date")[0].main_emotion.name                
                user_select_emotion = None
                print(request.POST.get('main_emotion'))
                print(request.POST.get('percent'))
                
            
                main_emotion = str(request.POST.get('main_emotion'))
                percent = str(request.POST.get('percent'))
                percent = percent.replace("[","").replace("]","")
                dataset = Dataset()
                print(type(percent))
                print(Diary.objects.filter(author = request.user).filter(write_date__exact=DiaryTemp.objects.get(author = request.user).write_date).count())
                
                if Diary.objects.filter(author = request.user).filter(write_date__exact=DiaryTemp.objects.get(author = request.user).write_date).count()>0:
                    Diary.objects.filter(author = request.user).filter(write_date__exact=DiaryTemp.objects.get(author = request.user).write_date).delete()
                
                if request.POST.get('sort-category') != '0':    
                    diary_response = Diary()
                    diary_response.author = request.user
                    diary_response.diary_title = request.POST['title']
                    if request.FILES.get('image') is None:
                        diary_response.diary_img = DiaryTemp.objects.get(author = request.user).diary_img
                    else:
                        diary_response.diary_img = request.FILES.get('image')
                    diary_response.diary_content = str(DiaryTemp.objects.get(author = request.user).diary_content).strip()
                    diary_response.write_date = DiaryTemp.objects.get(author = request.user).write_date
                    diary_response.angry_percent = float(str(percent).split(",")[0])
                    diary_response.calmness_percent = float(str(percent).split(",")[1])
                    diary_response.expect_percent = float(str(percent).split(",")[2])
                    diary_response.loathing_percent = float(str(percent).split(",")[3])
                    diary_response.pleasure_percent = float(str(percent).split(",")[4])
                    diary_response.sadness_percent = float(str(percent).split(",")[5])
                    diary_response.shock_percent = float(str(percent).split(",")[6])
                    diary_response.terror_percent = float(str(percent).split(",")[7])
                    diary_response.main_emotion = Emotion_Category.objects.get(name = main_emotion)
                    user_select_emotion = emotion_select_dict[request.POST.get('sort-category')]
                    diary_response.user_select_emotion = Emotion_Category.objects.get(name = emotion_select_dict[request.POST.get('sort-category')])
                    print(user_select_emotion)
                    diary_response.save()
                    response = ModelValidDataset(model_return_emotion = main_emotion, user_select_emotion = emotion_select_dict[request.POST.get('sort-category')], comment = request.POST.get('feedback'))
                    response.save()
                    dataset.text = str(DiaryTemp.objects.get(author = request.user).diary_content).strip()
                    dataset.final_emotion = emotion_select_dict[request.POST.get('sort-category')]
                    dataset.save()
                else:
                    diary_response = Diary()
                    diary_response.author = request.user
                    diary_response.diary_title = request.POST['title']
                    if request.FILES.get('image') is None:
                        diary_response.diary_img = DiaryTemp.objects.get(author = request.user).diary_img
                    else:
                        diary_response.diary_img = request.FILES.get('image')
                    diary_response.diary_content = str(DiaryTemp.objects.get(author = request.user).diary_content).strip()
                    diary_response.write_date = DiaryTemp.objects.get(author = request.user).write_date
                    diary_response.angry_percent = float(str(percent).split(",")[0])
                    diary_response.calmness_percent = float(str(percent).split(",")[1])
                    diary_response.expect_percent = float(str(percent).split(",")[2])
                    diary_response.loathing_percent = float(str(percent).split(",")[3])
                    diary_response.pleasure_percent = float(str(percent).split(",")[4])
                    diary_response.sadness_percent = float(str(percent).split(",")[5])
                    diary_response.shock_percent = float(str(percent).split(",")[6])
                    diary_response.terror_percent = float(str(percent).split(",")[7])
                    diary_response.main_emotion = Emotion_Category.objects.get(name = main_emotion)
                    diary_response.user_select_emotion = Emotion_Category.objects.get(name = main_emotion)
                    diary_response.save()
                    response = ModelValidDataset(model_return_emotion = main_emotion, user_select_emotion = Emotion_Category.objects.get(name = main_emotion))
                    response.save()
                    print(Dataset.objects.filter(text__exact = str(DiaryTemp.objects.get(author = request.user).diary_content).strip()).count())
                    if Dataset.objects.filter(text__exact = str(DiaryTemp.objects.get(author = request.user).diary_content).strip()).count()>0:
                        Dataset.objects.filter(text__exact = str(DiaryTemp.objects.get(author = request.user).diary_content).strip()).delete()
                    dataset.text = str(DiaryTemp.objects.get(author = request.user).diary_content).strip()
                    dataset.final_emotion = Emotion_Category.objects.get(name = main_emotion)
                    dataset.save()
                    user_select_emotion = main_emotion

                emotion_count = {}
                print(UserSelectGenreForEmotion.objects.filter(emotion = Emotion_Category.objects.get(name = user_select_emotion)).all())
                for i in UserSelectGenreForEmotion.objects.filter(emotion = Emotion_Category.objects.get(name = user_select_emotion)).all():
                    for j in i.genre.all():
                        print(j.name)
                        if emotion_count.get(j.name) == None:
                            emotion_count[j.name] = 1
                        else:
                            emotion_count[j.name] = emotion_count[j.name]+1
                print(sorted(emotion_count.items(), key = lambda item:item[1], reverse=True))
                recommend_genre = []
                for key, value in sorted(emotion_count.items(), key = lambda item:item[1], reverse=True):
                    recommend_genre.append(key)
                    if len(recommend_genre) == 3:
                        break
                
                # main_emotion_kor[main_emotion]
                context = {
                    "main_emotion":main_emotion,
                    "genre_list": genre_list,
                    "youtube_list" : Recommend_Youtube.objects.filter(emotion_id = Emotion_Category.objects.get(name = user_select_emotion)).order_by("?")[:10],
                    "main_emotion" : emotion_to_kor[Diary.objects.filter(author=request.user).order_by("-write_date")[0].main_emotion.name],
                    "movie_genre_list": recommend_genre,
                    "user_select_emotion" : emotion_to_kor[user_select_emotion],
                    "emotion_image" : Emotion_Category.objects.get(name = user_select_emotion).emotion_image.url
                }
                return render(request, "EmotionBoard/diary_result.html",context=context)
            
            #diary_result에서 드라마 새로고침 눌렀을 시
            elif request.method == "POST" and 'movie_drama_recommend' in request.POST:
                print("체크박스")
                genre_select_list = request.POST.getlist('selected')
                main_emotion = request.POST['main_emotion']
                print(main_emotion)
                print(request.POST.getlist('selected'))
                movie_drama_recommend_list = []
                for i in genre_select_list:
                    movie_drama_recommend_list.append(Movie_Drama_Recommend.objects.filter(genre__name__startswith=i).order_by("?")[:5].values())
                print(movie_drama_recommend_list)
                
                main_emotion = Diary.objects.filter(author=request.user).order_by("-pk")[0].user_select_emotion.name
                user_select_emotion = Diary.objects.filter(author = request.user).order_by("-pk")[0].user_select_emotion.name

                user_select_genre = UserSelectGenreForEmotion.objects.create(emotion = Emotion_Category.objects.get(name = main_emotion))
                if len(genre_select_list) != 0:
                    for i in genre_select_list:
                        user_select_genre.genre.add(Genre_Category.objects.get(name = i))
                    user_select_genre.save()
                
                
                emotion_count = {}
                print(UserSelectGenreForEmotion.objects.filter(emotion = Emotion_Category.objects.get(name = user_select_emotion)).all())
                for i in UserSelectGenreForEmotion.objects.filter(emotion = Emotion_Category.objects.get(name = user_select_emotion)).all():
                    for j in i.genre.all():
                        print(j.name)
                        if emotion_count.get(j.name) == None:
                            emotion_count[j.name] = 1
                        else:
                            emotion_count[j.name] = emotion_count[j.name]+1
                print(sorted(emotion_count.items(), key = lambda item:item[1], reverse=True))
                recommend_genre = []
                for key, value in sorted(emotion_count.items(), key = lambda item:item[1], reverse=True):
                    recommend_genre.append(key)
                    if len(recommend_genre) == 3:
                        break
                
                
                context = {
                    "main_emotion":emotion_to_kor[main_emotion],
                    "genre_list": genre_list,
                    "youtube_list" : Recommend_Youtube.objects.filter(emotion_id = Emotion_Category.objects.get(name = user_select_emotion)).order_by("?")[:10],
                    "movie_genre_list": recommend_genre,
                    "recomment_list" : movie_drama_recommend_list,
                    "selected_list" : genre_select_list,
                    "user_select_emotion" : emotion_to_kor[main_emotion],
                    "data" : Emotion_Category.objects.all(),
                    "emotion_image" : Emotion_Category.objects.get(name = user_select_emotion).emotion_image.url
                }
                return render(request, "EmotionBoard/diary_result.html", context = context)
            
            elif request.method == "POST" and 'reload_recommend_movie_drama' in request.POST:
                print(request.POST)
                print("체크박스")
                genre_select_list = request.POST.getlist('selected')
                main_emotion = request.POST['main_emotion']
                print(main_emotion)
                print(request.POST.getlist('selected'))
                movie_drama_recommend_list = []
                for i in genre_select_list:
                    movie_drama_recommend_list.append(Movie_Drama_Recommend.objects.filter(genre__name__startswith=i).order_by("?")[:5].values())
                print(movie_drama_recommend_list)
                
                main_emotion = Diary.objects.filter(author=request.user).order_by("-pk")[0].user_select_emotion.name
                user_select_emotion = Diary.objects.filter(author = request.user).order_by("-pk")[0].user_select_emotion.name
                
                
                # print(UserSelectGenreForEmotion.objects.filter(emotion = user_select_emotion))
                emotion_count = {}
                print(UserSelectGenreForEmotion.objects.filter(emotion = Emotion_Category.objects.get(name = user_select_emotion)).all())
                for i in UserSelectGenreForEmotion.objects.filter(emotion = Emotion_Category.objects.get(name = user_select_emotion)).all():
                    for j in i.genre.all():
                        print(j.name)
                        if emotion_count.get(j.name) == None:
                            emotion_count[j.name] = 1
                        else:
                            emotion_count[j.name] = emotion_count[j.name]+1
                print(sorted(emotion_count.items(), key = lambda item:item[1], reverse=True))
                recommend_genre = []
                for key, value in sorted(emotion_count.items(), key = lambda item:item[1], reverse=True):
                    recommend_genre.append(key)
                    if len(recommend_genre) == 3:
                        break
                
                context = {
                    "main_emotion":emotion_to_kor[main_emotion],
                    "genre_list": genre_list,
                    "youtube_list" : Recommend_Youtube.objects.filter(emotion_id = Emotion_Category.objects.get(name = user_select_emotion)).order_by("?")[:10],
                    # "movie_genre_list": emotion_dict.get(str(main_emotion)),
                    "movie_genre_list" : recommend_genre,
                    "recomment_list" : movie_drama_recommend_list,
                    "selected_list" : genre_select_list,
                    "user_select_emotion" : emotion_to_kor[main_emotion],
                    "data" : Emotion_Category.objects.all(),
                    "emotion_image" : Emotion_Category.objects.get(name = user_select_emotion).emotion_image.url
                }
                
                
                return render(request, "EmotionBoard/diary_result.html", context=context)
            #일기 작성 완료 버튼 눌렀을 시
            else:
                response = DiaryTemp()
                
                diary_img = str(request.POST.get("image_other"))
                find_index = diary_img.find("images")
                print(find_index)
                diary_img = diary_img[find_index:]
                print(diary_img)
                response.diary_img = diary_img
                
                if request.FILES.get('image') is None:
                    # response.diary_img = DiaryTemp.objects.get(author = request.user).diary_img
                    if request.POST.get("image_other") == None:
                        response.diary_img = None
                    else:
                        diary_img = str(request.POST.get("image_other"))
                        find_index = diary_img.find("images")
                        print(find_index)
                        diary_img = diary_img[find_index:]
                        print(diary_img)
                        response.diary_img = diary_img
                    # if DiaryTemp.objects.get(author = request.user).diary_img.url is not None:
                    #     response.diary_img = DiaryTemp.objects.get(author = request.user).diary_img.url
                    # else:
                    #     response.diary_img = None
                else:
                    response.diary_img = request.FILES.get('image')
                    
                if len(DiaryTemp.objects.filter(author = request.user)) > 0 :
                    delete_DB = DiaryTemp.objects.filter(author = request.user)
                    delete_DB.delete()
                        
                    
                response.diary_title = request.POST['title']
                print(request.FILES.get('image'))

                year = request.POST['current_date'][0:4]
                month = request.POST['current_date'][5:7]
                day = request.POST['current_date'][8:10]
                print(datetime(year = int(year), month = int(month), day = int(day)))
                write_date = datetime(year = int(year), month = int(month), day = int(day))
                response.diary_content = str(request.POST['content']).strip()
                response.author = request.user
                response.write_date = write_date

                senti, percentlist = predictSenti(str(request.POST['content']).strip())
                main = senti[0]
                print(main)
                #sub = senti[1]
                response.save()
                print("submit")
                target = ['angry', 'calmness', 'expect', 'loathing', 'pleasure', 'sadness', 'shock', 'terror']
                
                main_emotion_kor = emotion_to_kor[main]
                context = {
                    "write_date" : write_date.strftime("%Y-%m-%d"),
                    "diary_title":request.POST['title'],
                    "diary_img":DiaryTemp.objects.filter(author = request.user).order_by("-pk")[0].diary_img,
                    "diary_content":str(request.POST['content']).strip(),
                    "main_emotion" : main,
                    "main_emotion_kor" : main_emotion_kor,
                    "data" : emotion_to_kor.values(),
                    "percent" : percentlist
                }
                return render(request, "EmotionBoard/diary_emotion.html", context = context)
    form = DiaryForm()
    diary_day = []
    for day in Diary.objects.filter(author = request.user).values("write_date"):
        if day["write_date"].strftime("%Y-%m-%d") not in diary_day:
            diary_day.append(day["write_date"].strftime("%Y-%m-%d"))
            # print("중복안됨")
    d = get_date(request.GET.get('month', None))
    cal = Calendar(d.year, d.month, user=request.user)
    html_cal = cal.formatmonth(withyear=True)
    context = {
        "prev_month" : prev_month(d),
        "next_month" : next_month(d),
        "calendar" :  mark_safe(html_cal),
        "diary" : Diary.objects.all(),
        "form":form,
        "diary_day":diary_day,
        "save_count" : DiaryTemp.objects.filter(author = request.user).count()
    }
    return render(request, "EmotionBoard/post_diary.html", context=context)

class DiarySave(TemplateView):
    template_name = "EmotionBoard/diary_final_save.html"        


class DiaryList(ListView):
    model = Diary
    # template_name = 'EmotionBoard/diary_list.html'
    
    # def get_context_data(self, **kwargs):
    #     context = super(DiaryList, self).get_context_data(**kwargs)
    #     context['diary'] = Diary.objects.filter(author = self.request.user).all().order_by('-write_date')
    #     p = Paginator(context['diary'], 9) # Setting 20 products per page
    #     page: int = self.request.GET.get('page', p) # retrive page from URL
    #     context['diarylist'] = p.get_page(page) # Inject Paginator object with limited amout of products

    #     return context    
    def get_context_data(self, **kwargs):
        context = super(DiaryList, self).get_context_data(**kwargs)
        context['diarylist'] = Diary.objects.filter(author = self.request.user).all().order_by('-write_date')
        # context['diary'] = Diary.objects.get(pk = self.kwargs.)
        p = Paginator(context['diarylist'], 9) # Setting 20 products per page
        page: int = self.request.GET.get('page', p) # retrive page from URL
        context['diarylist'] = p.get_page(page) # Inject Paginator object with limited amout of products

        return context  
    
    # paginate_by = 9   # pagination 기능 활성화, page 당 3개   
    # ordering = '-write_date'

class DiaryListDetail(DetailView):
    model = Diary
    # context_object_name = 'Diary'
    template_name = 'EmotionBoard/diary_detail.html'
    # def get_context_data(self, **kwargs):       
    #     context = super(DiaryListDetail,self).get_context_data()
    #     context['diarylist'] = Diary.objects.all().order_by('-pk')
        
    #     return context
    
    def get_context_data(self, **kwargs):
        context = super(DiaryListDetail, self).get_context_data(**kwargs)
        context['diarylist'] = Diary.objects.filter(author = self.request.user).all().order_by('-write_date')
        context['diary'] = Diary.objects.get(pk = self.kwargs['pk'])
        # context['diary'] = Diary.objects.get(pk = self.kwargs.)
        p = Paginator(context['diarylist'], 9) # Setting 20 products per page
        page: int = self.request.GET.get('page', p) # retrive page from URL
        context['diarylist'] = p.get_page(page) # Inject Paginator object with limited amout of products

        return context    
        

def diary_list_detail(request, pk):
    print(pk)
    context = None
    main_emotion = Diary.objects.get(pk = pk).user_select_emotion.name
    data = ['angry', 'calmness', 'expect', 'loathing', 'pleasure', 'sadness', 'shock', 'terror']
    angry_percent = Diary.objects.get(pk=pk).angry_percent
    calmness_percent = Diary.objects.get(pk=pk).calmness_percent
    expect_percent = Diary.objects.get(pk=pk).expect_percent
    loathing_percent = Diary.objects.get(pk=pk).loathing_percent
    pleasure_percent = Diary.objects.get(pk=pk).pleasure_percent
    sadness_percent = Diary.objects.get(pk=pk).sadness_percent
    shock_percent = Diary.objects.get(pk=pk).shock_percent
    terror_percent = Diary.objects.get(pk=pk).terror_percent
    get_emotion_image = Emotion_Category.objects.get(name = Diary.objects.get(pk=pk).user_select_emotion).emotion_image.url
    youtube_list = Recommend_Youtube.objects.filter(emotion_id = Emotion_Category.objects.get(name = main_emotion).pk).order_by("?")[:10]
    print(main_emotion)
    print(emotion_dict.get(main_emotion))
    print(UserSelectGenreForEmotion.objects.filter(emotion = Emotion_Category.objects.get(name = main_emotion)).all())
    
    emotion_count = {}
    recommend_genre = []
    for i in UserSelectGenreForEmotion.objects.filter(emotion = Emotion_Category.objects.get(name = main_emotion)).all():
        for j in i.genre.all():
            if emotion_count.get(j.name) == None:
                emotion_count[j.name] = 1
            else:
                emotion_count[j.name] += 1

    
    for key, value in sorted(emotion_count.items(), key = lambda item:item[1], reverse=True):
        recommend_genre.append(key)
        if len(recommend_genre) == 3:
            break
        
        
    context = {
        "main_emotion" : main_emotion,
        "data" : emotion_to_kor.values(),
        "angry_percent" : angry_percent,
        "calmness_percent": calmness_percent,
        "expect_percent" : expect_percent,
        "loathing_percent" : loathing_percent,
        "pleasure_percent" : pleasure_percent,
        "sadness_percent" : sadness_percent,
        "shock_percent" : shock_percent,
        "terror_percent" : terror_percent,
        "get_emotion_image" : get_emotion_image,
        "youtube_list" : youtube_list,
        "genre_list" : genre_list,
        "movie_genre_list" : recommend_genre
    }
    if request.method == "POST":
        print("selected : ",request.POST.getlist('selected'))
        genre_select_list = request.POST.getlist('selected')
        movie_drama_recommend_list = []
        for i in genre_select_list:
            movie_drama_recommend_list.append(Movie_Drama_Recommend.objects.filter(genre__name__startswith=i).order_by("?")[:5].values())
            
        
        
        #추천 알고리즘 부분. 해당 감정을 느낀 사용자가 입력한 장르 내용을 토대로 가장 많이 선택된 장르 3개를 보여준다.
        #협업 기반 알고리즘이다. 같은 감정을 느낀 사용자가 고른 장르값을 가져오고 가장 많이 선택된 장르를 추천한다.
        #질문 1. 왜 군집화 알고리즘이나 코사인 유사도 같은 알고리즘을 사용하지 않았는가?
        emotion_count = {}
        #print(UserSelectGenreForEmotion.objects.filter(emotion = Emotion_Category.objects.get(name = main_emotion)).all())
        #사용자가 감정에 대해 선택한 장르 테이블에서 해당 감정이 든 값들을 모두 가져온다
        for i in UserSelectGenreForEmotion.objects.filter(emotion = Emotion_Category.objects.get(name = main_emotion)).all():
            #값들을 한개씩 불러오는데 genre로 지정된 컬럼을 다 가져온다. 즉, ManyToMany로 되어있는 모든 genre를 가져온다
            for j in i.genre.all():
                #만약 카운팅에 사용되지 않은 장르 이름이면 키값으로 추가하고 1을 입력한다
                if emotion_count.get(j.name) == None:
                    emotion_count[j.name] = 1
                #카운팅 되어있는 장르면 1을 추가한다.
                else:
                    emotion_count[j.name] = emotion_count[j.name]+1
        recommend_genre = []
        #dict 형식으로 카운팅된 내용을 value값을 기준으로 정렬한다. 상위 3개만 가져온다.
        for key, value in sorted(emotion_count.items(), key = lambda item:item[1], reverse=True):
            recommend_genre.append(key)
            if len(recommend_genre) == 3:
                break    
        
        
        
        context["recomment_list"] = movie_drama_recommend_list
        context["selected_list"] = genre_select_list
        context["movie_genre_list"] = recommend_genre
    return render(request, "EmotionBoard/diary_details.html", context=context)

   
   
def satistic(request):
    
    context = None
    emotion_name = Emotion_Category.objects.all()
    #print(f"request : {request.POST}")
    if not request.user.is_authenticated:
        return redirect("/board/")
    else:
        # if request.POST:
        #     if request.method == "POST" and 'diary' in request.POST:
        if Diary.objects.filter(author = request.user).all().count() == 0:
            return render(request, "EmotionBoard/emotion_chart.html")
        else:
            
            angry_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].angry_percent
            terror_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].terror_percent
            sadness_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].sadness_percent
            loathing_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].loathing_percent
            shock_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].shock_percent
            expect_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].expect_percent
            pleasure_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].pleasure_percent
            calmness_score = Diary.objects.filter(author = request.user).order_by("-write_date")[0].calmness_percent
            main_emotion = Diary.objects.filter(author=request.user).order_by("-write_date")[0].user_select_emotion
                
            angry_count = Diary.objects.filter(author = request.user).filter(user_select_emotion__name="angry").count()
            terror_count = Diary.objects.filter(author = request.user).filter(user_select_emotion__name="terror").count()
            sadness_count = Diary.objects.filter(author = request.user).filter(user_select_emotion__name="sadness").count()
            loathing_count = Diary.objects.filter(author = request.user).filter(user_select_emotion__name="loathing").count()
            shock_count = Diary.objects.filter(author = request.user).filter(user_select_emotion__name="shock").count()
            expect_count = Diary.objects.filter(author = request.user).filter(user_select_emotion__name="expect").count()
            pleasure_count = Diary.objects.filter(author = request.user).filter(user_select_emotion__name="pleasure").count()
            calmness_count = Diary.objects.filter(author = request.user).filter(user_select_emotion__name="calmness").count()

            

            context = [
                angry_score, terror_score, sadness_score, loathing_score, 
                shock_score, expect_score, pleasure_score, calmness_score
            ]

    #########################################월간 긍부정############################################
        
            _year = datetime.today().year
            _month = datetime.today().month
            _today = datetime.today()
            this_month_first_day = datetime(year=_year, month=_month, day=1).date() # 현재 달 기준 1일
            next_month = this_month_first_day + relativedelta.relativedelta(months=1) # 현재 달 기준 다음달
            this_month_last_day = next_month - timedelta(days=1) # 현재 달 기준 마지막일

            delta = this_month_last_day - this_month_first_day
            dates = Diary.objects.filter(author = request.user).filter(write_date__range=[this_month_first_day, this_month_last_day+timedelta(days=1)]).values_list('write_date',flat=True).order_by('write_date')
            
            #datelist=[]
            # 부정
            for i in range(delta.days+1):
                #filter_list = datetime.strftime(this_month_first_day + timedelta(days=i), '%Y-%m-%d') # start에 day를 +1 씩 넣어 list에 저장시킨다.
                negative_count_M = dates.filter(user_select_emotion__name="angry").count() + dates.filter(user_select_emotion__name="terror").count() + dates.filter(user_select_emotion__name="sadness").count() + dates.filter(user_select_emotion__name="loathing").count() + dates.filter(user_select_emotion__name="shock").count() 
                positive_count_M = dates.filter(user_select_emotion__name="expect").count() + dates.filter(user_select_emotion__name="pleasure").count() + dates.filter(user_select_emotion__name="calmness").count() 
                #datelist.append({filter_list: date_count})

            print(f"1월 부정 감정횟수: {negative_count_M}")
            print(f"1월 긍정 감정횟수: {positive_count_M}")

    ###########################################주간 긍부정################################################
            
            startdate = _today - timedelta(days=7)
            enddate = _today
            
            alpha = enddate - startdate
            weeks = Diary.objects.filter(author = request.user).filter(write_date__range=[startdate, enddate]).values_list('write_date',flat=True).order_by('write_date')

            
            negative_count_W = weeks.filter(user_select_emotion__name="angry").count() + weeks.filter(user_select_emotion__name="terror").count() + weeks.filter(user_select_emotion__name="sadness").count() + weeks.filter(user_select_emotion__name="loathing").count() + weeks.filter(user_select_emotion__name="shock").count() 
            positive_count_W = weeks.filter(user_select_emotion__name="expect").count() + weeks.filter(user_select_emotion__name="pleasure").count() + weeks.filter(user_select_emotion__name="calmness").count()
            
            print(weeks)
            print(f"최근 일주일 부정 감정횟수: {negative_count_W}")
            print(f"최근 일주일 감정횟수: {positive_count_W}")

    ######################################################################################################
            count = [
                angry_count, terror_count, sadness_count, loathing_count,
                shock_count, expect_count, pleasure_count, calmness_count
            ]

        return render(request, "EmotionBoard/emotion_chart.html",context={ 
            'context':context, 'data': emotion_name, 'main_emotion': main_emotion,
            'angry_count':angry_count, 'terror_count':terror_count, 'sadness_count':sadness_count,
            'loathing_count':loathing_count, 'shock_count':shock_count, 'expect_count':expect_count,
            'pleasure_count':pleasure_count, 'calmness_count':calmness_count,
            'negative_count_M':negative_count_M, 'positive_count_M':positive_count_M,
            'negative_count_W':negative_count_W, 'positive_count_W':positive_count_W
            })
from django.urls import path, include
from .views import MainView, post_diary, DiarySave, CalendarDetail, CalendarDetails, DiaryListDetail, diary_list_detail, DiaryList, calendar_list_detail, satistic
from django.conf import settings
from django.conf.urls.static import static
app_name="EmotionBoard"
urlpatterns = [
    # path('account/view',UserView.as_view(), name = "account_view" ),
    path('', MainView.as_view(),name="board_main"),
    # path('index/',IndexView.as_view(), name="index_view" ),
    path('post_diary/', post_diary, name="post_diary"),
    path('diary_save/', DiarySave.as_view()),
    path('Account/', include('Account.urls')),
    path('diary_list/', DiaryList.as_view(),name='diary_list'),
    path('diary_detail/<int:pk>/', DiaryListDetail.as_view(),name='diary_detail'),
    path('diary_details/<int:pk>/', diary_list_detail ,name='diary_details'),
    path('calendar_detail/<int:pk>/', CalendarDetail.as_view(),name='calendar_detail'),
    path('calendar_details/<int:pk>/', calendar_list_detail,name='calendar_details'),
    path('emotion_chart/', satistic, name = "statics")
    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)


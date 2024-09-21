from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
import pandas as pd
from EmotionBoard.models import Recommend_Youtube
from EmotionBoard.models import Emotion_Category

#파라미터

# key값 : AIzaSyAkq1LpRG1vKDZO_sjXhH2dvDvdacEgSFg
DEVELOPER_KEY = "AIzaSyAkq1LpRG1vKDZO_sjXhH2dvDvdacEgSFg"
YOUTUBE_API_SERVICE_NAME="youtube"
YOUTUBE_API_VERSION="v3"
#여기서 사용하는 build는 구글 api client 모듈로 어떤 구글의 api와 그 서비스의 버전, 인증 키 값을 넣는다.
youtube = build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)




def playlist(x):
  video_name=[] #영상 제목
  video_date=[] #업로드 시간
  video_thumbnails= [] #썸네일 이미지
  video_url= []
  
  search_response=youtube.search().list(
      q= x,
      order='relevance',
      part='snippet',
      maxResults=30,
      ).execute()

  for i in search_response['items']:
    j = i.get("id")
    if j.get("videoId") != None:
        video_url.append(f"https://www.youtube.com/watch?v={j['videoId']}")
        video_name.append(i['snippet']['title'])
        video_date.append(i['snippet']['publishedAt'])
        video_thumbnails.append(i['snippet']['thumbnails']['medium']['url'])
  
  df=pd.DataFrame([video_name,video_url,video_thumbnails,video_date]).T
  df.columns=['video_name','video_url','video_thumbnails','video_date']
  return df


def df_data(df):
    for i in range(len(df)):
        video_name = df["video_name"][i]
        print(video_name)
        video_url= df["video_url"][i]
        print(video_url)
        video_thumbnails= df["video_thumbnails"][i]
        print(video_thumbnails)
        video_date = df['video_date'][i]
        print(video_date)
        if Recommend_Youtube.objects.filter(link_url__iexact=video_url).count() == 0:
            Recommend_Youtube(link_url=video_url,title =video_name, thumnail =video_thumbnails, emotion = Emotion_Category.objects.get(name = "calmness"), viewCount = 0).save()
            print("저장완료")
        else : 
            print("중복값")

def run():
    
    df_data(playlist("평온한 음악"))





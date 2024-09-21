from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
import pandas as pd
# from crolling.models import Youtube_For_Angry
from EmotionBoard.models import Recommend_Youtube
from EmotionBoard.models import Emotion_Category


class YoutubeVideoapi:
    def __init__(self):
        self.developer_key = "AIzaSyAkq1LpRG1vKDZO_sjXhH2dvDvdacEgSFg"
        self.youtube_api_service_name = "youtube"
        self.youtube_api_version = "v3"

    def videolist(self, keyword):
        youtube = build(self.youtube_api_service_name, self.youtube_api_version, developerKey=self.developer_key)

        search_response = youtube.search().list(
            q=keyword,
            order='relevance',
            part='snippet',
            maxResults=50
        ).execute()
        
        # 검색을 위한 videoID 추출
        video_ids = []
        for i in search_response['items']:
            j = i.get("id")
            if j.get("videoId") != None:
                video_ids.append(j['videoId'])


        channel_video_id = []
        channel_video_title = []
        # channel_rating_view = []
        # channel_rating_comments = []
        channel_rating_good = []
        channel_thumbnails = []
        data_dicts = {'link_url': [], 'title': [], 'goodCount': [], 'thumbnails': []}
        
        # 영상이름, 조회수 , 좋아요수 등 정보 등 추출
        for k in range(0, len(video_ids)):
            video_ids_lists = youtube.videos().list(
                part='snippet, statistics',
                id=video_ids[k],
            ).execute()

            str_video_id = video_ids_lists['items'][0]['id']
            str_video_title = video_ids_lists['items'][0]['snippet'].get('title')

            # str_view_count = video_ids_lists['items'][0]['statistics'].get('viewCount')
            # if str_view_count is None:
            #     str_view_count = "0"

            # str_comment_count = video_ids_lists['items'][0]['statistics'].get('commentCount')
            # if str_comment_count is None:
            #     str_comment_count = "0"

            str_like_count = video_ids_lists['items'][0]['statistics'].get('likeCount')
            if str_like_count is None:
                str_like_count = "0"

            str_thumbnails = video_ids_lists['items'][0]['snippet'].get('thumbnails').get('medium').get('url')

            
            # URL 입력
            channel_video_id.append(f"https://www.youtube.com/watch?v={str_video_id}")
            # 제목 입력
            channel_video_title.append(str_video_title)
            # # 조회수 입력
            # channel_rating_view.append(str_view_count)
            # # 댓글수 입력
            # channel_rating_comments.append(str_comment_count)
            # 좋아요 입력
            channel_rating_good.append(str_like_count)
            # 썸네일 입력
            channel_thumbnails.append(str_thumbnails)

        data_dicts['link_url'] = channel_video_id
        data_dicts['title'] = channel_video_title
        # data_dicts['조회수'] = channel_rating_view
        # data_dicts['댓글수'] = channel_rating_comments
        data_dicts['goodCount'] = channel_rating_good
        data_dicts['thumbnails'] = channel_thumbnails
        return data_dicts


def fuck(keyword):
    search_dict = YoutubeVideoapi().videolist(keyword)  # 아이디, 제목, 조회수, 댓글수, 좋아요수 추출
    df = pd.DataFrame(search_dict)  # 데이터프레임화
    for i in range(len(df)):
        video_name = df["title"][i]
        print(video_name)
        video_url= df["link_url"][i]
        print(video_url)
        video_thumbnails= df["thumbnails"][i]
        print(video_thumbnails)
        goodCount = df['goodCount'][i]
        print(Recommend_Youtube.objects.filter(link_url__iexact=video_url).count())
        if Recommend_Youtube.objects.filter(link_url__iexact=video_url).count() == 0:
            Recommend_Youtube(link_url=video_url,title =video_name, thumnail =video_thumbnails, goodCount = goodCount, emotion = Emotion_Category.objects.get(name = "angry")).save()
            print("저장완료")
        else : 
            print("중복값")


def run():
    fuck("화날때")
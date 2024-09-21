from googleapiclient.discovery import build
import pandas as pd
import datetime as dt
from EmotionBoard.models import Recommend_Youtube

DEVELOPER_KEY = "AIzaSyAYmLZBXL5oc-ahV56KB9VIx8pmZHlDtM0"
YOUTUBE_API_SERVICE_NAME="youtube"
YOUTUBE_API_VERSION="v3"

class YoutubeVideoapi:
    def __init__(self):
        self.developer_key = DEVELOPER_KEY
        self.youtube_api_service_name = YOUTUBE_API_SERVICE_NAME
        self.youtube_api_version = YOUTUBE_API_VERSION

    def videolist(self, keyword):
        # youtube api의 get_authenticated_service 메서드에서 build를 반환함.
        # build의 매개변수로 통해 구글의 api 서비스 이름과 그 서비스의 버전, 인증 키 값을 넣는다.
        youtube = build(self.youtube_api_service_name, self.youtube_api_version, developerKey=self.developer_key)

        search_response = youtube.search().list(  # search(): API에 검색을 요청하여 리스트로 반환
            q=keyword,          # 검색어
            order='relevance',  # 정렬방법 -> 관련성 기준으로 리소스 정렬
            part='snippet',     # 필수 매개변수('id', 'snippet'), snippet으로 해야 검색한 정보에 대한 상세 내용이 나오고 id만 하면 정말 id만 나온다.
            maxResults=100      # 결과개수
        ).execute()             # 실행
        
        # 검색을 위한 videoID 추출
        video_ids = []
        for i in search_response['items']:
            j = i.get("id")
            if j.get("videoId") != None: # 유튜브채널만 존재할때, 
                video_ids.append(j['videoId'])


        channel_video_id = []
        channel_video_title = []
        channel_rating_good = []
        channel_thumbnails = []
        data_dicts = {'link_url': [], 'title': [], 'goodCount': [], 'thumbnails': []}
        
        # video id에 대해 영상이름, 조회수 , 좋아요수 등 정보 등 추출
        # video_ids 리스트의 길이 만큼 반복문으로 'snippet'와'statistics'를 동시에 지정해야 조회수, 좋아요수에 대해 접근할수있음
        for k in range(0, len(video_ids)):
            video_ids_lists = youtube.videos().list(
                part='snippet, statistics',
                id=video_ids[k],
            ).execute()

            str_video_id = video_ids_lists['items'][0]['id']

            str_video_title = video_ids_lists['items'][0]['snippet'].get('title')

            str_like_count = video_ids_lists['items'][0]['statistics'].get('likeCount')
            if str_like_count is None: # 좋아요에 대한 정보가 존재하지 않는다면, 
                str_like_count = "0"   # 0을 반환

            str_thumbnails = video_ids_lists['items'][0]['snippet'].get('thumbnails').get('medium').get('url')

            
            # URL 추가
            channel_video_id.append(f"https://www.youtube.com/watch?v={str_video_id}")
            # 제목 추가
            channel_video_title.append(str_video_title)
            # 좋아요 추가
            channel_rating_good.append(str_like_count)
            # 썸네일 추가
            channel_thumbnails.append(str_thumbnails)

        data_dicts['link_url'] = channel_video_id
        data_dicts['title'] = channel_video_title
        data_dicts['goodCount'] = channel_rating_good
        data_dicts['thumbnails'] = channel_thumbnails
        return data_dicts


def main(keyword):
    search_dict = YoutubeVideoapi().videolist(keyword)  # 아이디, 제목, 조회수, 댓글수, 좋아요수 추출
    df = pd.DataFrame(search_dict)  # 데이터프레임화

    for i in range(len(df)):
        video_name = df["title"][i]

        video_url= df["link_url"][i]

        video_thumbnails= df["thumbnails"][i]

        goodCount = df['goodCount'][i]

        if Recommend_Youtube.objects.filter(link_url__iexact=video_url).count() == 0:
            # 대소문자를 구분하지 않고 정확히 일치하는 link_url 수가 0일때,
            Recommend_Youtube(link_url=video_url,title =video_name, thumnail =video_thumbnails, goodCount = goodCount, emotion = Emotion_Category.objects.get(name = "분노")).save()
            print("저장완료")
        else : 
            print("중복값")

def run():
    main('신날때 플레이리스트')
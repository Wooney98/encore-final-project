import requests
import json
# from crolling.models import Romance_model
# action adeventure function
from EmotionBoard.models import Movie_Drama_Recommend
from EmotionBoard.models import Genre_Category

genre_list = [12,14,16,18,28,35,878,10402,10749,10751,10770]

def romance_func(x):
    romance = []
    iter_num = len(x)
    for i in range(iter_num):
        if ('10749' in str(x[i]['fields']['genres'])):
             romance.append(x[i]['fields'])
        else:
            continue
    # print( romance)
    # print("## 원하는 장르 결과 :  ", tvmoive_ect.__len__())
    return  romance



def genreCast(x):
  input_list = x
  genre2str = [ i for i in input_list]
  print(genre2str)
  return genre2str

def dbSave(romance):
    # print(fantasy_sf)
    for obj in romance:
        except_num = 0 
        # print(obj, type(obj))
        print('-----------------------------')
        try :
            movie_id = obj['movie_id']
            print("movie_id> ", movie_id)
            print(type(movie_id))
            title = obj['title']
            print("title > ", title)
            print(type(title))
            released_date = obj['released_date']
            print("'released_date > ", released_date)
            print(type(released_date))
            overview = obj['overview']
            print("overview > ", overview)
            print(type(overview))
            poster_path = obj['poster_path']
            print("poster_path > ", poster_path)
            print(type(released_date))
            genres = obj['genres']
            print(genres)
            genres = genreCast(genres)
            print("new genres>>> ", genres)
            print(type(genres[0]))
            
                    
            if Movie_Drama_Recommend.objects.filter(title__iexact=title).count() == 0:
                db = Movie_Drama_Recommend.objects.create(title=title,released_date=released_date,thumnail=poster_path)
                
                for i in genres:
                    if i in genre_list:
                        db.genre.add(Genre_Category.objects.get(id = i))
                        # genre.append(Genre_Category.objects.get(id = i))
                db.save()
                    
                print("저장완료")
                print("## 원하는 장르 결과 :  ", romance.__len__())
            else : 
                print("중복값")
        except Exception as e:
            print(e)
            except_num =+1
            print('답없음', except_num )
            



def run():
    TMDB_API_KEY = '4343395b65d4f99d0f3351458f26c8fd'
    total_data = []
    for i in range(1, 50):
        request_url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&region=KR&language=ko&page={i}"
        movies = requests.get(request_url).json()
        for movie in movies['results']:
            if movie.get('release_date', ''):
                # print('여기에 값있음')
                fields = {
                    'movie_id': movie['id'],
                    'title': movie['title'],
                    'released_date': movie['release_date'],
                    'overview': movie['overview'],
                    'poster_path': "https://image.tmdb.org/t/p/w200"+movie['poster_path'],
                    'genres': movie['genre_ids']
                }
                data = {
                    "fields": fields
                }
                total_data.append(data)    
    # print(total_data)
    dbSave(romance_func(total_data))





# [{'id': 28, 'name': '액션'},
#  {'id': 12, 'name': '모험'},
#  {'id': 16, 'name': '애니메이션'},
#  {'id': 35, 'name': '코미디'},
#  {'id': 80, 'name': '범죄'},
#  {'id': 99, 'name': '다큐멘터리'},
#  {'id': 18, 'name': '드라마'},
#  {'id': 10751, 'name': '가족'},
#  {'id': 14, 'name': '판타지'},
#  {'id': 36, 'name': '역사'},
#  {'id': 27, 'name': '공포'},
#  {'id': 10402, 'name': '음악'},
#  {'id': 9648, 'name': '미스터리'},
#  {'id': 10749, 'name': '로맨스'},
#  {'id': 878, 'name': 'SF'},
#  {'id': 10770, 'name': 'TV 영화'},
#  {'id': 53, 'name': '스릴러'},
#  {'id': 10752, 'name': '전쟁'},
#  {'id': 37, 'name': '서부'}]
import requests
import json
from EmotionBoard.models import Movie_Drama_Recommend
from EmotionBoard.models import Genre_Category

genre_list = [12,14,16,18,28,35,878,10402,10749,10751,10770]

# action adeventure function

def action_adventure(x):
    action_adventure = []
    iter_num = len(x)
    for i in range(iter_num):
        if ('28' in str(x[i]['fields']['genres'])) and ('12'  in str(x[i]['fields']['genres'])):
            action_adventure.append(x[i]['fields'])
        else:
            continue
    print("## 원하는 장르 결과 :  ", action_adventure.__len__())
    return action_adventure


def genreCast(x):
  input_list = x
  genre2str = [ i for i in input_list]
  print(genre2str)
  return genre2str

def dbSave(action_adventure):
    print(action_adventure)
    for obj in action_adventure:
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
            genres = genreCast(genres)
            print("new genres>>> ", genres)
            
            
            if Movie_Drama_Recommend.objects.filter(title__iexact=title).count() == 0:
                db = Movie_Drama_Recommend.objects.create(title=title,released_date=released_date,thumnail=poster_path)
                for i in genres:
                    if i in genre_list:
                        db.genre.add(Genre_Category.objects.get(id = i))
                        # genre.append(Genre_Category.objects.get(id = i))
                db.save()
                print("저장완료")
            else : 
                print("중복값")
        except Exception as e:
            print(e)
            except_num =+1
            print('답없음', except_num )
            



def run():
    TMDB_API_KEY = '4343395b65d4f99d0f3351458f26c8fd'
    total_data = []
    for i in range(1, 20):
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
    dbSave(action_adventure(total_data))


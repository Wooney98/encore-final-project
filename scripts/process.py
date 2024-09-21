from django.conf import settings
import torch
import gluonnlp as nlp
import numpy as np
import time
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from kobert.utils import get_tokenizer
from kobert.pytorch_kobert import get_pytorch_kobert_model


#bertmodel의 vocabulary
tokenizer = get_tokenizer()
_ , vocab = get_pytorch_kobert_model()
tok = nlp.data.BERTSPTokenizer(tokenizer, vocab, lower=False)
tokenizer = nlp.data.BERTSentenceTransform(tok, max_seq_length=64, pad=True, pair=False)


# labelEncoder
LE = LabelEncoder()
target = ['angry', 'calmness', 'expect', 'loathing', 'pleasure', 'sadness', 'shock', 'terror']
LE.fit_transform(np.array(target))


#predict_sentence는 사용자가 입력한 일기를 의미
def predictSenti(predict_sentence):
  device = torch.device("cuda:0")
  start = time.time()
  # settings에 환경변수로 등록한 model 불러오기 
  MODEL = getattr(settings, 'MODEL', 'model')
  MODEL.eval() # 평가 mode로 전환 : 학습이 아닌 평가(추론) 모드 
  out = tokenizer(predict_sentence) # tokenizer에 사용자가 입력한 일기를 넣으면, 입력한 일기인 텍스트 데이터를 토큰화함
  
  # 토크나이저는 총 3개의 값을 뱉어냄
  # 그 3개의 값은 token_ids(토큰화된 토큰의 고유 id), valid_length, segments_ids
  token_ids = torch.LongTensor(out[0]).unsqueeze(0).to(device) # token_id는 tensor형태
  
  # token_type_ids >>  문장 순서 정보가 담겨 있음. 
  # 만약 토크나이저의 input(일기)이 1문장일 경우 0으로 1문장이라는 위치를 표현하며, 
  # 2문장일 경우 첫번째 문장은 0의 값을 갖고, 두번째 문장은 1의 값을 갖는다.
  # 0과 1로 토큰이 속한 문장의 위치(순서)를 표현한 값이다.
  valid_length = torch.tensor(out[1]).unsqueeze(0)
  
  # attention mask는 어떤 token에 집중해야할지를 알려주는 정보이다. 모델에 입력되는 모든 문장은 길이가 같아야하는데, 최대 문장길이보다 짧은 경우 padding 옵션을 통해 길이를 맞춘다. 
  # 이때 padding된 부분은 0, padding되지 않은 부분을 1로 표현한 값이다. 
 # 토크나이저가 뱉어낸 값을 모델에 넣으면 , model이 해당 문장에 대한감정을 추론한다. 
  # 이를 모델에 넣으면 model이 해당 문장에 대한 감정을 추론
  segment_ids = torch.LongTensor(out[2]).unsqueeze(0).to(device)
  
  # 모델이 추론한 값은 tensor객체의 배열로 리턴되며, 총 8개의 값을 가지고 있다.
  # 모델은 8개의 라벨 중 1개를 맞추도록 학습되었기 때문에, 
  # 리턴된 배열의 각각의 값은
  # 모델이 예측한 고유 감정이 정답일 확률을 뜻한다. 
  pred = MODEL(token_ids, valid_length ,segment_ids)


  # numpy로 변환하여 추가적인 연산을 수행하기 쉽게 설정함
  #gpu의 작업되어 있는 내용을 cpu로 옮김
  pred =  pred.to('cpu').detach().numpy()
  print("pred>", pred)

   # 모델에 대한 감정을 확률로 매긴 값을 scailing하여 퍼센티지로 변환 
  scaler = MinMaxScaler()
  scaled = scaler.fit_transform(pred.reshape(-1,1))
  total = scaled.sum()
  percent = [ (obj/total)*100 for obj in scaled.squeeze()]


  # 실제로 모델이 추론한 감정에는 가장 큰 값이 들어있기 때문에, 
  # 가장 큰 값의 인덱스 위치를 반환하는 함수를 사용하여 정보를 얻어냄
  pred = np.argmax(pred)


  # 텍스트의 감정은 label encoder에 의해 수치화되었음
  # 수치형태로 변환된 감정 값을 다시 label encoder에 넣어서 기존의 텍스트 형태의 감정을 얻어냄  
  pred = LE.inverse_transform([pred])
  end = time.time()
  print("### 모델 추론 시간 >> ", end-start )
  return pred, percent
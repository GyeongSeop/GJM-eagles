### module import ###
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from konlpy.tag import Okt
from collections import Counter
import re
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

### Functions ###

def content_filter(text):
    hangul = re.compile('[^ ㄱ-ㅣ 가-힣]')  # 정규 표현식 처리
    result = hangul.sub('', text)
    okt = Okt()  # 형태소 추출
    pos = [i[1] for i in okt.pos(result)]
    
    if len(pos)!=0:
        n_na = (pos.count('Noun')+pos.count('Adjective'))/len(pos)
        n_va = (pos.count('Verb')+pos.count('Adverb'))/len(pos)
    else:
        n_na = 0
        n_va = 0
    
    # 명사, 형용사 비율이 낮고, 동사와 부사의 비율이 높은 경우
    # 내용 없는 리뷰 또는 총 길이 10자 미만 리뷰
    if len(result)<10 or n_na < n_va:
        return True # 필터링 기준에 부합 -> 제외
    return False 

def score_to_int(text):
    return int(text[4:-2])

def text_cleaning(text):
    hangul = re.compile('[^ ㄱ-ㅣ 가-힣]')  # 정규 표현식 처리
    result = hangul.sub('', text)
    okt = Okt()  # 형태소 추출
    nouns = okt.nouns(result)
    nouns = [x for x in nouns if len(x) > 1]  # 한글자 키워드 제거
    nouns = [x for x in nouns if x not in stopwords]  # 불용어 제거
    return nouns

def rating_to_label(rating):
    if rating > 3: # 4, 5점: 긍정
        return 1
    else:
        return 0 # 1~3: 부정

### Data Preprocessing ###

# 데이터 불러오기
df = pd.read_excel("final_result.xlsx")

# 기본 필터링
df['filtering'] = df['content'].apply(content_filter)
df = df[df['filtering']==False]
df.reset_index(drop=True, inplace=True)

# 별 개수를 숫자로 변환
df['score'] = df['score'].apply(score_to_int)

# 감성 분석을 위해 필요한 열만 남김
df = df[['score', 'content']]
df.columns = ['rating', 'text'] # 열 이름 변경

# 불용어 사전
stopwords = pd.read_csv("https://raw.githubusercontent.com/yoonkt200/FastCampusDataset/master/korean_stopwords.txt").values.tolist()
my_stopwords = ['노맛', '존맛'] #나의 불용어 추가

# 텍스트 클렌징
vect = CountVectorizer(tokenizer = lambda x: text_cleaning(x))
bow_vect = vect.fit_transform(df['text'].tolist())
word_list = vect.get_feature_names()
count_list = bow_vect.toarray().sum(axis=0)

# tf-idf 가중치 부여 -> 중요 키워드 파악
tfidf_vectorizer = TfidfTransformer()
tf_idf_vect = tfidf_vectorizer.fit_transform(bow_vect)

# 별점에 따라 긍정부정 -> 4, 5(긍정) // 1, 2, 3(부정)
df['y'] = df['rating'].apply(lambda x: rating_to_label(x))


### 모델 학습1 ###
x = tf_idf_vect
y = df['y']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.3, random_state=1)

# fit in training set
lr = LogisticRegression(random_state = 0)
lr.fit(x_train, y_train)

# predict in test set
y_pred = lr.predict(x_test)

# classification result for test set
print('accuracy: %.2f' % accuracy_score(y_test, y_pred))
print('precision: %.2f' % precision_score(y_test, y_pred))
print('recall: %.2f' % recall_score(y_test, y_pred))
print('F1: %.2f' % f1_score(y_test, y_pred))


# confusion matrix -> 긍정 응답이 많아서 편향된 결과가 나타납니다. -> 따라서 2차 학습에 들어갑니다.
confu = confusion_matrix(y_true = y_test, y_pred = y_pred)
plt.figure(figsize=(4, 3))
sns.heatmap(confu, annot=True, annot_kws={'size':15}, cmap='OrRd', fmt='.10g')
plt.title('Confusion Matrix')
plt.show()

### 모델 학습2 ###
print(df['y'].value_counts()) # 부정 응답의 개수만큼 학습시킬 것입니다.
r_value = df['y'].value_counts()[0]
positive_random_idx = df[df['y']==1].sample(r_value, random_state=12).index.tolist()
negative_random_idx = df[df['y']==0].sample(r_value, random_state=12).index.tolist()

random_idx = positive_random_idx + negative_random_idx
x = tf_idf_vect[random_idx]
y = df['y'][random_idx]
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=1)

lr2 = LogisticRegression(random_state = 0)
lr2.fit(x_train, y_train)
y_pred = lr2.predict(x_test)

# classification result for test set
print('accuracy: %.2f' % accuracy_score(y_test, y_pred))
print('precision: %.2f' % precision_score(y_test, y_pred))
print('recall: %.2f' % recall_score(y_test, y_pred))
print('F1: %.2f' % f1_score(y_test, y_pred))

confu = confusion_matrix(y_true = y_test, y_pred = y_pred)
plt.figure(figsize=(4, 3))
sns.heatmap(confu, annot=True, annot_kws={'size':15}, cmap='OrRd', fmt='.10g')
plt.title('Confusion Matrix')
plt.show()

### 최종 결과 ###
print(sorted(((value, index) for index, value in enumerate(lr2.coef_[0])), reverse = True)[:5])
print(sorted(((value, index) for index, value in enumerate(lr2.coef_[0])), reverse = True)[-5:])

coef_pos_index = sorted(((value, index) for index, value in enumerate(lr2.coef_[0])), reverse = True)
coef_neg_index = sorted(((value, index) for index, value in enumerate(lr2.coef_[0])), reverse = False)

invert_index_vectorizer = {v: k for k, v in vect.vocabulary_.items()}

# 긍정 top20
print()
print("### 긍정 top20 ###")
for coef in coef_pos_index[:20]:
    print(invert_index_vectorizer[coef[1]], coef[0])

# 부정 top20
print()
print("### 부정 top20 ###")
for coef in coef_neg_index[:20]:    
    print(invert_index_vectorizer[coef[1]], coef[0])
    
# 키워드 저장
pos = [[invert_index_vectorizer[coef[1]], coef[0]] for coef in coef_pos_index]
neg = [[invert_index_vectorizer[coef[1]], coef[0]] for coef in coef_neg_index]

df_pos = pd.DataFrame(pos, columns=['word', 'coef'])
df_neg = pd.DataFrame(neg, columns=['word', 'coef'])
df_pos.to_excel("result_pos_word.xlsx")
df_neg.to_excel("result_neg_word.xlsx")
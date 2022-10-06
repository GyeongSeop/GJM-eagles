import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 500)
pd.options.display.max_colwidth = 200

def score_to_int(text):
    return int(text[4:-2])


def select():   # 응답 받기
    choice_list = ["지역", "카테고리", "전체"]
    while True:
        result = input("{}중에서 한 가지를 선택해 주세요: ".format(choice_list))
        if result not in choice_list:
            print("다시 선택해주세요.")
        else:
            break
    return result


def first_task(df):     #동작 task 결정
    choice = select()
    if choice == "지역":
        local_select(df)
    elif choice == "카테고리":
        category_select(df)
    else:
        total_select(df)


def last_task(df, mode_num):    #다음 동작 결정
    while True:
        mode_select = int(input("\n1. 홈\n2. 현재 모드\n3. 종료\n다음 작업의 번호를 선택해 주세요: "))
        if mode_select not in [1, 2, 3]:
            print("잘못된 선택입니다. 다시 선택해주세요.")
        else:
            break
    if mode_select == 1:
        first_task(df)
    elif mode_select == 2:
        if mode_num == 1:
            local_select(df)
        elif mode_num == 2:
            category_select(df)
        else:
            total_select(df)
    else:
        print("감사합니다. 다음에 다시 이용해 주세요.")


def store_list_maker(df, k):
    store_list = []
    for i in range(k):
        store_list.append(df.iat[i, 0])
    return store_list


def information(df, store_list):
    df2 = pd.read_excel("final_result.xlsx", index_col=0)
    df2.set_index("name")
    temp = pd.DataFrame()
    temp_df = pd.DataFrame()
    while True:
        store_name = input("상세정보 열람을 희망하는 가게의 이름을 입력해 주세요: ")
        if store_name not in store_list:
            print("잘못된 정보입니다. 다시 입력해주세요")
        else:
            break
    temp_df2 = df[df['name'].str.contains(store_name) == True]
    temp_df = pd.concat([temp_df, temp_df2], axis=0)
    temp_df.drop_duplicates(['name'], inplace=True)  # 이름 중복 제거

    temp2 = df2[df2['name'].str.contains(store_name) == True]
    temp = pd.concat([temp, temp2], axis=0)

    print("음식점 이름 : {}".format(store_name))
    print("상세 주소 : {}".format(','.join(list(temp_df['address']))))
    print("가게 카테고리 : {}".format(','.join(list(temp_df['category']))))
    print("가게 평점 : {} 점".format(','.join(map(str, list(temp_df['score_avg'])))))
    print("------------------------------------------------")
    print(temp[['score', 'date', 'content']])


def local_select(df):
    temp = pd.DataFrame()
    busan = ['중구', '서구', '동구', '영도구', '부산진구', '동래구', '남구', '북구',
             '해운대구', '사하구', '금정구', '강서구', '연제구', '수영구', '사상구', '기장군']

    while True:
        local = input("부산광역시 내 지역 중에서 원하시는 곳을 입력해 주세요(ex. 금정구): ".format(busan))
        if local not in busan:
            print("다시 선택해주세요.")
        else:
            break

    temp2 = df[df['address'].str.contains(local) == True]
    temp = pd.concat([temp, temp2], axis=0)
    temp.drop_duplicates(['name'], inplace=True)  # 이름 중복 제거
    temp.sort_values(by=['score_avg'], ascending=False, inplace=True)  # 정렬
    temp.reset_index(drop=True, inplace=True)
    if len(temp) == 0:
        print('죄송합니다. 해당 지역의 음식점은 없습니다. 다른지역을 선택해주세요.')
        local_select(df)
    else:
        k = len(temp.index)
        store_list = store_list_maker(temp, k)
        print(temp)
        information(df, store_list)
        last_task(df, 1)


def category_select(df):
    category_list = ["일식", "한식", "중식", "양식"]
    japan = ['일본', '돈까스', '초밥', '텐동', '라멘']
    china = ['중국', '마라탕', '훠궈', '탕수육', '깐풍기']
    western = ['이탈리아', '프랑스', '피자', '양식', '브라질', '유럽']
    korea = japan + china + western
    while True:
        cate = input("{} 중에서 원하시는 카테고리를 입력해 주세요: ".format(category_list))
        if cate not in category_list:
            print("다시 선택해주세요.")
        else:
            break
    temp = pd.DataFrame()
    if cate == "일식":
        for c in japan:
            temp2 = df[df['category'].str.contains(c) == True]
            temp = pd.concat([temp, temp2], axis=0)
    elif cate == "중식":
        for c in china:
            temp2 = df[df['category'].str.contains(c) == True]
            temp = pd.concat([temp, temp2], axis=0)
    elif cate == "양식":
        for c in western:
            temp2 = df[df['category'].str.contains(c) == True]
            temp = pd.concat([temp, temp2], axis=0)
    else:
        temp3 = pd.DataFrame()
        for c in korea:
            temp2 = df[df['category'].str.contains(c) == True]
            temp3 = pd.concat([temp3, temp2], axis=0) #한식이 아닌 음식점 concat
        temp3.drop_duplicates(['name'], inplace=True)  # 이름 중복 제거
        temp = pd.concat([df, temp3, temp3]).drop_duplicates(keep=False)  #차집합

    temp.drop_duplicates(['name'], inplace=True)  # 이름 중복 제거
    temp.sort_values(by=['score_avg'], ascending=False, inplace=True)  # 정렬
    temp.reset_index(drop=True, inplace=True)
    k = len(temp.index)
    store_list = store_list_maker(temp, k)
    print(temp)
    information(df, store_list)
    last_task(df, 2)


def total_select(df):
    answer = ['10', '20', '50', '전체']
    while True:
        k = input("전체 가게 중 상위 몇개의 가게가 출력되길 원하십니까? (10, 20, 50, 전체 중 택 1): ")
        if k not in answer:
            print("다시 선택해주세요.")
        else:
            break
    if k == '전체':
        k2 = len(df.index)
        store_list = store_list_maker(df, k)
        print(df)
        information(df, store_list)
        last_task()
    else:
        k = int(k)
        store_list = store_list_maker(df, k)
        print(df.iloc[:k, :])
        information(df, store_list)
        last_task(df, 3)


def main():
    # 데이터 로드
    df = pd.read_excel("final_result.xlsx", index_col=0)
    df.set_index("name")

    # 별점 -> 숫자
    df['score'] = df['score'].apply(score_to_int)

    # 별점 평균, category 분류 단순화
    avg_list = []
    for i in range(len(df)):
        n = len(df[df['name'] == df['name'][i]])
        s = sum(df.loc[df['name'] == df['name'][i], "score"].values)
        avg_list.append(round(s/n, 2))
    df['score_avg'] = avg_list
    df.drop_duplicates(['name'], inplace=True) # 이름 중복 제거
    df = df.sort_values(by=['score_avg'], ascending=False) # 별 평균으로 나열
    df = df[['name', 'address', 'category', 'score_avg']]
    first_task(df)

main()
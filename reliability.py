import copy

def reliability(csv_list):
    store = csv_list[0].index('가게이름')
    name = csv_list[0].index('ID')
    score = csv_list[0].index('별점')
    day = csv_list[0].index('날짜')
    review = csv_list[0].index('리뷰')
    name_list, score_list = user_overlap(csv_list, name, score, review, day)
    return name_list, score_list

def user_overlap(csv_list, name, score, review, day):     #리뷰 작성자 중복 -> 해당 사용자 평점 평균으로 1개만 반영
    name_list = list()
    score_list = list()
    temp = list()
    for i in range(1, len(csv_list)):
        if csv_list[i][name] not in name_list:
            name_list.append(csv_list[i][name])
            score_list.append(int(csv_list[i][score]))
            temp.append(1)
        else:
            k = name_list.index(csv_list[i][name])
            if csv_list[k+1][review] == csv_list[i][review] or csv_list[k+1][day] == csv_list[i][day]:
                temp[k] = 0        #해당 사용자 리뷰 배제
            elif temp[k] != 0:
                temp[k] += 1
                score_list[k] += int(csv_list[i][score])
    while 0 in temp:
        k = temp.index(0)
        del score_list[k], name_list[k], temp[k]
    for i in range(len(name_list)):
        score_list[i] = score_list[i] / temp[i]
    return name_list, score_list

def score_correction(l2): #점수 보정. 최하점과 최상점 제거 -> 평점 외곡 방지
    num = len(l2)
    temp = copy.deepcopy(l2)  # deep copy 사용
    temp.sort()

    if num <= 3:
        pass
    elif num < 10:
        del temp[0], temp[-1]
        num -= 2
    else:
        del temp[0:1], temp[-2:-1]
        num -= 4
    total_score = sum(temp)
    return round(total_score / num, 2)
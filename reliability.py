import copy
from datetime import datetime

class Store:
    def __init__(self, store, address, category):
        self._store = store
        self._address = address
        self._category = category
        self._review = list()
        self._average = 0
        self._check = False

    def review_append(self, id, score, day, review):
        self._review.append([id, score, day, review])

    def user_overlap(self):
        id_list = list()
        score_list = list()
        day_list = list()
        review_list = list()
        temp = list()
        result = list()
        for line in self._review:
            if line[0] not in id_list:
                id_list.append(line[0])
                score_list.append(int(line[1]))
                day_list.append(int(line[2]))
                review_list.append(line[3])
                temp.append(1)
            else:
                k = id_list.index(line[0])
                if review_list[k] == line[3] or day_list[k] == line[3]:
                    temp[k] = 0  # 해당 사용자 리뷰 배제
                    review_list[k] = ''
                elif temp[k] != 0:
                    temp[k] += 1
                    score_list[k] += int(line[1])
                    review_list[k] += line[3]
                    day_list[k] = day_list[k] if day_list[k] > int(line[2]) else int(line[2])
        while 0 in temp:
            k = temp.index(0)
            del score_list[k], id_list[k], day_list[k], review_list[k], temp[k]
        for i in range(len(id_list)):
            score_list[i] = score_list[i] / temp[i]
            result.append([id_list[i], score_list[i], day_list[i], review_list[i]])
        self._review = result

    def score_correction(self):  # 점수 보정. 최하점과 최상점 제거 -> 평점 외곡 방지
        num = len(self._review)
        temp = copy.deepcopy(self._review)  # deep copy 사용
        temp.sort(key=lambda x: x[1])

        if num <= 3:
            pass
        elif num < 10:
            del temp[0], temp[-1]
            num -= 2
        else:
            del temp[0:1], temp[-2:-1]
            num -= 4
        score = [int(temp[i][1]) for i in range(num)]
        total_score = sum(score)
        self._average = round(total_score / num, 2)

    def latest(self):  # 최신 리뷰가 작성된 지 1개월이 지난 경우 작업
        temp = copy.deepcopy(self._review)
        temp.sort(key=lambda x: x[2])
        now = datetime.now()
        compare_date = datetime.strptime(str(temp[-1][2]), "%Y%m%d")
        date_diff = now - compare_date
        if int(date_diff.days) >= 31:
            self._check = True
            print('확인 절차 필요')

    def write(self):
        result = [[self._store,self._average,self._review[0][0],self._review[0][1],self._review[0][2],self._review[0][3]]]
        for i in range(1, len(self._review)):
            result.append(['','',self._review[i][0],self._review[i][1],self._review[i][2],self._review[i][3]])
        return result

def latest():
    passimport copy
from datetime import datetime

def latest(day_list): #최신 리뷰가 작성된 지 1개월이 지난 경우 작업
    temp = copy.deepcopy(day_list)
    temp.sort()
    now = datetime.now()
    compare_date = datetime.strptime(str(temp[-1]), "%Y%m%d")
    date_diff = now - compare_date
    if int(date_diff.days) >= 31:
        print('업장 확인 필요')

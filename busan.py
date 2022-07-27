from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time


# 구글 지도의 검색창이 떴는지 확인하는 코드
def wait_searchBar(driver):
    # 검색창을 class name을 통해 찾고, 검색창이 떴다면 넘어갑니다
    try: element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tactile-searchbox-input")))
    finally: pass

# serach_name으로 검색하는 코드
def input_funtion(driver, search_name):
    # 우선 검색창을 찾습니다
    search_box = driver.find_element_by_id("searchboxinput")
    # 검색어를 입력합니다
    search_box.send_keys(search_name)
    # 엔터를 쳐서 검색합니다
    search_box.send_keys(Keys.ENTER)


# 엔터를 기준으로 받아온 데이터를 split 하는 함수
def parse_data(text_list):
    # 최종 결과를 담을 배열들을 선언해둡니다
    name, rating, review_count, address, category, rv = [], [], [], [], [], []
    for i in range(len(text_list)):
        # text_list에는 각 가게별로 정보가 엔터(\n)를 기준으로 나뉘어 저장되어 있습니다. 엔터를 구분자로 텍스트를 배열로 만들어줍니다
        text_array = text_list[i].split('\n')
        # 첫줄에는 이름이 저장되어있습니다([0])
        name.append(text_array[0])

        # 두번째줄에는 리뷰가 저장되어 있으나 리뷰가 없는 경우에 대해서는 아래와 같이 예외처리 해줍니다
        if text_array[1] == 'No reviews':
            rating.append(' ')
            review_count.append(' ')
        else:
            # 리뷰가 있는 경우에는
            try:
                # 첫줄에 있는 리뷰 정보를 아래와 같이 파싱해줍니다
                rating.append(text_array[1].split(' · ')[0].split('(')[0])
            except:
                try:
                    # 리뷰 형태가 점이 없는 경우에 대한 예외처리 입니다
                    rating.append(text_array[1].split('(')[0])
                except:
                    rating.append(' ')
            try:
                category.append(text_array[2].split(' · ')[0])
            except:
                try:
                    category.append(' ')
                except:
                    category.append(' ')
            try:
                rv.append(' ')
            except:
                try:
                    rv.append(' ')
                except:
                    rv.append(' ')
            try:
                # 리뷰 개수는 리뷰 이후에 나오는 괄호 뒷부분에 들어있거나
                review_count.append(text_array[1].split(' · ')[0].split('(')[1][:-1])
            except:
                # 리뷰 형태가 점이 없는 경우에 대한 예외처리 입니다
                try:
                    review_count.append(text_array[1].split('(')[1][:-1])
                except:
                    review_count.append(' ')
        try:
            # 주소는 세번째 줄어 들어있습니다
            address.append(text_array[2].split(' · ')[1])
        except:
            # 형태가 다른 경우에 대한 예외처리입니다
            address.append(' ')
    return name, rating, review_count, address, category, rv

# 최종 결과물을 csv로 만드는 함수입니다.
def make_csv(food_name, rating, review_count, address, category, rv):
    df = pd.DataFrame({
        '가게이름': food_name,
        '평점': rating,
        '주소': address,
        '리뷰수': review_count,
        '카테고리' : category,
        'rv' : rv
    })
    df.to_csv('result.csv', encoding='utf-8-sig')

if __name__ == "__main__":
    # 크롬을 여는 옵션을 세팅해줍니다
    options = webdriver.ChromeOptions()
    options.add_argument('disable-gpu')
    # 이때 아래줄을 주석처리하면 크롬창이 열려서 과정이 보이고, 아래처럼 있는 경우에는 크롬창을 백그라운드에서 띄웁니다
    # options.add_argument('headless')

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.delete_all_cookies()

    # 구글 지도로 들어가서 검색창이 뜰때까지 기다립니다
    googleMap_link = 'https://www.google.com/maps'
    driver.get(googleMap_link)
    wait_searchBar(driver)
    results = []

    # 검색어 입력
    search_name = "부산광역시 맛집"
    input_funtion(driver, search_name)
    time.sleep(5)
    # 정보를 빼올 시작 가게 번호 입니다 0부터 시작해서 증가합니다
    start = 0
    while True:
        try:
            # 검색 결과가 끝날때 까지 스크롤을 아래로 내리고 스크롤을 하는 과정을 반복합니다
            # 밑에 나오는 time.sleep(2)의 경우 인터넷 속도에 맞춰 조절
            scroll_element = driver.find_element_by_xpath('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]')
            driver.execute_script("arguments[0].scrollBy(0,2000)", scroll_element)
            time.sleep(3)
            driver.execute_script("arguments[0].scrollBy(0,2000)", scroll_element)
            time.sleep(3)
            driver.execute_script("arguments[0].scrollBy(0,2000)", scroll_element)

            # 전체 가게 검색결과를 받아옵니다
            stores = driver.find_elements_by_class_name('y7PRA')
            # 만약 검색이 끝난경우 종료합니다
            if stores[start] is None: raise Exception()
            # 가게 20개를 받아오고 start를 마지막 가게까지 늘려줍니다
            next_start = None
            for i in range(start, start + 20):
                try:
                    results.append(stores[i].text)
                    next_start = i + 1
                except:
                    next_start = i
                    break
            start = next_start
            time.sleep(3)
        except:
            break

    # 받아온 결과를 출력합니다. 아직 파싱되지 않은 정보입니다
    print(stores[0])

    # 데이터를 파싱합니다
    name, rating, review_count, address, category, rv = parse_data(results)

    # 파싱된 데이터를 csv로 저장합니다
    make_csv(name, rating, review_count, address, category, rv)

    # 크롬창을 종료합니다
    driver.quit()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

# google maps 는 정적페이지이다.

def set_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def maps_crawler(url, outputfile='./maps_reviews.csv'):
    driver = set_chrome_driver()
    driver.get(url)
    sleep(0.5)
    element = driver.find_element(By.CSS_SELECTOR, 'input#searchboxinput')
    element.send_keys("부산맛집")
    searchbutton = driver.find_element(By.CSS_SELECTOR, "button#searchbox-searchbutton")
    searchbutton.click()
    while True:
        sleep(3)
        # 컨테이너(가게) 데이터 수집 // div.section-result-content
        stores = driver.find_elements(By.CSS_SELECTOR, "div.section-result-content")

        for s in stores:
            # 가게 이름 데이터 수집 // h3.section-result-title
            title = s.find_element(By.CSS_SELECTOR, "h3.section-result-title").text

            # 평점 데이터 수집 // span.cards-rating-score
            # 평점이 없는 경우 에러 처리
            try:
                score = s.find_element(By.CSS_SELECTOR, "span.cards-rating-score").text
            except:
                score = "평점없음"

            # 가게 주소 데이터 수집 // span.section-result-location
            addr = s.find_element(By.CSS_SELECTOR, "span.section-result-location").text

            print(title, "/", score, "/", addr)

        # 다음페이지 버튼 클릭 하기
        # 다음페이지가 없는 경우(데이터 수집 완료) 에러 처리
        try:
            nextpage = driver.find_element(By.CSS_SELECTOR, "button#n7lv7yjyC35__section-pagination-button-next")
            nextpage.click()
        except:
            print("데이터 수집 완료.")
            break
    driver.close()

def main():
    url = "https://www.google.com/maps/"
    maps_crawler(url, 'com.google.maps.csv')

main()
# -*- coding: utf-8 -*-

import os
import time
import pandas as pd
import pyautogui
import random as r
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains

def wait(type_, time_):
    if type_== 0:
        driver.implicitly_wait(10)
    time.sleep(time_)
    
def get_data(driver, temp, current_index, titl, cate, addr):
    # 스크롤 다운
    first_content = driver.find_elements(by=By.CLASS_NAME, value="DU9Pgb")[-1]
    action = ActionChains(driver)
    action.move_to_element(first_content).click().perform()
    wait(1, 1)
    pyautogui.press("pagedown", presses=3, interval=0.2)

    # 자세히 클릭
    try:
        for _ in range(3):
            btn_mores = [i for i in driver.find_elements(by=By.TAG_NAME, value="button") if i.text=="자세히"]
            for btn_more in btn_mores:
                action = ActionChains(driver)
                action.move_to_element(btn_more).click().perform()
                wait(1, 0.2)
            pyautogui.press("pagedown", presses=3, interval=0.2)

        
    except:
        pass
    
    div_reviews_ori = driver.find_elements(by=By.CLASS_NAME, value="jftiEf")
    div_reviews = div_reviews_ori[current_index:]
    
    for div in div_reviews:
        # 리뷰 개수
        try:
            temp_text = div.text
            review_count = int(temp_text[temp_text.index("리뷰")+3:temp_text.index("개")])
        except:
            review_count = 0
        
        # 댓글
        content = div.find_element(by=By.CLASS_NAME, value="MyEned").text
        
        # 필터링
        if review_count < 3 or len(content) < 10:
            continue
        
        # 별점, 작성일
        spans = div.find_element(by=By.CLASS_NAME, value="DU9Pgb").find_elements(by=By.TAG_NAME, value="span")
        try:
            score = spans[1].get_attribute("aria-label")
        except:
            score = ""
        try:
            date = spans[2].text
        except:
            date = ""
        
        # 데이터 추가
        temp.append([titl, cate, addr, score, date, review_count, content])
    
    # 40개 가져오기 
    if len(temp)>=40 or current_index==len(div_reviews_ori): # 긁은 리뷰가 20개가 넘거나 아래로 내렸지만 더 댓글이 없는 경우
        return temp
    else: # 40개가 안 될 경우
        return get_data(driver, temp, len(div_reviews_ori), titl, cate, addr)


if __name__ == "__main__":
    # set data
    reviews = []

    # go to url
    driver = webdriver.Chrome("./chromedriver.exe")
    driver.maximize_window() 
    url = "https://www.google.co.kr/maps/?hl=ko"
    driver.get(url)

    # 부산 맛집 검색
    driver.find_element(by=By.ID, value="searchboxinput").send_keys("부산 맛집")
    wait(1, 1)
    driver.find_element(by=By.ID, value="searchbox-searchbutton").click()
    wait(0, 2)

    # get a tag
    alist = driver.find_elements(by=By.CLASS_NAME, value="hfpxzc")

    # 스크롤 다운 - 이 과정에서만 수동으로 내려 주면 더 좋습니다.
    alist[0].click()
    wait(1, 2)
    alist[0].click()
    wait(1, 1)
    prior = 0
    while True:
        for _ in range(5):
            pyautogui.press("pagedown")
            wait(1, 1+r.random())
        pyautogui.press("pageup")
        wait(0, 2)
        alist = driver.find_elements(by=By.CLASS_NAME, value="hfpxzc")
        if len(alist)==prior:
            break
        else:
            prior = len(alist)
    print("전체 개수: ", len(alist))
    
    # main loop
    i = 0
    alen = len(alist)
    while True:
        try:
            # 맛집 클릭
            alist = driver.find_elements(by=By.CLASS_NAME, value="hfpxzc")
            alist[i].click()
            wait(1, 2)

            if i!=0 and i%20==0:
                pyautogui.press("pagedown")

            # 상호명, 카테고리, 지역
            title = driver.find_element(by=By.CLASS_NAME, value="fontHeadlineLarge").text
            try:
                category = driver.find_element(by=By.CLASS_NAME, value="u6ijk").text
            except:
                category = ''
            address =  driver.find_element(by=By.CLASS_NAME, value="Io6YTe").text

            # 정렬 클릭
            div = driver.find_element(by=By.CLASS_NAME, value="Hu9e2e")
            div = div.find_element(by=By.CLASS_NAME, value="m6QErb")
            btns = div.find_elements(by=By.CLASS_NAME, value="S9kvJb")
            btn_sort = [i for i in btns if i.get_attribute("data-value")=="정렬"][0]
            action = ActionChains(driver)
            action.move_to_element(btn_sort).click().perform()
            wait(1, 1.5)

            # 최신순 클릭
            ul_list = driver.find_elements(by=By.TAG_NAME, value="ul")
            ul = [i for i in ul_list if i.get_attribute("role")=="menu"][0]
            ul.find_elements(by=By.TAG_NAME, value="li")[1].click()
            wait(1, 2)

            # 한 달이내 리뷰 확인
            recent_text = driver.find_element(by=By.CLASS_NAME, value="rsqaWe").text
            if "달" in recent_text and "년" in recent_text:
                i +=1
                continue

            # 스크롤 다운
            first_content = driver.find_element(by=By.CLASS_NAME, value="DU9Pgb")
            action = ActionChains(driver)
            action.move_to_element(first_content).click().perform()

            # 데이터 수집 및 추가
            temp = get_data(driver, [], 0, title, category, address)
            reviews += temp
            #print(len(reviews))
        except Exception as e:
            print(e)
            pyautogui.press("pagedown")
            i -= 1

        i +=1
        if i==alen:
            break

# data save
df = pd.DataFrame(reviews)
df.columns = ["name", "category", "address", "score", "date", "reviewers_reivew_count", "content"]
df.to_excel("data_result.xlsx")
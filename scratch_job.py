import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import json
import random
import os

# --- 1. 配置和全局变量 ---

# 关键词字典
changye = ['航空航天']

changye_urls = [
]
with open('urls.txt', 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f.readlines()]
    changye_urls.append(urls)
changye_xueke_dict = dict(zip(changye, changye_urls))
MAX_PAGES_PER_KEYWORD = 2 # 每个关键词最多爬取2页

el_img_url = './descendant-or-self::IMG[contains(@class,"comlogo")]'
el_jname = './descendant-or-self::SPAN[contains(@class,"jname text-cut")]'
el_sal = './descendant-or-self::SPAN[contains(@class,"sal shrink-0")]'
el_tags = './descendant-or-self::DIV[contains(@class,"tags")]'
el_cname_link = './descendant-or-self::A[contains(@class,"cname text-cut")]'
el_cname = './descendant-or-self::A[contains(@class,"cname text-cut")]'
el_dc = './descendant-or-self::SPAN[contains(@class,"dc text-cut")]'
el_dc2 = './descendant-or-self::SPAN[contains(@class,"dc shrink-0")]'
el_dc3 = './descendant-or-self::SPAN[contains(@class,"dc shrink-0")][2]'
el_tips = './descendant-or-self::SPAN[contains(@class,"tip shrink-0")]'
el_shrink0 = './descendant-or-self::DIV[@class="shrink-0"]'
def handle_slider_verification(driver):
    """处理可能出现的滑块验证。"""
    try:
        sleep(3)
        slider = driver.find_element(By.ID, "nc_1_n1z")
        track = driver.find_element(By.ID, "nc_1_wrapper")
        print("  - 检测到滑块验证，正在尝试破解...")
        distance = track.size['width'] - slider.size['width']
        actions = ActionChains(driver)
        actions.click_and_hold(slider)
        current_pos = 0
        while current_pos < distance:
            move = random.randint(20, 40)
            actions.move_by_offset(move, 0)
            current_pos += move
            sleep(random.uniform(0.05, 0.2))
        actions.release()
        actions.perform()
        print("  - 滑块验证尝试完成。")
        sleep(3)
        return True
    except NoSuchElementException:
        print("  - 未检测到滑块验证。")
        return False
    except Exception as e:
        print(f"  - 处理滑块验证时出错: {e}")
        return False

def scrape_all_jobs(level,xpath):
    """根据关键词字典爬取51job的职位详情，并保存为指定格式的Excel。"""
    print("正在初始化浏览器...")
    chrome_driver_path = './chromedriver.exe'
    service = Service(chrome_driver_path)
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    try:
        web = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"启动浏览器失败: {e}")
        return

    all_results = []
    job_id_counter = 1
    base_url = 'https://we.51job.com/pc/search'

    try:
        for industry, keywords in changye_xueke_dict.items():
            print(f"\n开始处理产业: '{industry}'")
            for keyword in keywords:
                print(f"\n-- 正在搜索关键词: '{keyword}' --")
                search_url = f'{keyword}&searchType=2&sortType=0&metro='
                web.get(search_url)
                sleep(5)
                # original_window = web.current_window_handle

                page = 0
                while True:
                    handle_slider_verification(web)
                    
                    print(f"\n  处理第 {page + 1} 页...")
                    try:
                        if page==0:
                            toggle_button = web.find_element(By.XPATH, '//div[@class="carrybox"]/span[1]') # [0]
                            toggle_button.click()
                            sleep(2)
                            option_button = web.find_element(By.XPATH, xpath)
                            option_button.click()
                            sleep(2)
                        job_items = web.find_elements(By.XPATH, '//div[contains(@class, "joblist-item-job-wrapper")]')
                        if not job_items:
                            print(f"    页面上没有找到职位，结束当前关键词。")
                            break
                        print(f"    找到 {len(job_items)} 个职位，开始处理...")
                    except NoSuchElementException:
                        print(f"    无法定位到职位列表，结束当前关键词。")
                        break
                    for i in range(len(job_items)):
                        current_job_item = web.find_elements(By.XPATH, '//div[contains(@class, "joblist-item-job-wrapper")]')[i]
                        result = {
                            "图片":current_job_item.find_element(By.XPATH, el_img_url).get_attribute('src') if current_job_item.find_elements(By.XPATH, el_img_url) else "",
                            "职位名称":current_job_item.find_element(By.XPATH, el_jname).text if current_job_item.find_elements(By.XPATH, el_jname) else "",
                            "公司名称":current_job_item.find_element(By.XPATH, el_cname).text if current_job_item.find_elements(By.XPATH, el_cname) else "",    
                            "公司链接":current_job_item.find_element(By.XPATH, el_cname_link).get_attribute('href') if current_job_item.find_elements(By.XPATH, el_cname_link) else "",
                            "薪资":current_job_item.find_element(By.XPATH, el_sal).text if current_job_item.find_elements(By.XPATH, el_sal) else "",
                            "dc":current_job_item.find_element(By.XPATH, el_dc).text if current_job_item.find_elements(By.XPATH, el_dc) else "",
                            "tips":current_job_item.find_element(By.XPATH, el_tips).text if current_job_item.find_elements(By.XPATH, el_tips) else "",
                            "关键词":current_job_item.find_element(By.XPATH, el_tags).text if current_job_item.find_elements(By.XPATH, el_tags) else "",
                        }
                        # print(result)
                    # result = {
                    #     "图片": web.find_element(By.XPATH, el_img_url).get_attribute('src') if web.find_elements(By.XPATH, el_img_url) else "",
                    #     "职位名称": web.find_element(By.XPATH, el_jname).text if web.find_elements(By.XPATH, el_jname) else "",
                    #     "公司名称": web.find_element(By.XPATH, el_cname).text if web.find_elements(By.XPATH, el_cname) else "",
                    #     "公司链接": web.find_element(By.XPATH, el_cname_link).get_attribute('href') if web.find_elements(By.XPATH, el_cname_link) else "",
                    #     "薪资": web.find_element(By.XPATH, el_sal).text if web.find_elements(By.XPATH, el_sal) else "",
                    #     "工作地点": web.find_element(By.XPATH, el_dc).text if web.find_elements(By.XPATH, el_dc) else "",
                    #     "发布时间": web.find_element(By.XPATH, el_tips).text if web.find_elements(By.XPATH, el_tips) else "",
                    #     "标签": web.find_element(By.XPATH, el_tags).text if web.find_elements(By.XPATH, el_tags) else "",
                    # }
                   
                        all_results.append(result)
                    # --- 翻页逻辑 ---
                    try:
                        next_button = web.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div[2]/div/div[2]/div/div[3]/div/div/div/button[2]')
                        if next_button.get_attribute('disabled') is not None:
                            print("  已到达最后一页，结束当前关键词。")
                            break
                        else:
                            print("  点击下一页...")
                            page += 1
                            next_button.click()
                            sleep(0.5) # 等待新页面加载
                    except NoSuchElementException:
                        print("  未找到下一页按钮，结束当前关键词。")
                        break
    except Exception as e:
        print(f"发生严重错误: {e}")
    finally:
        web.quit()
        if all_results:
            print(f"\n爬取结束，共获得 {len(all_results)} 条数据。")
            df = pd.DataFrame(all_results)
            output_filename = f"./6/{level}.xlsx"
            try:
                df.to_excel(output_filename, index=False, engine='openpyxl')
                print(f"数据已成功保存到: {output_filename}")
            except Exception as e:
                print(f"保存到Excel失败: {e}")
        else:
            print("未能爬取到任何有效数据。")

if __name__ == '__main__':
    el_bachelor = '//div[@class="launchbox open"]/div[2]/div[1]/div[2]/a[4]'
    el_graduate = '//div[@class="launchbox open"]/div[2]/div[1]/div[2]/a[5]'
    el_master = '//div[@class="launchbox open"]/div[2]/div[1]/div[2]/a[6]'
    el_phd = '//div[@class="launchbox open"]/div[2]/div[1]/div[2]/a[7]'
    el_map = {
        # "bachelor": el_bachelor,
        # "graduate": el_graduate,
        "master": el_master,
        "phd": el_phd
    }
    for level,xpath in el_map.items():
        print(f"\n\n================ 开始爬取学历层次: {level} ================\n\n")
        scrape_all_jobs(level=level,xpath=xpath)

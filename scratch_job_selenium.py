from concurrent.futures import ThreadPoolExecutor
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
from threading import Lock
import subprocess
import time

# --- 1. 配置和全局变量 ---

# 关键词字典
changye = ["新一代信息技术","冶金工程","有色金属"]

changye_urls = [
]
for cy in changye:
    url_xlsx = f'./{cy}/新建 XLSX 工作表.xlsx'
    data_xlsx = pd.read_excel(url_xlsx)
    urls = data_xlsx.iloc[:, 0].tolist()
    changye_urls.append(urls)
changye_xueke_dict = dict(zip(changye, changye_urls))
MAX_PAGES_PER_KEYWORD = 2 # 每个关键词最多爬取2页

# 全局锁和结果列表
result_lock = Lock()
all_results = {}

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
el_shrink0 = './descendant-or-self::DIV[contains(@class,"shrink-0")]'
el_shrink3 = './descendant-or-self::DIV[@class="shrink-0"]'
el_dc1 = './descendant-or-self::SPAN[contains(@class,"dc shrink-0")][2]'

def disable_adapter(adapter_name="以太网"):
    """禁用网络适配器"""
    try:
        print(f"\n⚠ 禁用网络适配器: {adapter_name}...")
        cmd = f'netsh interface set interface "{adapter_name}" disabled'
        subprocess.run(cmd, shell=True, capture_output=True, check=False)
        print(f"✓ 网络适配器已禁用")
        sleep(2)
    except Exception as e:
        print(f"✗ 禁用网络适配器失败: {e}")

def enable_adapter(adapter_name="以太网"):
    """启用网络适配器"""
    try:
        print(f"\n✓ 启用网络适配器: {adapter_name}...")
        cmd = f'netsh interface set interface "{adapter_name}" enabled'
        subprocess.run(cmd, shell=True, capture_output=True, check=False)
        print(f"✓ 网络适配器已启用")
        sleep(2)
    except Exception as e:
        print(f"✗ 启用网络适配器失败: {e}")

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

def scrape_industry_level(industry, keywords, level, xpath):
    """爬取单个产业+学历层次的职位数据"""
    print(f"\n-- 线程启动: 产业='{industry}', 学历='{level}' --")
    chrome_driver_path = './chromedriver.exe'
    service = Service(chrome_driver_path)
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    try:
        web = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"启动浏览器失败: {e}")
        return []

    thread_results = []
    base_url = 'https://we.51job.com/pc/search'

    try:
        # 处理该产业的所有关键词
        for keyword in keywords:
            print(f"\n  处理关键词: '{keyword}'")
            search_url = f'{keyword}&searchType=2&sortType=0&metro='
            web.get(search_url)
            sleep(5)

            page = 0
            while True:
                handle_slider_verification(web)
                
                print(f"    页码: {page + 1}")
                try:
                    if page == 0:
                        toggle_button = web.find_element(By.XPATH, '//div[@class="carrybox"]/span[1]')
                        toggle_button.click()
                        sleep(2)
                        option_button = web.find_element(By.XPATH, xpath)
                        option_button.click()
                        sleep(2)
                    job_items = web.find_elements(By.XPATH, '//div[contains(@class, "joblist-item-job-wrapper")]')
                    if not job_items:
                        print(f"      页面上没有找到职位，结束当前关键词。")
                        break
                    print(f"      找到 {len(job_items)} 个职位，开始处理...")
                except NoSuchElementException:
                    print(f"      无法定位到职位列表，结束当前关键词。")
                    break
                
                for i in range(len(job_items)):
                    current_job_item = web.find_elements(By.XPATH, '//div[contains(@class, "joblist-item-job-wrapper")]')[i]
                    result = {
                        "标题": current_job_item.find_element(By.XPATH, el_jname).text if current_job_item.find_elements(By.XPATH, el_jname) else "",
                        "图片": current_job_item.find_element(By.XPATH, el_img_url).get_attribute('src') if current_job_item.find_elements(By.XPATH, el_img_url) else "",
                        "sal": current_job_item.find_element(By.XPATH, el_sal).text if current_job_item.find_elements(By.XPATH, el_sal) else "",
                        "关键词": current_job_item.find_element(By.XPATH, el_tags).text if current_job_item.find_elements(By.XPATH, el_tags) else "",
                        "名称_链接": current_job_item.find_element(By.XPATH, el_cname_link).get_attribute('href') if current_job_item.find_elements(By.XPATH, el_cname_link) else "",
                        "名称": current_job_item.find_element(By.XPATH, el_cname).text if current_job_item.find_elements(By.XPATH, el_cname) else "",    
                        "dc": current_job_item.find_element(By.XPATH, el_dc).text if current_job_item.find_elements(By.XPATH, el_dc) else "",
                        "dc1": current_job_item.find_element(By.XPATH, el_dc2).text if current_job_item.find_elements(By.XPATH, el_dc2) else "",
                        "tips": current_job_item.find_element(By.XPATH, el_tips).text if current_job_item.find_elements(By.XPATH, el_tips) else "",
                        "dc2": current_job_item.find_element(By.XPATH, el_dc1).text if current_job_item.find_elements(By.XPATH, el_dc1) else "",
                        "shrink0": current_job_item.find_element(By.XPATH, el_shrink0).text if current_job_item.find_elements(By.XPATH, el_shrink0) else "",
                        "shrink3": current_job_item.find_element(By.XPATH, el_shrink3).text if current_job_item.find_elements(By.XPATH, el_shrink3) else "",
                    }
                    thread_results.append(result)
                
                # --- 翻页逻辑 ---
                try:
                    next_button = web.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div[2]/div/div[2]/div/div[3]/div/div/div/button[2]')
                    if next_button.get_attribute('disabled') is not None:
                        print("      已到达最后一页，结束当前关键词。")
                        break
                    else:
                        print("      点击下一页...")
                        page += 1
                        next_button.click()
                        sleep(0.5)
                except NoSuchElementException:
                    print("      未找到下一页按钮，结束当前关键词。")
                    break
    except Exception as e:
        print(f"线程错误: {e}")
    finally:
        web.quit()
        print(f"线程完成: 产业='{industry}', 学历='{level}', 获取 {len(thread_results)} 条数据")
    
    return thread_results

def scrape_all_jobs():
    """使用线程池爬取所有职位 (4学历 × 3产业 = 12个线程)"""
    
    el_bachelor = '//div[@class="launchbox open"]/div[2]/div[1]/div[2]/a[4]'
    el_graduate = '//div[@class="launchbox open"]/div[2]/div[1]/div[2]/a[5]'
    el_master = '//div[@class="launchbox open"]/div[2]/div[1]/div[2]/a[6]'
    el_phd = '//div[@class="launchbox open"]/div[2]/div[1]/div[2]/a[7]'
    el_map = {
        "大专": el_bachelor,
        "本科": el_graduate,
        "硕士": el_master,
        "博士": el_phd
    }
    
    print("================ 开始多线程爬取 ================")
    print(f"总线程数: {len(el_map)} 学历 × {len(changye_xueke_dict)} 产业 = {len(el_map) * len(changye_xueke_dict)} 线程\n")
    
    # 对每个产业进行处理
    industries = list(changye_xueke_dict.keys())
    for industry_idx, industry in enumerate(industries):
        print(f"\n{'='*50}")
        print(f"开始爬取产业: '{industry}' ({industry_idx + 1}/{len(industries)})")
        print(f"{'='*50}")
        
        # 使用ThreadPoolExecutor，该产业的所有学历并发爬取
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            for level, xpath in el_map.items():
                keywords = changye_xueke_dict[industry]
                future = executor.submit(scrape_industry_level, industry, keywords, level, xpath)
                futures.append((industry, level, future))
            
            # 收集结果并立即保存
            print("\n================ 收集并保存结果 ================")
            for industry_name, level, future in futures:
                results_list = future.result()
                if results_list:
                    df = pd.DataFrame(results_list)
                    output_filename = f"./{industry_name}/{industry_name}-{level}-刘雨蘅.xlsx"
                    try:
                        df.to_excel(output_filename, index=False, engine='openpyxl')
                        print(f"✓ 已保存: {output_filename} ({len(results_list)} 条数据)")
                    except Exception as e:
                        print(f"✗ 保存失败: {output_filename} - {e}")
                else:
                    print(f"- 无数据: {industry_name}-{level}")
        
if __name__ == '__main__':
    scrape_all_jobs()
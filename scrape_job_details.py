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

# 关键词字典 (参考 51job_save.py)
changye = ['新型医疗器械']
changye_keywords = [
    [
        "光学技术", "多模态融合", "微生物检测", "彩超", "B超", "医学CT", "MRI", 
        "POCT", "TLA", "免疫诊断", "基因检测", "多模态交互", "心电监测仪",
        "无创血糖仪", "智能手环", "智能鞋", "智能鞋垫"
    ]
]
changye_xueke_dict = dict(zip(changye, changye_keywords))

def handle_slider_verification(driver):
    """
    处理可能出现的滑块验证。
    代码来自 51job_save.py
    """
    try:
        sleep(1) # 等待一下，让验证码元素加载
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
        sleep(3) # 等待页面跳转
        return True
    except NoSuchElementException:
        print("  - 未检测到滑块验证。")
        return False
    except Exception as e:
        print(f"  - 处理滑块验证时出错: {e}")
        return False

def scrape_all_jobs():
    """
    根据关键词字典爬取51job的职位详情，并保存为指定格式的Excel。
    """
    # --- 2. 初始化Selenium ---
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
        # --- 3. 遍历行业和关键词 ---
        for industry, keywords in changye_xueke_dict.items():
            if job_id_counter%10 == 0:
                #save 
                if all_results:
                    print(f"\n爬取结束，共获得 {len(all_results)} 条数据。")
                    df = pd.DataFrame(all_results)
                    output_filename = "comprehensive_job_scrape.xlsx"
                    try:
                        df.to_excel(output_filename, index=False, engine='openpyxl')
                        print(f"数据已成功保存到: {output_filename}")
                    except Exception as e:
                        print(f"保存到Excel失败: {e}")
                else:
                    print("未能爬取到任何有效数据。")
                
            print(f"\n开始处理产业: '{industry}'")
            for keyword in keywords:
                print(f"\n-- 正在搜索关键词: '{keyword}' --")
                
                # --- 4. 打开搜索页 ---
                search_url = f'{base_url}?keyword={keyword}&searchType=2&sortType=0&metro='
                web.get(search_url)
                sleep(10)

                original_window = web.current_window_handle
                
                try:
                    job_items = web.find_elements(By.XPATH, '//div[contains(@class, "joblist-item-job-wrapper")]')
                    if not job_items:
                        print(f"  关键词 '{keyword}' 没有找到任何职位，跳过。")
                        continue
                    print(f"  找到 {len(job_items)} 个职位，开始处理...")
                except NoSuchElementException:
                    print(f"  无法定位到 '{keyword}' 的职位列表，跳过。")
                    continue

                # --- 5. 遍历职位列表 ---
                for i in range(len(job_items)):
                    try:
                        # 重新获取元素以避免StaleElementReferenceException
                        current_job_item = web.find_elements(By.XPATH, '//div[contains(@class, "joblist-item-job-wrapper")]')[i]

                        # --- 6. 提取结构化数据 ---
                        sensors_data_element = current_job_item.find_element(By.XPATH, ".//div[@sensorsdata]")
                        job_attributes_str = sensors_data_element.get_attribute('sensorsdata')
                        job_attributes = json.loads(job_attributes_str)

                        print(f"  处理第 {i+1} 个职位: {job_attributes.get('jobTitle', 'N/A')}")

                        # --- 7. 点击进入详情页 ---
                        current_job_item.find_element(By.XPATH, './/span[contains(@class, "jname")]').click()
                        sleep(2)

                        # --- 8. 切换窗口并处理验证 ---
                        for handle in web.window_handles:
                            if handle != original_window:
                                web.switch_to.window(handle)
                                break
                        
                        handle_slider_verification(web)
                        sleep(3)

                        # --- 9. 提取详情页信息 ---
                        detail_url = web.current_url
                        try:
                            job_desc_element = web.find_element(By.XPATH, '//div[contains(@class, "bmsg job_msg inbox")]')
                            job_description = job_desc_element.text.strip()
                            print(job_description)
                        except NoSuchElementException:
                            job_description = "N/A"

                        # --- 10. 组装数据 (格式参考51job_save.py) ---
                        final_result = {
                            'ID': job_id_counter,
                            '产业': industry,
                            '学科': "待分析",  # 此脚本不进行分析，留空或设为默认值
                            '招聘详情文本': job_description,
                            'URL': detail_url,
                            'jobTitle': job_attributes.get('jobTitle'),
                            '负责人': "刘雨蘅"
                        }
                        print(final_result)
                        all_results.append(final_result)
                        job_id_counter += 1

                    except Exception as e:
                        print(f"    处理单个职位时出错: {e}")
                    finally:
                        # --- 11. 切回主窗口 ---
                        if web.current_window_handle != original_window:
                            web.close()
                        web.switch_to.window(original_window)
                        sleep(1)

    except Exception as e:
        print(f"发生严重错误: {e}")
    finally:
        # --- 12. 保存结果 ---
        web.quit()
        if all_results:
            print(f"\n爬取结束，共获得 {len(all_results)} 条数据。")
            df = pd.DataFrame(all_results)
            output_filename = "comprehensive_job_scrape.xlsx"
            try:
                df.to_excel(output_filename, index=False, engine='openpyxl')
                print(f"数据已成功保存到: {output_filename}")
            except Exception as e:
                print(f"保存到Excel失败: {e}")
        else:
            print("未能爬取到任何有效数据。")

if __name__ == '__main__':
    scrape_all_jobs()

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

changye_keywords = [
 [
    # "军用芯片",
    # "卫星互联网",
    # "卫星发射",
    # "卫星总装",
    # "卫星数据应用",
    # "卫星通信网络",
    # "子级独立测试",
    # "导航卫星",
    # "导航系统客户端",
    # "导航终端抗干扰技术",
    # "扩散连接",
    # "模块化集成技术",
    # "海洋卫星",
    # "熔模精密铸造",
    # "航电系统设计",
    # "航空航天GNSS算法",
    # "航空航天嵌入式软件",
    # "航空航天成型复合材料",
    # "航空航天电源模块设计",
    # "轻质合金材料结构",
    # "通信卫星",
    # "通导一体化",
    # "遥感",
    # "遥感卫星",
    # "隐身材料",
    # "飞机数据分析",
    # "飞行器强度",
    # "高性能金属材料",
    # "高温合金",
    # "5G移动通信网络",
    # "5G通讯设备",
    # "GEO轨道",
    # "GPS",
    # "光纤互联技术",
    # "军用飞机",
    # "制导控制",
    # "北斗卫星",
    # "卫星发射",
    # "卫星控制系统",
    # "卫星研发测试",
    # "卫星设计",
    # "卫星通信系统",
    # "地面系统",
    # "地面设备制造",
    # "客运航空",
    # "弹体结构",
    # "弹道设计",
    # "强击机",
    # "控制分系统研发",
    # "推进剂液位测量技术",
    # "整机制造",
    # "无人机负载设备",
    # "无线传感技术",
    # "机场运营",
    # "民用飞机",
    # "民航安全",
    # "民航运营",
    # "流体动力电源技术",
    # "火箭发动机",
    # "火箭总体设计",
    # "火箭控制系统研发",
    # "热成型设备",
    # "燃气轮机",
    # "物联网星座",
    # "特种作业",
    # "特种设备加工",
    # "电子对抗",
    # "电静压伺服机构",
    # "空间系统",
    "航空器动力设计",
    "航空器总体设计",
    "航空器气动设计",
    "航空器结构设计",
    "航空航天产品销售",
    "航空航天仪器",
    "航空航天伺服控制系统",
    "航空航天信息传输",
    "航空航天发动机研制",
    "航空航天外贸",
    "航空航天控制与检测技术",
    "航空航天控制系统",
    "航空航天红外",
    "航空航天设备系统保障",
    "航空航天设备设计制造",
    "航空锻造",
    "训练飞行",
    "货运航空",
    "跟踪测轨",
    "载荷研发测试",
    "运载火箭",
    "通讯导航系统",
    "遥感设备与服务",
    "降落组件",
    "飞控系统",
    "飞机航线管理",
    "飞机起落架",
    "飞行器电机控制"
]
]
changye_xueke_dict = dict(zip(changye, changye_keywords))
MAX_PAGES_PER_KEYWORD = 1 # 每个关键词最多爬取2页

def handle_slider_verification(driver):
    """处理可能出现的滑块验证。"""
    try:
        sleep(1)
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

def scrape_all_jobs():
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
                search_url = f'{base_url}?keyword={keyword}&searchType=2&sortType=0&metro='
                web.get(search_url)
                sleep(12)
                original_window = web.current_window_handle

                for page in range(MAX_PAGES_PER_KEYWORD):
                    print(f"\n  处理第 {page + 1} 页...")
                    try:
                        job_items = web.find_elements(By.XPATH, '//div[contains(@class, "joblist-item-job-wrapper")]')
                        if not job_items:
                            print(f"    页面上没有找到职位，结束当前关键词。")
                            break
                        print(f"    找到 {len(job_items)} 个职位，开始处理...")
                    except NoSuchElementException:
                        print(f"    无法定位到职位列表，结束当前关键词。")
                        break

                    for i in range(len(job_items)):
                        try:
                            current_job_item = web.find_elements(By.XPATH, '//div[contains(@class, "joblist-item-job-wrapper")]')[i]
                            sensors_data_element = current_job_item.find_element(By.XPATH, ".//div[@sensorsdata]")
                            job_attributes_str = sensors_data_element.get_attribute('sensorsdata')
                            job_attributes = json.loads(job_attributes_str)
                            print(f"    处理职位: {job_attributes.get('jobTitle', 'N/A')}")

                            current_job_item.find_element(By.XPATH, './/span[contains(@class, "jname")]').click()
                            sleep(2)

                            for handle in web.window_handles:
                                if handle != original_window:
                                    web.switch_to.window(handle)
                                    break
                            
                            handle_slider_verification(web)
                            sleep(2)

                            detail_url = web.current_url
                            try:
                                job_desc_element = web.find_element(By.XPATH, '//div[contains(@class, "bmsg job_msg inbox")]')
                                job_description = job_desc_element.text.strip()
                            except NoSuchElementException:
                                job_description = "N/A"
                                continue

                            final_result = {
                                'ID': job_id_counter, '产业': industry, '学科': "待分析",
                                '招聘详情文本': job_description, 'URL': detail_url, '负责人': "刘雨蘅",
                                
                            }
                            print(detail_url)
                            all_results.append(final_result)
                            job_id_counter += 1
                        except Exception as e:
                            # print(f"      处理单个职位时出错: {e}")
                            pass
                        finally:
                            if web.current_window_handle != original_window:
                                web.close()
                            web.switch_to.window(original_window)
                            sleep(1)
                    
                    # --- 翻页逻辑 ---
                    try:
                        next_button = web.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div[2]/div/div[2]/div/div[3]/div/div/div/button[2]')
                        if next_button.get_attribute('disabled') is not None:
                            print("  已到达最后一页，结束当前关键词。")
                            break
                        else:
                            print("  点击下一页...")
                            next_button.click()
                            sleep(5) # 等待新页面加载
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
            output_filename = "./3/comprehensive_job_scrape_航空航天_2.xlsx"
            try:
                df.to_excel(output_filename, index=False, engine='openpyxl')
                print(f"数据已成功保存到: {output_filename}")
            except Exception as e:
                print(f"保存到Excel失败: {e}")
        else:
            print("未能爬取到任何有效数据。")

if __name__ == '__main__':
    scrape_all_jobs()

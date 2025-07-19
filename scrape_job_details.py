import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from time import sleep

def scrape_job_details(keyword, max_jobs=10):
    """
    根据关键词爬取51job的职位详情。

    :param keyword: 要搜索的职位关键词。
    :param max_jobs: 最多爬取的职位数量。
    """
    # --- 1. 初始化Selenium ---
    print("正在初始化浏览器...")
    chrome_driver_path = './chromedriver.exe'
    service = Service(chrome_driver_path)
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # 如果需要无头模式，取消此行注释
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    try:
        web = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"启动浏览器失败，请确保chromedriver.exe在当前目录下，并且与您的Chrome浏览器版本匹配。")
        print(f"错误信息: {e}")
        return

    # --- 2. 打开搜索结果页 ---
    search_url = f'https://we.51job.com/pc/search?keyword={keyword}&searchType=2&sortType=0&metro='
    print(f"正在打开搜索页面: {search_url}")
    web.get(search_url)
    sleep(10)  # 等待页面完全加载

    # --- 3. 定位并遍历职位列表 ---
    try:
        job_items = web.find_elements(By.XPATH, '//div[contains(@class, "joblist-item-job-wrapper")]')
        if not job_items:
            print("在页面上没有找到职位列表。")
            web.quit()
            return
        print(f"在第一页找到 {len(job_items)} 个职位，将尝试处理最多 {max_jobs} 个。")
    except NoSuchElementException:
        print("无法定位到职位列表容器。")
        web.quit()
        return

    results = []
    original_window = web.current_window_handle

    for i, job_item in enumerate(job_items):
        if len(results) >= max_jobs:
            print(f"已达到最大处理数量 ({max_jobs})，停止爬取。")
            break

        try:
            # --- 4. 提取列表页信息 ---
            job_title = job_item.find_element(By.XPATH, './/span[contains(@class, "jname")]').text
            company_name = job_item.find_element(By.XPATH, './/a[contains(@class, "cname")]').text
            print(f"\n正在处理第 {i+1} 个职位: {job_title} @ {company_name}")

            # --- 5. 点击进入详情页 ---
            job_item.find_element(By.XPATH, './/span[contains(@class, "jname")]').click()
            sleep(2)

            # --- 6. 切换到新窗口 ---
            for window_handle in web.window_handles:
                if window_handle != original_window:
                    web.switch_to.window(window_handle)
                    break
            
            sleep(2) # 等待新页面加载

            # --- 7. 提取详情页信息 ---
            detail_url = web.current_url
            
            # 尝试提取职位描述，不同页面结构可能不同，这里用一个比较通用的XPath
            try:
                job_description_element = web.find_element(By.XPATH, '//div[contains(@class, "bmsg job_msg inbox")]')
                job_description = job_description_element.text.strip()
                print(f"  - 提取到职位描述：{job_description}")
            except NoSuchElementException:
                job_description = "未能自动提取职位描述"
            
            print(f"  - 详情页URL: {detail_url}")
            
            results.append({
                "职位名称": job_title,
                "公司名称": company_name,
                "详情页URL": detail_url,
                "职位描述": job_description
            })

            # --- 8. 关闭详情页并切回 ---
            web.close()
            web.switch_to.window(original_window)
            sleep(1)

        except Exception as e:
            print(f"  - 处理职位时出错: {e}")
            # 如果出错，尝试切回主窗口继续
            if web.current_window_handle != original_window:
                try:
                    web.close()
                except: pass
                web.switch_to.window(original_window)
            continue
    
    # --- 9. 保存结果到Excel ---
    web.quit()
    if results:
        print(f"\n爬取完成，共获得 {len(results)} 条职位信息。")
        df = pd.DataFrame(results)
        output_filename = f"{keyword}_job_details.xlsx"
        try:
            df.to_excel(output_filename, index=False, engine='openpyxl')
            print(f"数据已成功保存到: {output_filename}")
        except Exception as e:
            print(f"保存到Excel失败: {e}")
    else:
        print("没有成功爬取到任何职位信息。")


if __name__ == '__main__':
    # 设置要搜索的关键词和最大爬取数量
    SEARCH_KEYWORD = "python工程师"
    MAX_JOBS_TO_SCRAPE = 70
        
    changye = ['新型医疗器械']
    changye_keywords = [
        [
            "光学技术",
            "多模态融合",
            "微生物检测",
            "彩超",
            "B超",
            "医学CT",
            "MRI", 
            "POCT",
            "TLA",
            "免疫诊断",
            "基因检测",
            "多模态交互",
            "心电监测仪",
            "无创血糖仪",
            "智能手环",
            "智能鞋",
            "智能鞋垫"
        ]
    ]
    changye_xueke_dict = dict(zip(changye, changye_keywords))
    
    scrape_job_details(SEARCH_KEYWORD, MAX_JOBS_TO_SCRAPE)

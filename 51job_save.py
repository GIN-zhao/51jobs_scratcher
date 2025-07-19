from datetime import datetime
from time import sleep
import json
import ktool
import pandas as pd
import google.generativeai as genai
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import random
import os

# 配置Gemini API
genai.configure(api_key="AIzaSyB4k6UrOve6L-ynyGmn1AfGX7mvjtJB2s4")  # 请替换为你的API密钥
model = genai.GenerativeModel('gemini-2.5-pro')

url = 'https://we.51job.com/pc/search?keyword=&searchType=2&sortType=0&metro='
opt = Options()
opt.add_argument("--headless")
opt.add_experimental_option('useAutomationExtension', False)
opt.add_experimental_option('excludeSwitches', ['enable-automation'])
opt.add_argument('--disable-blink-features=AutomationControlled')

changye = ['新型医疗器械']
changye_keywords = [
    [
        # "光学技术",
        # "多模态融合",
        # "微生物检测",
        # "彩超",
        # "B超",
        # "医学CT",
        # "MRI", 
        # "POCT",
        # "TLA",
        # "免疫诊断",
        # "基因检测",
        "多模态交互",
        # "心电监测仪",
        # "无创血糖仪",
        # "智能手环",
        # "智能鞋",
        # "智能鞋垫"
    ]
]
changye_xueke_dict = dict(zip(changye, changye_keywords))

# 学科列表
disciplines = [
    "生物学", "机械工程", "仪器科学与技术", "材料科学与工程", 
    "电气工程", "电子科学与技术", "信息与通信工程", "控制科学与技术",
    "计算机科学与技术", "生物医学工程", "生物工程", "基础医学", 
    "临床医学", "药学"
]

# 全局变量
all_results = []
job_id = 1
SAVE_INTERVAL = 5  # 每处理5个职位保存一次
BACKUP_INTERVAL = 10  # 每处理10个职位创建一个备份

# 创建保存文件夹
if not os.path.exists("crawl_data"):
    os.makedirs("crawl_data")
if not os.path.exists("crawl_data/backups"):
    os.makedirs("crawl_data/backups")

# 生成文件名
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
main_filename = f"crawl_data/招聘分析结果_{timestamp}.xlsx"
temp_filename = f"crawl_data/temp_招聘分析结果_{timestamp}.xlsx"

def save_data_to_file(data, filename, is_temp=False):
    """保存数据到Excel文件"""
    try:
        if data:
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False, engine='openpyxl')
            if not is_temp:
                print(f"数据已保存到: {filename}")
            else:
                print(f"临时数据已保存 (共 {len(data)} 条记录)")
        return True
    except Exception as e:
        print(f"保存数据失败: {e}")
        return False

def create_backup(data):
    """创建数据备份"""
    try:
        backup_filename = f"crawl_data/backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        if save_data_to_file(data, backup_filename):
            print(f"备份已创建: {backup_filename}")
        return True
    except Exception as e:
        print(f"创建备份失败: {e}")
        return False

def load_existing_data():
    """加载已存在的数据（用于程序重启恢复）"""
    global all_results, job_id
    
    if os.path.exists(temp_filename):
        try:
            df = pd.read_excel(temp_filename)
            all_results = df.to_dict('records')
            if all_results:
                job_id = max([item['ID'] for item in all_results]) + 1
                print(f"恢复了 {len(all_results)} 条已爬取的数据，从ID {job_id} 继续")
            return True
        except Exception as e:
            print(f"恢复数据失败: {e}")
            return False
    return False

def handle_slider_verification(driver):
    try:
        # 检查是否存在滑块验证
        sleep(1) # 等待一下，让验证码元素加载
        slider = driver.find_element(By.ID, "nc_1_n1z")
        track = driver.find_element(By.ID, "nc_1_wrapper")
        
        print("检测到滑块验证，正在尝试破解...")

        # 计算需要移动的距离
        distance = track.size['width'] - slider.size['width']

        # 创建ActionChains实例
        actions = ActionChains(driver)
        
        # 按住滑块
        actions.click_and_hold(slider)

        # 模拟非线性拖动
        current_pos = 0
        while current_pos < distance:
            # 随机生成每一步的移动距离
            move = random.randint(20, 40)
            actions.move_by_offset(move, 0)
            current_pos += move
            # 随机停顿
            sleep(random.uniform(0.05, 0.2))
        
        # 释放滑块
        actions.release()
        actions.perform()
        
        print("滑块验证尝试完成。")
        sleep(3) # 等待页面跳转
        return True

    except NoSuchElementException:
        # 没有找到滑块，说明不需要验证
        print("未检测到滑块验证。")
        return False
    except Exception as e:
        print(f"处理滑块验证时出错: {e}")
        return False

def analyze_job_with_gemini(job_information, disciplines):
    """使用Gemini API分析职位信息与学科的相关性"""
    return disciplines[0]
    try:
        print(f'请求googlegoogle')
        prompt = f"""
        请分析以下招聘信息，判断该职位与以下学科中哪个最相关：
        
        学科列表：{', '.join(disciplines)}
        
        招聘信息：
        {job_information}
        
        请只返回最相关的一个学科名称，不要其他解释。
        """
        import os 
        os.environ['https_proxy'] = 'http://127.0.0.1:7890'
        os.environ['http_proxy'] = 'http://127.0.0.1:7890'
        response = model.generate_content(prompt)
        result = response.text.strip()
        os.environ['https_proxy'] = ''
        os.environ['http_proxy'] = ''
        print(result)
        # 确保返回的结果在学科列表中
        for discipline in disciplines:
            if discipline in result:
                return discipline
        
        return "未分类"
    except Exception as e:
        print(f"Gemini API调用失败: {e}")
        return "API错误"

# 程序启动时尝试恢复数据
print("检查是否有未完成的爬取任务...")
load_existing_data()

chrome_driver = './chromedriver.exe'
service = Service(chrome_driver)
web = webdriver.Chrome(service=service, options=opt)

try:
    # 遍历每个产业及其关键词
    for industry, keywords in changye_xueke_dict.items():
        print(f"正在处理产业: {industry}")
        
        for keyword in keywords:
            print(f"正在搜索关键词: {keyword}")
            
            # 构造搜索URL
            web.get(url)
            sleep(10)
            
            c_name = f'_{keyword}_{datetime.now().strftime("%Y_%m_%d")}'
            
            # 输入关键词并搜索
            web.find_element(By.XPATH, '//*[@id="keywordInput"]').clear()
            web.find_element(By.XPATH, '//*[@id="keywordInput"]').send_keys(keyword)
            web.find_element(By.XPATH, '//*[@id="search_btn"]').click()
            sleep(1)
            
            original_window = web.current_window_handle
            total_page = 3  # 每个关键词搜索3页
            valid_jobs = 0
            
            for page in range(total_page):
                if valid_jobs >= 70:
                    break
                try:
                    num_jobs_on_page = len(web.find_elements(By.XPATH, '//div[contains(@class, "joblist")]'))
                    
                    for i in range(num_jobs_on_page):
                        if valid_jobs >= 70:
                            break
                        try:
                            print(f"处理第 {i+1} 个职位")
                            
                            # 重新获取元素避免过期引用
                            item = web.find_elements(By.XPATH, '//div[contains(@class, "joblist")]')[i]
                            one_job = item.find_element(By.XPATH, ".//div[contains(@class, 'joblist-item-job-wrapper')]")
                            data_div = one_job.find_element(By.XPATH, "./div[1]")
                            job_attributes = data_div.get_attribute('sensorsdata')
                            job_attributes = json.loads(job_attributes)
                            
                            search_result = {}
                            search_result['ID'] = job_id
                            search_result['产业'] = industry
                            search_result['jobTitle'] = job_attributes['jobTitle']
                            search_result['搜索关键词'] = keyword
                            
                            try:
                                search_result['company_name'] = one_job.find_element(By.XPATH, './/a[contains(@class, "cname")]').text
                            except Exception:
                                search_result['company_name'] = "null"
                            
                            search_result['jobArea'] = job_attributes['jobArea']
                            search_result['jobDegree'] = job_attributes['jobDegree']
                            
                            try:
                                search_result['company_nature'] = one_job.find_element(By.XPATH, './/span[@class="dc text-cut"]').text
                            except Exception:
                                search_result['company_nature'] = "null"
                            
                            try:
                                search_result['company_scale'] = one_job.find_element(By.XPATH, './/span[@class="dc shrink-0"]').text
                            except Exception:
                                search_result['company_scale'] = "null"
                                
                            search_result['jobTime'] = job_attributes['jobTime']
                    
                            # 点击进入详情页
                            one_job.find_element(By.XPATH, './/span[contains(@class, "jname")]').click()
                            
                            # 切换到新窗口
                            for window_handle in web.window_handles:
                                if window_handle != original_window:
                                    web.switch_to.window(window_handle)
                                    break
                            
                            # 处理滑块验证
                            handle_slider_verification(web)
                            
                            sleep(2)
                            
                            current_url = web.current_url
                            job_information = ktool.xpath.xpath_union(
                                web.page_source, '/html/body/div[2]/div/div[3]/div[1]/div/text()',
                                default=current_url
                            )
                            
                            # 关闭详情页，回到主窗口
                            web.close()
                            web.switch_to.window(original_window)
                            
                            # 使用Gemini API分析职位与学科的相关性
                            related_discipline = analyze_job_with_gemini(job_information, disciplines)
                            
                            # 构造最终结果
                            final_result = {
                                'ID': job_id,
                                '产业': industry,
                                '学科': related_discipline,
                                '招聘详情文本': job_information,
                                '分类结果（不用做）': '',  # 留空
                                '担当者': "刘雨蘅",
                                'URL': current_url
                            }
                            
                            all_results.append(final_result)
                            job_id += 1
                            valid_jobs += 1
                            
                            print(f"已处理职位ID: {job_id-1}, 信息: {final_result}")
                            sleep(4)
                            # 实时保存 - 每处理SAVE_INTERVAL个职位保存一次
                            if len(all_results) % SAVE_INTERVAL == 0:
                                save_data_to_file(all_results, temp_filename, is_temp=True)
                            
                            # 创建备份 - 每处理BACKUP_INTERVAL个职位创建备份
                            if len(all_results) % BACKUP_INTERVAL == 0:
                                create_backup(all_results)
                            
                        except Exception as e:
                            # print(f"处理职位时出错，跳过: {e}")
                            continue
                    
                    # 尝试点击下一页
                    try:
                        next_button = web.find_element(By.XPATH,
                                    '//*[@id="app"]/div/div[2]/div/div/div[2]/div/div[2]/div/div[3]/div/div/div/button[2]')
                        if next_button.get_attribute('disabled') is None:
                            next_button.click()
                            print("*********************点击下一页*********************")
                            sleep(5)
                        else:
                            print("已到达最后一页")
                            break
                    except Exception as e:
                        print(f"无法点击下一页: {e}")
                        break
                        
                except Exception as e:
                    print(f"处理页面时出错: {e}")
                    break
            
            print(f"关键词 '{keyword}' 共处理 {valid_jobs} 个有效职位")
            
            # 每个关键词处理完后保存数据
            if all_results:
                save_data_to_file(all_results, temp_filename, is_temp=True)
            
            # 每个关键词处理完后稍作休息
            sleep(3)

except KeyboardInterrupt:
    print("\n程序被用户中断，正在保存已收集的数据...")
except Exception as e:
    print(f"程序异常: {e}，正在保存已收集的数据...")
finally:
    web.quit()
    
    # 最终保存所有数据
    if all_results:
        # 保存最终结果
        save_data_to_file(all_results, main_filename)
        
        # 创建最终备份
        create_backup(all_results)
        
        # 删除临时文件
        try:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                print("临时文件已清理")
        except:
            pass
        
        print(f"总共处理了 {len(all_results)} 个职位")
        
        # 显示学科分布统计
        df = pd.DataFrame(all_results)
        discipline_counts = df['学科'].value_counts()
        print("\n学科分布统计:")
        print(discipline_counts)
        
        # 显示进度统计
        keyword_counts = df['搜索关键词'].value_counts()
        print("\n关键词处理统计:")
        print(keyword_counts)
    else:
        print("没有获取到任何职位信息")

print("程序执行完成！")
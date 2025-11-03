import aiohttp
import asyncio
import json
import re 
import time 
from tqdm.asyncio import tqdm
import os 
import os 
import pandas  as pd

CHANYE = "新型医疗器械"

def get_keywords(file_path):
    data = pd.read_excel(file_path)
    keywords = data.iloc[:,0].tolist()
    return keywords
# os.environ['https_proxy'] = 'http://192.168.137.215:7890'
# os.environ['http_proxy'] = 'http://192.168.137.215:7890'
current_timestamp = str(int(time.time()))
PX = 349

# 定义代理服务器地址
PROXY_URL = "http://192.168.137.215:7890"

keywords = get_keywords(f'{CHANYE}/urls.xlsx')

def decrypt(a1):
    VP = json.loads("[15, 35, 29, 24, 33, 16, 1, 38, 10, 9, 19, 31, 40, 27, 22, 23, 25, 13, 6, 11,39,18,20,8, 14, 21, 32, 26, 2, 30, 7, 4, 17, 5, 3, 28, 34, 37, 12, 36]")
    Vf = '3000176000856006061501533003690027800375'
    PX = 349
    step = -347 + PX  
    VO = [''] * len(VP)
    Vh = ''
    Vz = ''
    
    for VM, Vq in enumerate(a1):
        target_index = VM + (-348 + PX)  
        for Vn in range(len(VP)):
            if VP[Vn] == target_index: 
                VO[Vn] = Vq
                break
    
    Vh = "".join(VO)
    VM = 0
    while VM < len(Vh) and VM < 40:
        Vh_slice = Vh[VM : VM + step]
        num_Vh = int(Vh_slice, 16)
        Vf_slice = Vf[VM : VM + step]
        num_Vf = int(Vf_slice, 16)
        xor_result = num_Vh ^ num_Vf
        VI = hex(xor_result)[2:].zfill(2)
        Vz += VI
        VM += step
    # print(Vz)
    return Vz

cookies = {
    'guid': '6688c8c6ffe869f1f747796edba5cf9a',
    'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%226688c8c6ffe869f1f747796edba5cf9a%22%2C%22first_id%22%3A%22199e1ac9a2cff5-06697d81b880aac-1f525631-1930176-199e1ac9a2dca0%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk5ZTFhYzlhMmNmZjUtMDY2OTdkODFiODgwYWFjLTFmNTI1NjMxLTE5MzAxNzYtMTk5ZTFhYzlhMmRjYTAiLCIkaWRlbnRpdHlfbG9naW5faWQiOiI2Njg4YzhjNmZmZTg2OWYxZjc0Nzc5NmVkYmE1Y2Y5YSJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%226688c8c6ffe869f1f747796edba5cf9a%22%7D%2C%22%24device_id%22%3A%22199e1ac9a2cff5-06697d81b880aac-1f525631-1930176-199e1ac9a2dca0%22%7D',
    'Hm_lvt_1370a11171bd6f2d9b1fe98951541941': current_timestamp,
    'Hm_lpvt_1370a11171bd6f2d9b1fe98951541941': current_timestamp,
    'HMACCOUNT': '4844DFD44A01DAE8',
    'JSESSIONID': '24455AAA6EA17EE785FC85F2C54F4E3C'
}

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'From-Domain': '51job_web',
    'Referer': 'https://we.51job.com/pc/search?jobArea=020000&keyword=python&searchType=2&keywordType=',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'account-id': '',
    'partner': '',
    'property': '%7B%22partner%22%3A%22%22%2C%22webId%22%3A2%2C%22fromdomain%22%3A%2251job_web%22%2C%22frompageUrl%22%3A%22https%3A%2F%2Fwe.51job.com%2F%22%2C%22pageUrl%22%3A%22https%3A%2F%2Fwe.51job.com%2Fpc%2Fsearch%3FjobArea%3D020000%26keyword%3Dpython%26searchType%3D2%26keywordType%3D%22%2C%22identityType%22%3A%22%22%2C%22userType%22%3A%22%22%2C%22isLogin%22%3A%22%E5%90%A6%22%2C%22accountid%22%3A%22%22%2C%22keywordType%22%3A%22%E5%8E%86%E5%8F%B2%E8%AE%B0%E5%BD%95%22%7D',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sign': '1f0166af5739e583dedebba6b10171a546980c2346ffee3a47e70b5dfabd2932',
    'user-token': '',
    'uuid': '6688c8c6ffe869f1f747796edba5cf9a',
}

params = {
    'api_key': '51job',
    'timestamp': current_timestamp,
    'keyword': 'python',
    'searchType': '2',
    'function': '',
    'industry': '',
    'jobArea': '020000',
    'jobArea2': '',
    'landmark': '',
    'metro': '',
    'salary': '',
    'workYear': '',
    'degree': '',
    'companyType': '',
    'companySize': '',
    'jobType': '',
    'issueDate': '',
    'sortType': '0',
    'pageNum': '1',
    'requestId': '',
    'keywordType': '',
    'pageSize': '20',
    'source': '1',
    'accountId': '',
    'pageCode': 'sou|sou|soulb',
    'scene': '7',
}

async def fetch_page(session, pageNum, keyword, pbar, retries=10, delay=1):
    """异步获取单个页面"""
    for attempt in range(retries):
        try:
            page_params = params.copy()
            page_params['pageNum'] = pageNum
            page_params['keyword'] = keyword
            
            async with session.get('https://we.51job.com/api/job/search-pc', 
                                   params=page_params, 
                                   cookies=cookies, 
                                   headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=30),
                                   proxy=PROXY_URL) as resp:
                resp.raise_for_status()  # This will raise an exception for 4xx/5xx status codes
                data = await resp.json()
                pbar.update(1)
                return data.get("resultbody", {}).get("job", {}).get("items", [])
        except Exception as e:
            if attempt < retries - 1:
                # print(f"第 {pageNum} 页获取失败 (尝试 {attempt + 1}/{retries}): {e}. {delay}秒后重试...")
                await asyncio.sleep(delay)
            else:
                # print(f"第 {pageNum} 页获取失败，已达最大重试次数: {e}")
                pbar.update(1)
                return []

async def scrape_keyword(session, keyword):
    """抓取单个关键词的数据并返回"""
    print(f"开始处理关键词: {keyword}")
    
    # 更新请求参数中的关键词
    local_params = params.copy()
    local_params['keyword'] = keyword
    
    # 获取第一页数据以触发反爬
    async with session.get('https://we.51job.com/api/job/search-pc', 
                          params=local_params, 
                          cookies=cookies, 
                          headers=headers,
                          proxy=PROXY_URL) as resp:
        response_text = await resp.text()
    if cookies.get("acw_sc__v2") is not None:
        del cookies["acw_sc__v2"]
    print(response_text)
    # 提取并更新 acw_sc__v2 cookie
    arg1_match = re.search(r"var\s+arg1\s*=\s*['\"]([^'\"]+)['\"]", response_text)
    if not arg1_match:
        print(f"关键词 '{keyword}' 未能获取到arg1，跳过。响应内容: {response_text[:500]}")
        return None
        
    arg1 = arg1_match.group(1)
    acw_sc__v2 = decrypt(arg1)
    cookies.update({"acw_sc__v2": acw_sc__v2})
    
    # 使用更新后的cookie获取第一页的真实数据
    async with session.get('https://we.51job.com/api/job/search-pc', 
                          params=local_params, 
                          cookies=cookies, 
                          headers=headers,
                          proxy=PROXY_URL) as resp:
        try:
            job_data = (await resp.json())["resultbody"]["job"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"关键词 '{keyword}' 获取第一页数据失败: {e}")
            print(f"响应内容: {await resp.text()}")
            return None

    totalcount = job_data.get("totalcount", 0)
    if totalcount == 0:
        print(f"关键词 '{keyword}' 没有找到相关职位。")
        return job_data
        
    pages = totalcount // 20
    print(f"关键词 '{keyword}' 总共 {totalcount} 条数据，需要爬取 {pages} 页")
    
    # 异步并发获取所有剩余页面
    all_items = job_data.get("items", [])
    
    if pages > 1:
        with tqdm(total=pages - 1, desc=f"下载 '{keyword}'") as pbar:
            tasks = [fetch_page(session, pageNum, keyword, pbar) for pageNum in range(2, pages + 1)]
            results = await asyncio.gather(*tasks)
            
            for items in results:
                all_items.extend(items)
    
    job_data["items"] = all_items
    
    print(f"\n关键词 '{keyword}' 共获取 {len(all_items)} 条职位数据")
    return job_data


async def main():
    all_keywords_data = {}
    total_jobs_count = 0
    async with aiohttp.ClientSession() as session:
        for keyword in keywords:
            result_data = await scrape_keyword(session, keyword)
            if result_data:
                all_keywords_data[keyword] = result_data
                total_jobs_count += len(result_data.get("items", []))
            print("-" * 30)
            await asyncio.sleep(2) # 切换关键词时稍作等待

    # 将所有关键词的数据保存到一个文件中
    output_filename = f'./{CHANYE}/data.json'
    with open(output_filename, mode='w', encoding='utf-8') as f:
        json.dump(all_keywords_data, f, ensure_ascii=False, indent=4)
    
    print(f"\n所有关键词处理完毕。")
    print(f"总共获取 {total_jobs_count} 条职位数据，已全部保存到 {output_filename}")

if __name__ == '__main__':
    asyncio.run(main())
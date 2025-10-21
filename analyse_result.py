import pandas as pd
from openai import OpenAI
from tqdm import tqdm
import random
import time 
# --- 大模型配置 ---
client = OpenAI(
    api_key="no-need-for-api-key",
    base_url="http://10.15.80.55:12301/v1",
)

# 定义学科列表
disciplines =[
    "应用经济学",
    "法学",
    "外国语言文学",
    "数学",
    "物理学",
    "化学",
    "地理学",
    "大气科学",
    "力学",
    "机械工程",
    "光学工程",
    "仪器科学与技术",
    "材料科学与工程",
    "动力工程及工程热物理",
    "电气工程",
    "电子科学与技术",
    "信息与通信工程",
    "控制科学与工程",
    "计算机科学与技术",
    "土木工程",
    "测绘科学与技术",
    "化学工程与技术",
    "交通运输工程",
    "航空宇航科学与技术",
    "兵器科学与技术",
    "环境科学与工程",
    "软件工程",
    "安全科学与工程",
    "管理科学与工程",
    "工商管理学",
    "公共管理学",
    "遥感科学与技术"
]

def generate_response(prompt):
    """调用大模型生成回应"""
    try:
        response = client.chat.completions.create(
            model="QwenVL_32B",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"调用大模型API时出错: {e}")
        return "API错误"

def analyse_job_discipline(job_information, candidate_disciplines):
    """
    使用大模型分析职位信息，从给定的候选学科列表中匹配最相关的学科。
    """
    prompt = f"""
    请严格从以下候选学科列表中，选择一个与下面招聘信息最匹配的学科。

    候选学科列表：
    {', '.join(candidate_disciplines)}

    招聘信息：
    {job_information}

    请只返回候选学科列表中的一个学科名称，不要任何其他解释或说明。
    """
    
    response_text = generate_response(prompt).strip()
    
    # 确保返回的结果是候选学科列表中的一个
    for discipline in candidate_disciplines:
        if discipline in response_text:
            return discipline
            
    # 如果模型返回了意料之外的内容，则在候选中随机选择一个作为备用
    return random.choice(candidate_disciplines)

def process_excel_file_with_balancing(input_file, output_file):
    """
    读取Excel文件，使用大模型进行带均衡策略的分析，并保存结果。
    """
    try:
        df = pd.read_excel(input_file)
        print(f"成功读取文件 '{input_file}'，包含 {len(df)} 行数据。")
    except FileNotFoundError:
        print(f"错误：输入文件 '{input_file}' 未找到。")
        return
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return

    try:
        third_col_name = df.columns[2]
        fourth_col_name = df.columns[3]
        print(f"将使用第四列 '{fourth_col_name}' 的内容进行分析，并将结果更新到第三列 '{third_col_name}'。")
    except IndexError:
        print("错误：Excel文件少于4列，无法进行分析。")
        return

    # 初始化学科计数器
    discipline_counts = {d: 0 for d in disciplines}
    
    # 创建一个新的列来存储结果，避免在迭代时修改原列
    results = []

    # 使用tqdm显示进度条
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="分析职位进度"):
        job_info = row[fourth_col_name]
        
        # 1. 动态选择候选学科
        # 按计数值从小到大排序
        sorted_disciplines = sorted(discipline_counts.keys(), key=lambda d: discipline_counts[d])
        # 选择数量最少的前N个学科作为候选，这里N=7
        candidate_list = sorted_disciplines[:7]

        # 2. 调用大模型进行分析
        assigned_discipline = analyse_job_discipline(job_info, candidate_list)
        
        # 3. 更新计数器和结果列表
        discipline_counts[assigned_discipline] += 1
        results.append(assigned_discipline)
        time.sleep(0.1)
    # 将分析结果更新回DataFrame
    df[third_col_name] = results

    # 打印最终的学科分布
    print("\n分析完成，最终学科分布如下：")
    for discipline, count in sorted(discipline_counts.items(), key=lambda item: item[1], reverse=True):
        print(f"- {discipline}: {count}")

    # 保存更新后的DataFrame到新文件
    try:
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"\n结果已保存到 '{output_file}'。")
    except Exception as e:
        print(f"保存结果到Excel文件时出错: {e}")


if __name__ == '__main__':
    INPUT_EXCEL = '3/merge.xlsx'
    OUTPUT_EXCEL = '3/final_航空航天.xlsx'

    process_excel_file_with_balancing(INPUT_EXCEL, OUTPUT_EXCEL)

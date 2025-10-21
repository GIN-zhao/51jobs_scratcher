import requests
import json
from config import API_KEY, API_BASE_URL_QWEN,API_BASE_URL_GEO
from openai import OpenAI
import json  # 用于完整日志记录
import base64

client = OpenAI(
    api_key="",
    base_url=API_BASE_URL_QWEN,
)

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

def poi_search(keyword,specify= "156310000" ):
    api_url = API_BASE_URL_GEO
    params = {
        "postStr": json.dumps({
            "keyWord": keyword,
            "queryType": 12,
            "start": 0,
            "count": 10,
            "specify": specify  # 上海市行政区划代码（可选）
        }),
        "type": "query",
        "tk": API_KEY 
    }

    try:
        # 发送GET请求
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # 检查HTTP错误

        # 解析JSON响应
        result = response.json()
    except requests.exceptions.RequestException as e:
        raise ValueError(f"请求失败: {e}")
    finally:
        return result
  
def stream_with_full_context(base64_qwen):
    stream = client.chat.completions.create(
        model="Qwen/Qwen2.5-VL-72B-Instruct-AWQ",
        messages=[
            {"role": "system", "content": "你是一个专业的地理定位专家."},
            {
                "role": "user",
                "content": [
                    {
                       "type": "image_url",
                        "image_url": {
                        "url": base64_qwen
                                            },
                    },
                    {"type": "text", "text": """
你是一个专业的地理定位专家。您必须使用以下格式的有效JSON对象进行响应:
{
"解释":"对图像的全面分析，包括:
-建筑风格和时期
-著名地标或特色
-自然环境和气候指标
-文化元素（标志、车辆、服饰等）
-任何可见的文本或语言
-时间段指标（如果有的话）",
"位置":[
{
"国家":“主要国家名称”，
“城市”:“城市名称”，
"地址":"必须提供给出具体的详细地址,,如xx路xx号、xx街道xx号、xx商场,不可以为空",
"街道":"街道名称",
“建筑”:“建筑或者店铺名称，只能为一个”，
“信心”:“高/中/低”，
“坐标”:{
“纬度”:12.3456,
“经度”:78.9012
},
“思考过程”:“此位置识别的详细推理，包括:
-与此位置相匹配的特定建筑特征
-支持这一地点的环境特征
-表明该地区的文化因素
-任何与众不同的地标或特征
- 来自可见文字或标识的佐证\“
 }
 ]
}

重要:
1. 您的响应必须是有效的JSON对象。不要在JSON对象之前或之后包含任何文本。
2. 不要包含任何标记格式或代码块。
3. 响应应该可以被JSON.parse()解析。
4. 如果您对单个地点不完全有信心，您可以提供最多三个可能的地点。
5. 按信任级别（从最高到最低）对位置进行排序。
6. 尽可能包括每个地点的近似坐标（纬度和经度）。

考虑以下关键方面以实现准确的位置识别:
1. 建筑分析:
-建筑风格和材料
-屋顶类型及施工方法
-门窗设计
-装饰元素和装饰

2. 环境指标:
-植被类型和形态
-气候指标（雪、沙漠、热带等）
-地形和地形
- 水袋
                     """},
                ],
            },
        ],
        stream=True,
        max_tokens=1024  # 确保足够长度
    )

    full_response = {
        "content": "",
        "raw_chunks": []
    }

    try:
        for chunk in stream:
            # 记录原始块（调试用）
            full_response["raw_chunks"].append(chunk)
            
            # 处理内容增量
            delta = chunk.choices[0].delta
            if delta and delta.content:
                print(delta.content, end="", flush=True)
                full_response["content"] += delta.content
                
            # 处理可能的元数据（如视觉标记）
            if hasattr(chunk, 'usage'):
                full_response["usage"] = chunk.usage

    except KeyboardInterrupt:
        print("\n[Stream interrupted by user]")
    finally:
        return full_response
   
if __name__ == "__main__":
    
    image_path = r"E:\homework\51job_spiders\other\image\w700d1q75cms.jpg"
    with open(image_path, "rb") as f:
        encoded_image = base64.b64encode(f.read())
    encoded_image_text = encoded_image.decode("utf-8")
    base64_qwen = f"data:image;base64,{encoded_image_text}"
    response = stream_with_full_context(base64_qwen)
    
    location = None
    # 尝试解析模型返回的JSON内容
    if response and response.get('content'):
        try:
            # 移除可能的代码块标记
            clean_content = response['content'].strip().replace('```json', '').replace('```', '').strip()
            data = json.loads(clean_content)
            
            # 提取第一个位置的“区域”字段
            if '位置' in data and isinstance(data['位置'], list) and len(data['位置']) > 0:
                location = data['位置'][0].get('建筑')
                print(f"\n成功从模型响应中解析出区域: {location}")
            else:
                print("\n未能从JSON中找到有效的'位置'信息。")

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"\n解析JSON或提取区域时出错: {e}")
            print("将使用默认地点进行搜索。")
    else:
        print("\n模型未能返回有效内容。")

    print(f"\n最终用于POI搜索的地点名称: {location}")
    search_result = poi_search(location, 156710009)
    print("\nPOI搜索结果:")
    print(json.dumps(search_result, indent=2, ensure_ascii=False))

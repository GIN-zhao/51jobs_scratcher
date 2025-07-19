from openai import OpenAI
import json  # 用于完整日志记录

client = OpenAI(
    api_key="",
    base_url="http://10.15.80.55:12301/v1",
)

def stream_with_full_context():
    stream = client.chat.completions.create(
        model="QwenVL_32B",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://modelscope.oss-cn-beijing.aliyuncs.com/resource/qwen.png"
                        },
                    },
                    {"type": "text", "text": "Describe the image in detail"},
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

    print("Streaming... (Ctrl+C to stop early)")
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
   

stream_with_full_context()
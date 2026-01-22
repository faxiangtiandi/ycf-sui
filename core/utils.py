import base64
import streamlit as st

# API预设配置（各服务商默认参数）
API_PRESETS = {
    "DeepSeek": {
        "base_url": "https://api.deepseek.com/v1/chat/completions",
        "default_model": "deepseek-chat"
    },
    "火山方舟（豆包）": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "default_model": "doubao-seed-1-8-251228"
    },
    "OpenAI": {
        "base_url": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-3.5-turbo"
    },
    "通义千问": {
        "base_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        "default_model": "qwen-turbo"
    },
    "智谱AI（GLM）": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "default_model": "glm-3-turbo"
    },
    "百度文心一言": {
        "base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro",
        "default_model": "ernie-3.5-8k"
    },
    "阿里云通义千问": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "default_model": "qwen-turbo"
    },
    "自定义API": {
        "base_url": "",
        "default_model": ""
    }
}

def image_to_base64(uploaded_file):
    """
    上传图片转Base64编码（复用coreutils的工具函数）
    :param uploaded_file: Streamlit上传的文件对象
    :return: Base64编码字符串
    """
    if not uploaded_file:
        return ""
    try:
        from core.coreutils import image_to_base64_bytesio
        bytes_data = image_to_base64_bytesio(uploaded_file)
        if not bytes_data:
            return ""
        mime_type = uploaded_file.type if uploaded_file.type else "image/jpeg"
        return f"data:{mime_type};base64,{bytes_data}"
    except Exception as e:
        st.error(f"❌ 图片编码失败：{str(e)}")
        return ""
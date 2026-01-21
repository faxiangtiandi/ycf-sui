import requests
import ssl
import json
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm(prompt, temperature=0.6, uploaded_image=None):
    """
    通用大模型API调用函数
    :param prompt: 提示词
    :param temperature: 随机性
    :param uploaded_image: 上传的图片文件（图文模式用）
    :return: API返回的文本结果
    """
    if st.session_state.stop_flag:
        return None

    # 获取有效配置
    cfg = get_valid_config()
    if not cfg:
        st.error("❌ 无有效API配置！请至少填写一个有效的API Key、接口地址和模型名")
        return None

    # 读取配置
    if cfg == "text_mode":
        api_key = st.session_state.text_mode_api_key.strip()
        base_url = st.session_state.text_mode_base_url.strip()
        model = st.session_state.text_mode_model.strip()
    else:
        api_key = st.session_state.multimodal_mode_api_key.strip()
        base_url = st.session_state.multimodal_mode_base_url.strip()
        model = st.session_state.multimodal_mode_model.strip()

    # 构建请求头
    headers = {"Content-Type": "application/json"}
    if "volces.com" in base_url and ":" in api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    else:
        headers["Authorization"] = f"Bearer {api_key}"

    # 构建请求内容
    content = [{"type": "text", "text": prompt}]
    
    # 图文模式处理图片
    if cfg == "multimodal_mode":
        from .utils import image_to_base64
        image_url = ""
        if uploaded_image:
            image_url = image_to_base64(uploaded_image)
        elif st.session_state.multimodal_mode_image_url.strip():
            image_url = st.session_state.multimodal_mode_image_url.strip()
        
        if image_url:
            content.insert(0, {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}})

    # 构建请求体
    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": 8000,
        "messages": [{"role": "user", "content": content}],
        "stream": False
    }

    try:
        if st.session_state.stop_flag:
            return None

        # 忽略SSL验证（适配内网/自定义API）
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        response = requests.post(
            base_url,
            headers=headers,
            json=payload,
            timeout=180,
            verify=False,
            allow_redirects=True
        )
        response.raise_for_status()
        response_json = response.json()

        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"].strip()
        else:
            st.error(f"❌ API返回格式异常：{json.dumps(response_json, ensure_ascii=False)[:200]}")
            return None

    except requests.exceptions.HTTPError as e:
        error_detail = f"HTTP {response.status_code}: {response.text[:500]}" if 'response' in locals() else str(e)
        st.error(f"❌ API调用失败：{error_detail}")
        return None
    except requests.exceptions.Timeout:
        st.error("❌ API调用超时（超过180秒）")
        return None
    except Exception as e:
        st.error(f"❌ API调用异常：{str(e)}")
        return None

def check_config_valid(mode):
    """校验指定模式的API配置是否完整"""
    if mode == "text_mode":
        return all([
            st.session_state.text_mode_api_key.strip(),
            st.session_state.text_mode_base_url.strip(),
            st.session_state.text_mode_model.strip()
        ])
    elif mode == "multimodal_mode":
        return all([
            st.session_state.multimodal_mode_api_key.strip(),
            st.session_state.multimodal_mode_base_url.strip(),
            st.session_state.multimodal_mode_model.strip()
        ])
    return False

def get_valid_config():
    """自动检测并返回可用的API模式（text_mode/multimodal_mode/None）"""
    selected = st.session_state.selected_mode
    text_valid = check_config_valid("text_mode")
    multimodal_valid = check_config_valid("multimodal_mode")

    if selected == "text_mode" and text_valid:
        return "text_mode"
    elif selected == "multimodal_mode" and multimodal_valid:
        return "multimodal_mode"
    elif text_valid:
        return "text_mode"
    elif multimodal_valid:
        return "multimodal_mode"
    else:
        return None
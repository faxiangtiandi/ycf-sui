import requests
import ssl
import json
import streamlit as st
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# 设置日志级别
logging.basicConfig(level=logging.INFO)

def get_valid_config():
    """
    获取有效的LLM配置（文本模式/多模态模式）
    :return: "text_mode" / "multimodal_mode" / None
    """
    # 检查文本模式配置
    text_mode_valid = (
        st.session_state.get("text_mode_api_key", "").strip() and
        st.session_state.get("text_mode_base_url", "").strip() and
        st.session_state.get("text_mode_model", "").strip()
    )
    
    # 检查多模态模式配置
    multimodal_mode_valid = (
        st.session_state.get("multimodal_mode_api_key", "").strip() and
        st.session_state.get("multimodal_mode_base_url", "").strip() and
        st.session_state.get("multimodal_mode_model", "").strip()
    )
    
    if st.session_state.get("selected_mode") == "text_mode" and text_mode_valid:
        return "text_mode"
    elif st.session_state.get("selected_mode") == "multimodal_mode" and multimodal_mode_valid:
        return "multimodal_mode"
    elif text_mode_valid:
        return "text_mode"
    elif multimodal_mode_valid:
        return "multimodal_mode"
    else:
        return None

def call_llm(prompt, temperature=0.6, uploaded_image=None, is_comic_creation=False):
    """
    通用大模型API调用函数
    :param prompt: 提示词
    :param temperature: 随机性
    :param uploaded_image: 上传的图片文件（图文模式用）
    :param is_comic_creation: 是否为漫画创作场景
    :return: API返回的文本结果
    """
    # 漫画创作专业提示词增强
    if is_comic_creation:
        comic_prompt_enhancement = """请以专业漫画创作专家的身份进行回答。需要考虑以下专业要素：
        1. 分镜设计：合理规划画面布局和镜头角度
        2. 角色表现：注重角色表情、动作和性格刻画
        3. 台词设计：对白要符合角色特征且简洁有力
        4. 画面构图：注意视觉引导线和画面平衡
        5. 色彩搭配：考虑色彩情感和氛围营造
        6. 特效文字：适当使用拟声词和特效字增强表现力
        7. 故事节奏：把握叙事节奏和悬念设置
        
        请按照专业漫画制作流程提供创意和建议。"""
        prompt = f"{comic_prompt_enhancement}\n\n原始请求：{prompt}"
    
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

    # 特殊处理豆包（火山方舟）API
    if "volces.com" in base_url:
        return _call_volcengine_api(base_url, api_key, model, prompt, temperature, uploaded_image, cfg, is_comic_creation=is_comic_creation)
    else:
        # 使用通用OpenAI兼容API调用
        return _call_openai_compatible_api(base_url, api_key, model, prompt, temperature, uploaded_image, cfg, is_comic_creation=is_comic_creation)

def _call_volcengine_api(base_url, api_key, model, prompt, temperature, uploaded_image, mode, is_comic_creation=False):
    """调用火山方舟（豆包）API"""
    # 构建请求头
    headers = {"Content-Type": "application/json"}
    if ":" in api_key:
        # AK:SK格式的认证
        headers["Authorization"] = f"Bearer {api_key}"
    else:
        headers["Authorization"] = f"Bearer {api_key}"

    # 构建请求内容
    content = [{"type": "text", "text": prompt}]
    
    # 图文模式处理图片
    if mode == "multimodal_mode":
        from .utils import image_to_base64
        image_url = ""
        if uploaded_image:
            image_url = image_to_base64(uploaded_image)
        elif st.session_state.multimodal_mode_image_url.strip():
            image_url = st.session_state.multimodal_mode_image_url.strip()
        
        if image_url:
            content.insert(0, {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}})

    # 构建请求体 - 火山方舟格式
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

        # 记录请求信息用于调试（但不记录敏感的API Key）
        logging.info(f"调用LLM API: {base_url}, model: {model}, prompt length: {len(prompt)}")
        response = requests.post(
            base_url,
            headers=headers,
            json=payload,
            timeout=180,
            verify=False,
            allow_redirects=True
        )
        logging.info(f"API响应状态: {response.status_code}, 长度: {len(response.content)}")
        response.raise_for_status()
        response_json = response.json()

        if "choices" in response_json and len(response_json["choices"]) > 0:
            result = response_json["choices"][0]["message"]["content"].strip()
            logging.info(f"成功获取LLM响应，长度: {len(result)}")
            return result
        else:
            error_msg = f"❌ API返回格式异常：{json.dumps(response_json, ensure_ascii=False)[:200]}"
            logging.error(error_msg)
            st.error(error_msg)
            return None

    except Exception as e:
        general_error = f"LLM调用异常：{str(e)}，请求URL: {base_url}，模型: {model}，错误类型: {type(e).__name__}"
        logging.error(general_error)
        st.error(f"❌ API调用异常：{str(e)}")
        return None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _call_openai_compatible_api(base_url, api_key, model, prompt, temperature, uploaded_image, mode, is_comic_creation=False):
    """调用兼容OpenAI格式的API（添加重试装饰器）"""
    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 构建消息内容
    content = [{"type": "text", "text": prompt}]
    
    # 图文模式处理图片
    if mode == "multimodal_mode":
        from .utils import image_to_base64
        image_url = ""
        if uploaded_image:
            image_url = image_to_base64(uploaded_image)
        elif st.session_state.multimodal_mode_image_url.strip():
            image_url = st.session_state.multimodal_mode_image_url.strip()
        
        if image_url:
            content.insert(0, {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}})

    # 构建请求体 - OpenAI兼容格式
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

        # 记录请求信息用于调试（但不记录敏感的API Key）
        logging.info(f"调用OpenAI兼容API: {base_url}, model: {model}, prompt length: {len(prompt)}")
        response = requests.post(
            base_url,
            headers=headers,
            json=payload,
            timeout=180,
            verify=False,
            allow_redirects=True
        )
        logging.info(f"API响应状态: {response.status_code}, 长度: {len(response.content)}")
        response.raise_for_status()
        response_json = response.json()

        if "choices" in response_json and len(response_json["choices"]) > 0:
            result = response_json["choices"][0]["message"]["content"].strip()
            logging.info(f"成功获取LLM响应，长度: {len(result)}")
            return result
        else:
            error_msg = f"❌ API返回格式异常：{json.dumps(response_json, ensure_ascii=False)[:200]}"
            logging.error(error_msg)
            st.error(error_msg)
            return None

    except requests.exceptions.HTTPError as e:
        error_detail = f"HTTP {response.status_code}: {response.text[:500]}" if 'response' in locals() else str(e)
        full_error = f"LLM调用HTTP错误：{error_detail}，请求URL: {base_url}，模型: {model}"
        logging.error(full_error)
        st.error(f"❌ API调用失败：{error_detail}")
        raise  # 抛出异常触发重试
    except requests.exceptions.Timeout:
        timeout_error = f"LLM调用超时（超过180秒）：请求URL: {base_url}，模型: {model}"
        logging.error(timeout_error)
        st.error("❌ API调用超时（超过180秒）")
        raise
    except requests.exceptions.ConnectionError as e:
        conn_error = f"LLM连接错误：{str(e)}，请求URL: {base_url}，模型: {model}"
        logging.error(conn_error)
        st.error(f"❌ API连接错误：{str(e)}")
        raise
    except ValueError as e:  # JSON解析错误
        json_error = f"LLM响应JSON解析错误：{str(e)}，响应内容: {response.text[:500] if 'response' in locals() else 'N/A'}，请求URL: {base_url}，模型: {model}"
        logging.error(json_error)
        st.error(f"❌ API响应解析错误：{str(e)}")
        raise
    except Exception as e:
        general_error = f"LLM调用异常：{str(e)}，请求URL: {base_url}，模型: {model}，错误类型: {type(e).__name__}"
        logging.error(general_error)
        st.error(f"❌ API调用异常：{str(e)}")
        raise

def call_llm_with_retry(prompt, temperature=0.6, uploaded_image=None, is_comic_creation=False):
    """带重试机制的API调用函数"""
    return call_llm(prompt, temperature, uploaded_image, is_comic_creation)
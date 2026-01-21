import uuid
import streamlit as st

def copy_to_clipboard_button(text, button_label="📋 复制", key_suffix=""):
    """
    生成带状态提示的复制按钮
    :param text: 要复制的文本
    :param button_label: 按钮文字
    :param key_suffix: 唯一标识后缀
    """
    unique_key = f"copy_btn_{uuid.uuid4().hex[:8]}_{key_suffix}"
    st.button(
        button_label,
        key=unique_key,
        on_click=lambda t=text: st.session_state.update({
            f"copied_text_{unique_key}": t, 
            f"copy_status_{unique_key}": True
        }),
        help="点击复制到剪贴板"
    )
    # 显示复制成功状态
    if st.session_state.get(f"copy_status_{unique_key}", False):
        st.success("✅ 复制成功！")
        st.session_state[f"copy_status_{unique_key}"] = False

def init_basic_config():
    """初始化页面基础配置（CSS/日志/页面设置）"""
    # 日志配置
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    st.session_state.logger = logging.getLogger(__name__)
    
    # 自定义CSS（优化UI/UX）
    st.markdown("""
    <style>
    /* 基础样式优化 */
    .stApp {max-width: 1600px; margin: 0 auto;}
    .stAlert {border-radius: 8px; padding: 1rem; margin-bottom: 1rem;}
    .stButton>button {border-radius: 6px; height: 38px; font-weight: 500;}
    .stTextArea, .stTextInput, .stSelectbox {border-radius: 6px; border: 1px solid #e2e8f0;}
    .stContainer {border-radius: 8px; padding: 1rem; margin-bottom: 1rem; border: 1px solid #e2e8f0;}
    /* 卡片样式 */
    .card {border-radius: 8px; padding: 1rem; margin-bottom: 1rem; border: 1px solid #e2e8f0; background-color: white;}
    /* 标签样式 */
    .tag {display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.875rem; margin-right: 0.5rem; margin-bottom: 0.5rem;}
    .tag-primary {background-color: #e0f2fe; color: #0369a1;}
    .tag-success {background-color: #dcfce7; color: #166534;}
    .tag-warning {background-color: #fffbeb; color: #92400e;}
    </style>
    """, unsafe_allow_html=True)

    # 页面基础配置
    st.set_page_config(
        page_title="🎬 导演级分镜生成器（小说漫改专属）",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

def init_session_state():
    """初始化会话状态（默认值）"""
    default_states = {
        # API配置相关
        "text_mode_api_provider": "DeepSeek",
        "text_mode_api_key": "",
        "text_mode_base_url": "https://api.deepseek.com/v1/chat/completions",
        "text_mode_model": "deepseek-chat",
        "multimodal_mode_api_provider": "火山方舟（豆包）",
        "multimodal_mode_api_key": "",
        "multimodal_mode_base_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "multimodal_mode_model": "doubao-seed-1-8-251228",
        "multimodal_mode_image_url": "",
        # 业务核心状态
        "novel_type": "",
        "novel_trait": "",
        "adapt_demand": "",
        "complexity": "",
        "storyboards": [],
        "comfyui_prompts": [],
        "optimized_prompts": [],
        "negative_prompt": "",
        "video_prompts": [],
        "selected_mode": "text_mode",
        "is_running": False,
        "stop_flag": False,
        "expanded_prompt_idx": -1,
        "generate_mode": "手动模式",
        # 小说基础信息
        "novel_title": "",
        "novel_author": "",
        "novel_background": "",    
        "novel_target_chapter": "",
        "director_persona": "",        
        "custom_director_name": "",    
        "director_recommend_list": [], 
        "selected_director": "",
        "director_style_tags": [],
        "director_radio": "",
        # 小说核心元素缓存
        "novel_core_characters": [],
        "novel_core_scenes": [],
        # 校验结果和应用状态
        "validation_result": "",
        "validation_suggestions": [],
        "applied_validation": False
    }
    
    # 初始化未定义的会话变量
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value
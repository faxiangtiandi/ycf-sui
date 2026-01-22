import uuid
import streamlit as st
import logging
from .utils import API_PRESETS  # 从 utils.py 导入 API_PRESETS，避免重复定义

def copy_to_clipboard_button(text, button_label="📋 复制", key_suffix=""):
    """
    生成带状态提示的复制按钮（优化交互反馈）
    :param text: 要复制的文本
    :param button_label: 按钮文字
    :param key_suffix: 唯一标识后缀
    """
    unique_key = f"copy_btn_{uuid.uuid4().hex[:8]}_{key_suffix}"
    # 美化按钮样式
    st.markdown(f"""
    <style>
    #{unique_key} {{
        background-color: #4f46e5 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.4rem 1rem !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}
    #{unique_key}:hover {{
        background-color: #4338ca !important;
        transform: translateY(-1px) !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    st.button(
        button_label,
        key=unique_key,
        on_click=lambda t=text: st.session_state.update({
            f"copied_text_{unique_key}": t, 
            f"copy_status_{unique_key}": True
        }),
        help="点击复制到剪贴板"
    )
    # 优化复制成功提示（更醒目）
    if st.session_state.get(f"copy_status_{unique_key}", False):
        st.success("✅ 复制成功！", icon="📋")
        # 3秒后自动清除提示（用streamlit的empty+延时）
        import time
        time.sleep(3)
        st.session_state[f"copy_status_{unique_key}"] = False
        st.rerun()

def init_basic_config():
    """初始化页面基础配置（VS深色主题）"""
    # 日志配置
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    st.session_state.logger = logging.getLogger(__name__)
    
    # VS深色主题CSS
    st.markdown("""
    <style>
    /* 全局重置（VS深色基础） */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    /* 页面主体（VS深色背景） */
    .stApp {
        max-width: 1800px !important;
        margin: 0 auto !important;
        padding: 1rem 2rem !important;
        background-color: #1e1e1e !important;
    }
    /* 标题样式（VS蓝强调） */
    h1, h2, h3, h4 {
        color: #d4d4d4 !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
    h1 {
        background: linear-gradient(90deg, #007acc, #4ec9b0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem !important;
        margin-bottom: 2rem !important;
        text-align: center;
    }
    h2 {
        font-size: 1.5rem !important;
        border-left: 4px solid #007acc;
        padding-left: 0.8rem !important;
        margin-top: 1.5rem !important;
    }
    h3 {
        font-size: 1.2rem !important;
        color: #c8c8c8 !important;
    }
    /* 卡片容器（深色卡片） */
    .stContainer [data-testid="stVerticalBlock"] {
        background-color: #2d2d2d !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
        border: 1px solid #3d3d3d !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    .stContainer [data-testid="stVerticalBlock"]:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3) !important;
    }
    /* 按钮样式（深色适配） */
    .stButton>button {
        border-radius: 8px !important;
        height: 42px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        padding: 0 1.2rem !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:not([disabled]):hover {
        transform: translateY(-1px) !important;
    }
    .stButton>button[data-testid="baseButton-primary"] {
        background-color: #007acc !important;
        color: white !important;
    }
    .stButton>button[data-testid="baseButton-primary"]:hover {
        background-color: #006bb3 !important;
    }
    .stButton>button[data-testid="baseButton-secondary"] {
        background-color: #3d3d3d !important;
        color: #d4d4d4 !important;
        border: 1px solid #4d4d4d !important;
    }
    .stButton>button[data-testid="baseButton-secondary"]:hover {
        background-color: #4d4d4d !important;
    }
    /* 输入框/文本域样式（深色输入框） */
    .stTextArea, .stTextInput, .stSelectbox, .stRadio [data-testid="stMarkdownContainer"] {
        border-radius: 8px !important;
        border: 1px solid #4d4d4d !important;
        padding: 0.75rem !important;
        font-size: 0.9rem !important;
        background-color: #2d2d2d !important;
        color: #d4d4d4 !important;
    }
    .stTextArea:focus, .stTextInput:focus {
        border-color: #007acc !important;
        box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.2) !important;
        outline: none !important;
    }
    /* 提示框样式（深色提示） */
    .stAlert {
        border-radius: 10px !important;
        padding: 1rem 1.2rem !important;
        margin-bottom: 1.2rem !important;
        border: none !important;
    }
    .stAlert-success {
        background-color: #1e3a29 !important;
        color: #4ec9b0 !important;
        border-left: 4px solid #4ec9b0 !important;
    }
    .stAlert-error {
        background-color: #3a1e1e !important;
        color: #f44747 !important;
        border-left: 4px solid #f44747 !important;
    }
    .stAlert-warning {
        background-color: #3a301e !important;
        color: #dcdcaa !important;
        border-left: 4px solid #dcdcaa !important;
    }
    /* 标签样式（深色标签） */
    .tag {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 999px;
        font-size: 0.8rem;
        margin-right: 0.6rem;
        margin-bottom: 0.6rem;
        font-weight: 500;
    }
    .tag-primary {
        background-color: #1e2a38 !important;
        color: #007acc !important;
    }
    .tag-success {
        background-color: #1e3a29 !important;
        color: #4ec9b0 !important;
    }
    .tag-warning {
        background-color: #3a301e !important;
        color: #dcdcaa !important;
    }
    /* 展开面板样式（深色面板） */
    [data-testid="stExpander"] {
        border-radius: 10px !important;
        border: 1px solid #3d3d3d !important;
        margin-bottom: 1rem !important;
        background-color: #2d2d2d !important;
    }
    [data-testid="stExpanderHeader"] {
        background-color: #252525 !important;
        border-bottom: 1px solid #3d3d3d !important;
        padding: 0.8rem 1rem !important;
        color: #d4d4d4 !important;
    }
    /* 下载按钮样式（深色下载） */
    [data-testid="stDownloadButton"] button {
        background-color: #4ec9b0 !important;
        color: #1e1e1e !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stDownloadButton"] button:hover {
        background-color: #3da68b !important;
    }
    /* 禁用状态优化 */
    button:disabled {
        opacity: 0.6 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }
    /* 下拉框/单选框文字颜色 */
    .stSelectbox [data-testid="stMarkdownContainer"], .stRadio label {
        color: #d4d4d4 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 页面基础配置
    st.set_page_config(
        page_title="🎬 导演级分镜生成器（小说漫改专属）",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

def init_session_state():
    """初始化会话状态（文本/图文模式配置完全独立）"""
    # 定义默认状态（文本/图文模式配置分开）
    default_states = {
        # ========== 文本模式独立配置 ==========
        "text_mode_api_provider": "DeepSeek",
        "text_mode_api_key": "",
        "text_mode_base_url": API_PRESETS["DeepSeek"]["base_url"],
        "text_mode_model": API_PRESETS["DeepSeek"]["default_model"],
        # ========== 图文模式独立配置 ==========
        "multimodal_mode_api_provider": "火山方舟（豆包）",
        "multimodal_mode_api_key": "",
        "multimodal_mode_base_url": API_PRESETS["火山方舟（豆包）"]["base_url"],
        "multimodal_mode_model": API_PRESETS["火山方舟（豆包）"]["default_model"],
        "multimodal_mode_image_url": "",
        # ========== 其他业务状态 ==========
        "selected_mode": "text_mode",
        "is_running": False,
        "stop_flag": False,
        "expanded_prompt_idx": -1,
        "generate_mode": "手动模式",
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
        "novel_core_characters": [],
        "novel_core_scenes": [],
        "validation_result": "",
        "validation_suggestions": [],
        "applied_validation": False,
        "storyboards": [],
        "comfyui_prompts": [],
        "optimized_prompts": [],
        "negative_prompt": "",
        "video_prompts": []
    }
    
    # 核心逻辑：只初始化不存在的变量，绝不覆盖已有值
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # ========== 兜底逻辑：防止默认值丢失 ==========
    # 文本模式兜底
    if not st.session_state.text_mode_base_url.strip():
        st.session_state.text_mode_base_url = API_PRESETS[st.session_state.text_mode_api_provider]["base_url"]
    if not st.session_state.text_mode_model.strip():
        st.session_state.text_mode_model = API_PRESETS[st.session_state.text_mode_api_provider]["default_model"]
    
    # 图文模式兜底
    if not st.session_state.multimodal_mode_base_url.strip():
        st.session_state.multimodal_mode_base_url = API_PRESETS[st.session_state.multimodal_mode_api_provider]["base_url"]
    if not st.session_state.multimodal_mode_model.strip():
        st.session_state.multimodal_mode_model = API_PRESETS[st.session_state.multimodal_mode_api_provider]["default_model"]

def check_config_valid(mode: str) -> bool:
    """校验指定模式的API配置是否有效"""
    if mode == "text_mode":
        return (
            bool(st.session_state.text_mode_api_key.strip()) and
            bool(st.session_state.text_mode_base_url.strip()) and
            bool(st.session_state.text_mode_model.strip())
        )
    elif mode == "multimodal_mode":
        return (
            bool(st.session_state.multimodal_mode_api_key.strip()) and
            bool(st.session_state.multimodal_mode_base_url.strip()) and
            bool(st.session_state.multimodal_mode_model.strip())
        )
    return False

def get_valid_config() -> dict:
    """获取当前选中模式的有效配置"""
    if st.session_state.selected_mode == "text_mode" and check_config_valid("text_mode"):
        return {
            "provider": st.session_state.text_mode_api_provider,
            "api_key": st.session_state.text_mode_api_key,
            "base_url": st.session_state.text_mode_base_url,
            "model": st.session_state.text_mode_model
        }
    elif st.session_state.selected_mode == "multimodal_mode" and check_config_valid("multimodal_mode"):
        return {
            "provider": st.session_state.multimodal_mode_api_provider,
            "api_key": st.session_state.multimodal_mode_api_key,
            "base_url": st.session_state.multimodal_mode_base_url,
            "model": st.session_state.multimodal_mode_model,
            "image_url": st.session_state.multimodal_mode_image_url
        }
    return {}
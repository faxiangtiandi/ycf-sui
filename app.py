# app.py — Streamlit UI（refactor 版本，调用 core 中的函数）
# 这是一个相对精简且可运行的 UI 入口，完整逻辑已拆分到 core/，便于你或豆包逐文件修改。
import streamlit as st
from core.generator import generate_universal_image_prompt, optimize_prompt_for_ai, parse_storyboards_from_raw
from core.utils import image_to_base64_bytesio

def init_basic_config():
    st.set_page_config(page_title="🎬 言出法随：导演级分镜生成器", layout="wide")
    st.markdown("""
    <style>
    .stApp { max-width: 1400px; margin: 0 auto; }
    </style>
    """, unsafe_allow_html=True)

def main():
    init_basic_config()

    st.title("🎬 言出法随（导演级分镜生成器）")
    st.sidebar.header("说明")
    st.sidebar.info("把小说章节粘到主区域，然后点击“生成示例提示词”。完整功能可由 core/ 模块扩展。")

    novel_text = st.text_area("目标章节内容（必填）", height=300)
    uploaded_image = st.file_uploader("参考图片（可选）", type=["png", "jpg", "jpeg"])

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("生成示例提示词（本地示例，不调用外部API）"):
            if not novel_text.strip():
                st.warning("请先输入目标章节内容。")
            else:
                # 示例：用核心函数生成一个图像提示词（不调用 LLM）
                core_elements = {
                    "main_characters": [{"name": "主角", "gender": "女", "age": "20岁", "appearance": "黑长发"}],
                    "key_scenes": [{"location": "客厅", "spatial_relations": "人物在窗前"}]
                }
                scene_info = {
                    "scene_core": "主角站在窗前",
                    "emotion": "紧张",
                    "camera": "中景，平视角度",
                    "atmosphere": "冷色调，阴影重",
                    "character_feature": "20岁女性主角，黑长发，惊讶表情",
                    "environment": "客厅窗边，室内昏暗",
                    "visual_style": "悬疑风"
                }
                prompts = generate_universal_image_prompt(scene_info, core_elements, novel_type="悬疑", director_style="冷青灰高对比色调")
                st.subheader("正向提示词（示例）")
                st.code(prompts["positive"])
                st.subheader("负向提示词（示例）")
                st.code(prompts["negative"])

    with col2:
        st.write("调试/说明")
        st.write("- core/generator.py: 生成 prompt 与解析分镜（你或豆包可直接修改）")
        st.write("- 若希望连接 LLM（豆包的豆包 AI），请在 core 中实现 call_llm 并在 .streamlit/secrets.toml 填入 Key")

    st.markdown("---")
    st.info("注意：这是可运行的分离版本。若你需要我把你原来的完整 Streamlit 代码逐行拆分并替换为对 core 的调用（保留 UI 所有控件与交互），回复“开始完整重构”，我会输出重构后的完整 app.py（包含原功能且与 core 解耦）。")

if __name__ == "__main__":
    main()
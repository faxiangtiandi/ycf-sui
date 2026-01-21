import streamlit as st

# 一键导入所有核心模块函数
from core import (
    call_llm, check_config_valid, get_valid_config,
    ai_recommend_director, generate_director_persona,
    generate_storyboards, extract_novel_core_elements, validate_storyboard_consistency, apply_validation_suggestions,
    image_to_base64, API_PRESETS,
    copy_to_clipboard_button, init_basic_config, init_session_state
)

def one_click_generate(uploaded_image=None):
    """一键全自动生成（UI层封装）"""
    st.session_state.is_running = True
    
    if not st.session_state.novel_target_chapter.strip():
        st.warning("⚠️ 请先填写目标章节内容！")
        st.session_state.is_running = False
        return
    
    if not get_valid_config():
        st.error("❌ 无有效API配置！请填写至少一个模式的API信息")
        st.session_state.is_running = False
        return
    
    # 自动推荐导演→生成风格→生成分镜
    recommend_ok = ai_recommend_director(auto=True, uploaded_image=uploaded_image)
    if not recommend_ok or st.session_state.stop_flag:
        st.error("❌ 自动推荐导演失败！")
        st.session_state.is_running = False
        return
    
    persona_ok = generate_director_persona(auto=True, uploaded_image=uploaded_image)
    if not persona_ok or st.session_state.stop_flag:
        st.error("❌ 自动生成导演风格失败！")
        st.session_state.is_running = False
        return
    
    storyboard_ok = generate_storyboards(auto=True, uploaded_image=uploaded_image)
    if storyboard_ok:
        st.success("🎉 全自动生成完成！")
    else:
        st.error("❌ 全自动生成失败！")
    
    st.session_state.is_running = False

def render_page_layout():
    """渲染页面UI（核心UI逻辑）"""
    st.title("🎬 导演级分镜生成器（小说漫改专属·通用优化版）")
    
    # 顶部导航栏
    tab1, tab2 = st.tabs(["📝 分镜生成", "ℹ️ 使用指南"])
    
    with tab1:
        # 主布局：左侧配置区，右侧操作和结果区
        main_left, main_right = st.columns([1, 2.5], gap="large")
        
        with main_left:
            # 第一部分：API配置（卡片式布局）
            with st.container(border=True):
                st.subheader("🔧 API 配置")
                st.write('<div class="tag tag-primary">基础配置</div>', unsafe_allow_html=True)
                
                # API模式选择
                api_mode = st.radio(
                    "API调用模式",
                    options=["文本模式", "图文模式"],
                    horizontal=True,
                    key="api_mode_selector"
                )
                
                if api_mode == "文本模式":
                    st.session_state.selected_mode = "text_mode"
                    provider1 = st.selectbox(
                        "API服务商",
                        options=list(API_PRESETS.keys()),
                        key="text_mode_api_provider",
                        on_change=lambda: [
                            setattr(st.session_state, "text_mode_base_url", API_PRESETS[st.session_state.text_mode_api_provider]["base_url"]),
                            setattr(st.session_state, "text_mode_model", API_PRESETS[st.session_state.text_mode_api_provider]["default_model"])
                        ]
                    )
                    st.text_input("API Key", key="text_mode_api_key", type="password", help="DeepSeek/OpenAI填密钥，火山方舟填AK:SK")
                    st.text_input("接口地址", key="text_mode_base_url", value=st.session_state.text_mode_base_url)
                    st.text_input("模型名", key="text_mode_model", value=st.session_state.text_mode_model)
                    
                    # 配置状态提示
                    if check_config_valid("text_mode"):
                        st.success("✅ 配置有效")
                    else:
                        if st.session_state.text_mode_api_key.strip() or st.session_state.text_mode_base_url.strip() or st.session_state.text_mode_model.strip():
                            st.error("❌ 请填写完整API信息")
                else:
                    st.session_state.selected_mode = "multimodal_mode"
                    provider2 = st.selectbox(
                        "API服务商",
                        options=list(API_PRESETS.keys()),
                        key="multimodal_mode_api_provider",
                        on_change=lambda: [
                            setattr(st.session_state, "multimodal_mode_base_url", API_PRESETS[st.session_state.multimodal_mode_api_provider]["base_url"]),
                            setattr(st.session_state, "multimodal_mode_model", API_PRESETS[st.session_state.multimodal_mode_api_provider]["default_model"])
                        ]
                    )
                    st.text_input("API Key", key="multimodal_mode_api_key", type="password")
                    st.text_input("接口地址", key="multimodal_mode_base_url", value=st.session_state.multimodal_mode_base_url)
                    st.text_input("模型名", key="multimodal_mode_model", value=st.session_state.multimodal_mode_model)
                    
                    # 图片输入
                    st.write("### 🖼️ 图片输入（可选）")
                    uploaded_image = st.file_uploader(
                        "上传参考图", 
                        type=["png", "jpg", "jpeg"], 
                        key="multimodal_mode_uploaded_image"
                    )
                    if uploaded_image:
                        st.image(uploaded_image, caption="已上传参考图", width=200)
                    st.text_input("或图片URL", key="multimodal_mode_image_url")
            
            # 第二部分：小说信息输入
            with st.container(border=True):
                st.subheader("📝 小说信息")
                st.write('<div class="tag tag-primary">内容输入</div>', unsafe_allow_html=True)
                
                st.text_input("小说标题", key="novel_title", placeholder="如：三体·黑暗森林")
                st.text_input("小说作者", key="novel_author", placeholder="如：刘慈欣")
                st.text_area("多章节背景（可选）", key="novel_background", height=100, placeholder="粘贴小说整体设定...")
                st.text_area("目标章节内容（必填）", key="novel_target_chapter", height=250, placeholder="粘贴目标章节内容...")
        
        with main_right:
            # 第一部分：操作面板（导演和分镜生成）
            with st.container(border=True):
                st.subheader("🎬 分镜创作面板")
                st.write('<div class="tag tag-primary">核心操作</div>', unsafe_allow_html=True)
                
                # 导演推荐和风格生成
                row1 = st.columns([2, 2, 2])
                with row1[0]:
                    st.button(
                        "🔍 智能推荐导演",
                        on_click=lambda: ai_recommend_director(uploaded_image=uploaded_image if 'uploaded_image' in locals() else None),
                        type="secondary",
                        disabled=not st.session_state.novel_target_chapter.strip() or st.session_state.is_running
                    )
                with row1[1]:
                    selected_dir = st.session_state.selected_director or st.session_state.custom_director_name
                    st.button(
                        "✨ 生成导演风格",
                        on_click=lambda: generate_director_persona(uploaded_image=uploaded_image if 'uploaded_image' in locals() else None),
                        type="secondary",
                        disabled=not selected_dir or st.session_state.is_running
                    )
                with row1[2]:
                    st.button(
                        "🗑️ 清空导演列表",
                        on_click=lambda: st.session_state.update({
                            "director_recommend_list": [], 
                            "selected_director": "", 
                            "director_persona": "", 
                            "director_style_tags": [], 
                            "director_radio": ""
                        }),
                        type="secondary",
                        disabled=st.session_state.is_running
                    )
                
                # 自定义导演和分镜生成
                row2 = st.columns([3, 2, 2])
                with row2[0]:
                    custom_dir = st.text_input("自定义导演姓名", key="custom_director_name", placeholder="输入后自动选中该导演")
                    if custom_dir and custom_dir.strip():
                        st.session_state.selected_director = custom_dir.strip()
                with row2[1]:
                    st.button(
                        "🎬 生成分镜",
                        on_click=lambda: generate_storyboards(uploaded_image=uploaded_image if 'uploaded_image' in locals() else None),
                        type="primary",
                        disabled=not st.session_state.novel_target_chapter.strip() or st.session_state.is_running
                    )
                with row2[2]:
                    st.button(
                        "🌟 一键全自动生成",
                        on_click=lambda: one_click_generate(uploaded_image=uploaded_image if 'uploaded_image' in locals() else None),
                        type="primary",
                        disabled=not st.session_state.novel_target_chapter.strip() or st.session_state.is_running
                    )
                
                # 导演列表展示
                if st.session_state.director_recommend_list:
                    with st.expander("🎯 适配导演推荐列表", expanded=False):
                        director_names = [d["name"] for d in st.session_state.director_recommend_list]
                        selected_name = st.radio(
                            "选择导演",
                            options=director_names,
                            key="director_radio",
                            index=director_names.index(st.session_state.director_radio) if st.session_state.director_radio in director_names else 0,
                            on_change=lambda: setattr(st.session_state, "selected_director", st.session_state.director_radio),
                            horizontal=True
                        )
                        
                        selected_director = next((d for d in st.session_state.director_recommend_list if d["name"] == selected_name), None)
                        if selected_director:
                            st.write(f"**核心标签**：{selected_director['style']}")
                            st.write(f"**适配手法**：{selected_director['reason']}")
                            st.write(f"**分镜优势**：{selected_director['advantage']}")
                
                # 导演风格展示
                if st.session_state.director_persona:
                    with st.expander("🎨 导演视觉风格指令", expanded=False):
                        st.write(st.session_state.director_persona)
                        st.write(f"**题材专属标签**：{', '.join(st.session_state.director_style_tags)}")
            
            # 第二部分：分镜校验和优化
            if st.session_state.storyboards:
                with st.container(border=True):
                    st.subheader("🔍 分镜校验与优化")
                    st.write('<div class="tag tag-warning">质量控制</div>', unsafe_allow_html=True)
                    
                    # 校验按钮
                    row_validate = st.columns([2, 2])
                    with row_validate[0]:
                        st.button(
                            "🔍 校验分镜一致性",
                            on_click=lambda: validate_storyboard_consistency(uploaded_image=uploaded_image if 'uploaded_image' in locals() else None),
                            type="secondary"
                        )
                    with row_validate[1]:
                        st.button(
                            "✨ 一键应用优化建议",
                            on_click=apply_validation_suggestions,
                            type="primary",
                            disabled=not st.session_state.validation_suggestions
                        )
                    
                    # 校验结果展示
                    if st.session_state.validation_result:
                        with st.expander("📋 校验结果与优化建议", expanded=True):
                            st.write(st.session_state.validation_result)
                            
                            # 建议列表
                            if st.session_state.validation_suggestions:
                                st.write("### 🎯 可应用的优化建议：")
                                for idx, suggestion in enumerate(st.session_state.validation_suggestions):
                                    st.write(f"{idx+1}. {suggestion}")
            
            # 第三部分：分镜结果展示
            if st.session_state.storyboards:
                with st.container(border=True):
                    st.subheader("🎞️ 分镜生成结果")
                    st.write('<div class="tag tag-success">成果展示</div>', unsafe_allow_html=True)
                    
                    # 筛选功能
                    filter_row = st.columns([2, 2, 2])
                    with filter_row[0]:
                        emotion_filter = st.selectbox("按情绪筛选", options=["全部"] + list(set([s["emotion"] for s in st.session_state.storyboards])))
                    with filter_row[1]:
                        character_filter = st.selectbox("按人物筛选", options=["全部", "是", "否"])
                    with filter_row[2]:
                        st.download_button(
                            "💾 批量导出所有提示词",
                            data="\n\n=== 分割线 ===\n\n".join([
                                f"镜头 {i+1}：\n正向提示词：{sb['optimized_prompt']}\n负向提示词：{sb['negative_prompt']}"
                                for i, sb in enumerate(st.session_state.storyboards)
                            ]),
                            file_name=f"{st.session_state.novel_title or '小说分镜'}_完整提示词包.txt",
                            mime="text/plain"
                        )
                    
                    # 筛选分镜
                    filtered_storyboards = st.session_state.storyboards
                    if emotion_filter != "全部":
                        filtered_storyboards = [s for s in filtered_storyboards if s["emotion"] == emotion_filter]
                    if character_filter != "全部":
                        filtered_storyboards = [s for s in filtered_storyboards if s["has_character"] == character_filter]
                    
                    # 分镜展示（带复制按钮）
                    for idx, sb in enumerate(filtered_storyboards):
                        scene_core = sb['scene'].split('：')[1].split('\n')[0] if '：' in sb['scene'] else '未命名'
                        with st.expander(f"📸 镜头 {idx+1}：{scene_core}", expanded=False):
                            # 分镜基础信息
                            col_info, col_prompts = st.columns([1, 1])
                            
                            with col_info:
                                st.write("### 📝 分镜信息")
                                st.write(f"**情绪**：{sb['emotion']}")
                                st.write(f"**镜头**：{sb['camera']}")
                                st.write(f"**氛围**：{sb['atmosphere']}")
                                st.write(f"**有人物**：{sb['has_character']}")
                                
                                if sb['has_character'] == "是":
                                    st.write(f"**人物特征**：{sb['character_feature'][:100]}...")
                                st.write(f"**场景细节**：{sb['environment'][:100]}...")
                            
                            with col_prompts:
                                # 优化提示词（带复制）
                                st.write("### 🎨 优化提示词（推荐）")
                                optimized_text = st.text_area(
                                    "正向提示词", 
                                    value=sb['optimized_prompt'], 
                                    height=120, 
                                    key=f"optimized_{idx}"
                                )
                                copy_to_clipboard_button(optimized_text, "📋 复制正向", f"optimized_{idx}")
                                
                                # 负向提示词（带复制）
                                negative_text = st.text_area(
                                    "负向提示词", 
                                    value=sb['negative_prompt'], 
                                    height=80, 
                                    key=f"negative_{idx}"
                                )
                                copy_to_clipboard_button(negative_text, "📋 复制负向", f"negative_{idx}")
                            
                            # AI提示词（带复制）
                            st.write("### 🔧 AI生图/视频提示词")
                            ai_col1, ai_col2 = st.columns([1, 1])
                            
                            with ai_col1:
                                comfy_text = st.text_area(
                                    "ComfyUI提示词（英文）", 
                                    value=sb['comfyui_prompt'], 
                                    height=100, 
                                    key=f"comfy_{idx}"
                                )
                                copy_to_clipboard_button(comfy_text, "📋 复制", f"comfy_{idx}")
                            
                            with ai_col2:
                                video_text = st.text_area(
                                    "视频提示词", 
                                    value=sb['video_prompt'], 
                                    height=100, 
                                    key=f"video_{idx}"
                                )
                                copy_to_clipboard_button(video_text, "📋 复制", f"video_{idx}")
    
    # 使用指南标签页
    with tab2:
        st.subheader("📖 使用指南")
        st.markdown("""
        ### 🔧 基础配置
        1. 选择API服务商并填写API Key、接口地址和模型名
        2. 图文模式可上传参考图片或填写图片URL
        
        ### 📝 内容输入
        1. 填写小说标题、作者（可选）
        2. 粘贴目标章节内容（必填）
        
        ### 🎬 分镜创作
        1. 点击「智能推荐导演」获取适配导演列表
        2. 选择导演后点击「生成导演风格」
        3. 点击「生成分镜」开始创作
        
        ### 🔍 质量控制
        1. 分镜生成后可点击「校验分镜一致性」
        2. 点击「一键应用优化建议」自动更新所有提示词
        
        ### 💡 功能亮点
        - ✨ 支持任意小说类型，自动提取核心人物和空间关系
        - ✨ 所有提示词均带复制按钮，一键复制使用
        - ✨ 分镜一致性校验，确保人物和空间关系统一
        - ✨ 一键应用优化建议，无需手动修改
        """)

# 主函数（仅初始化+渲染UI）
def main():
    init_basic_config()
    init_session_state()
    render_page_layout()

if __name__ == "__main__":
    main()
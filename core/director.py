import streamlit as st
from .llm import call_llm

def ai_recommend_director(auto=False, uploaded_image=None):
    """
    智能推荐适配小说题材的导演
    :param auto: 是否全自动模式（无弹窗提示）
    :param uploaded_image: 参考图片（图文模式）
    :return: 是否推荐成功
    """
    if not st.session_state.novel_target_chapter.strip():
        if not auto:
            st.warning("⚠️ 请先填写目标章节内容！")
        return False

    with st.spinner("🔍 分析小说风格，推荐适配导演..." if not auto else "自动推荐导演中..."):
        # 分析小说类型/特质/适配需求
        analyze_prompt = f"""分析以下小说文本，严格按格式返回3项内容（无额外说明）：
1. 类型：精准题材（如修仙/古风、科幻/星际、悬疑/灵异、都市/情感）
2. 特质：核心标签（3个以内，如“修仙-斗法密集、古风-权谋”）
3. 适配需求：改编分镜需强化的点（如“斗法动作拆解、权谋氛围铺垫”）

小说文本：
{st.session_state.novel_target_chapter[:2000]}"""
        analyze_result = call_llm(analyze_prompt, temperature=0.3, uploaded_image=uploaded_image)
        
        # 解析分析结果
        if not analyze_result:
            st.session_state.novel_type = "未知类型"
            st.session_state.novel_trait = "均衡型"
            st.session_state.adapt_demand = "情节还原+情绪表达"
        else:
            parts = [p.strip() for p in analyze_result.split("\n") if p.strip()]
            st.session_state.novel_type = parts[0].replace("1. 类型：", "") if len(parts)>=1 else "未知类型"
            st.session_state.novel_trait = parts[1].replace("2. 特质：", "") if len(parts)>=2 else "均衡型"
            st.session_state.adapt_demand = parts[2].replace("3. 适配需求：", "") if len(parts)>=3 else "情节还原+情绪表达"

        # 生成导演推荐列表
        prompt = f"""根据小说【{st.session_state.novel_type}】（特质：{st.session_state.novel_trait}，改编需求：{st.session_state.adapt_demand}），推荐3位擅长该题材改编的导演，严格按格式返回：
1. 每行一个导演，格式：导演姓名|核心改编标签（3个以内）|题材适配手法（15字内）|分镜优势（20字内）
2. 仅返回3行内容，无额外标题/注释

示例（修仙题材）：
林玉芬|修仙斗法、古风氛围、情绪铺垫|斗法动作分层拆解|擅长灵韵特效视觉化
"""
        result = call_llm(prompt, temperature=0.7, uploaded_image=uploaded_image)

        # 解析推荐结果（无结果则用默认列表）
        if not result:
            # 按题材适配默认导演
            if "修仙" in st.session_state.novel_type or "古风" in st.session_state.novel_type:
                default_list = [
                    {"name": "林玉芬", "style": "修仙斗法,古风氛围,情绪铺垫", "reason": "斗法动作分层拆解", "advantage": "灵韵特效视觉化，贴合修仙"},
                    {"name": "郑伟文", "style": "古装权谋,动作设计,群戏调度", "reason": "权谋氛围递进", "advantage": "多人物分镜逻辑清晰"},
                    {"name": "黄伟明", "style": "古风细节,情绪微变,场景还原", "reason": "古风场景精准落地", "advantage": "贴合小说文本细节"}
                ]
            elif "科幻" in st.session_state.novel_type:
                default_list = [
                    {"name": "诺兰", "style": "硬核科幻,时空逻辑,视觉冲击", "reason": "机甲特效分层", "advantage": "科幻场景叙事感强"},
                    {"name": "丹尼斯·维伦纽瓦", "style": "科幻氛围,细节质感,慢镜头", "reason": "星际场景还原", "advantage": "情绪与特效平衡"},
                    {"name": "今石洋之", "style": "机甲动作,快剪节奏,视觉张力", "reason": "机甲打斗拆解", "advantage": "动态漫快剪适配"}
                ]
            else:
                default_list = [
                    {"name": "彭发", "style": "悬疑惊悚,慢节奏,细节冲击", "reason": "适配情节转折", "advantage": "情绪分镜精准"},
                    {"name": "是枝裕和", "style": "日常情感,心理刻画,氛围", "reason": "情绪微变捕捉", "advantage": "贴合小说日常描写"},
                    {"name": "罗泓轸", "style": "社会悬疑,冷峻写实,节奏", "reason": "冲突场景拆解", "advantage": "分镜张力拉满"}
                ]
            st.session_state.director_recommend_list = default_list
        else:
            recommend_list = []
            for line in result.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >=4:
                    name, style, reason, advantage = parts[0], parts[1], parts[2], parts[3]
                elif len(parts) == 3:
                    name, style, reason, advantage = parts[0], parts[1], parts[2], "贴合题材改编"
                else:
                    continue
                recommend_list.append({
                    "name": name, "style": style, "reason": reason, "advantage": advantage
                })
            st.session_state.director_recommend_list = recommend_list if recommend_list else [
                {"name": "彭发", "style": "悬疑惊悚,慢节奏,细节冲击", "reason": "适配情节转折", "advantage": "情绪分镜精准"}
            ]

        # 默认选中第一个导演
        if st.session_state.director_recommend_list:
            first_director = st.session_state.director_recommend_list[0]["name"]
            st.session_state.selected_director = first_director
            st.session_state.director_radio = first_director

        if not auto:
            st.success(f"✅ 推荐完成！共找到{len(st.session_state.director_recommend_list)}位适配导演")
        return True

def generate_director_persona(auto=False, uploaded_image=None):
    """
    生成选中导演的视觉风格指令
    :param auto: 是否全自动模式
    :param uploaded_image: 参考图片
    :return: 是否生成成功
    """
    # 自动模式默认选第一个推荐导演
    if auto and st.session_state.director_recommend_list:
        st.session_state.selected_director = st.session_state.director_recommend_list[0]["name"]

    # 校验导演姓名
    selected_dir = st.session_state.selected_director or st.session_state.custom_director_name
    if not selected_dir or selected_dir.strip() == "":
        if not auto:
            st.warning("⚠️ 请先选择/输入导演姓名！")
        return False

    # 读取基础配置
    complexity = st.session_state.complexity if st.session_state.complexity else "均衡型"
    adapt_demand = st.session_state.adapt_demand if st.session_state.adapt_demand else "情节还原+情绪表达"
    genre = st.session_state.novel_type if st.session_state.novel_type else "未知类型"

    with st.spinner(f"🎭 生成{selected_dir}的风格..." if not auto else f"自动生成{selected_dir}风格中..."):
        prompt = f"""提取导演【{selected_dir}】的核心创作特征，结合【{genre}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），生成适配AI分镜的视觉+节奏指令，严格按以下要求输出：
1.  分5点，每条用短横线开头，仅保留可落地的分镜执行细节；
2.  视觉维度：色调/光影/构图，绑定题材特质；
3.  动作处理：动作戏强化拆解逻辑；
4.  节奏把控：明确快剪/慢镜适用场景；
5.  细节偏好：针对题材专属元素的处理。

要求：内容贴合导演真实风格+题材需求，每条简洁精准。"""
        result = call_llm(prompt, temperature=0.6, uploaded_image=uploaded_image)

        if result:
            # 生成题材专属标签
            if "修仙" in genre or "古风" in genre:
                style_tags = ["灵韵特效通透", "古风服饰纹理清晰", "斗法动作分层"]
            elif "科幻" in genre:
                style_tags = ["机甲细节拉满", "星际场景纵深感", "科幻特效克制"]
            elif "悬疑" in genre:
                style_tags = ["阴影占比提升", "镜头留白营造悬念", "微表情特写"]
            else:
                style_tags = ["色调统一", "光影自然", "构图平衡"]
            
            st.session_state.director_style_tags = style_tags
            st.session_state.director_persona = result
            if not auto:
                st.success(f"✅ {selected_dir}的{genre}适配风格生成完成！")
            return True
        else:
            if not auto:
                st.error("❌ 生成失败，请检查API配置！")
            return False
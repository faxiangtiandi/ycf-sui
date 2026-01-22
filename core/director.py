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
1. 类型：精准题材（如修仙/凡人修仙传、稳健修仙/师兄太稳健了、逆天修仙/仙逆、科幻/星际、悬疑/灵异、都市/情感）
2. 特质：核心标签（3个以内，如"修仙-斗法密集、稳健-步步为营、逆天-复仇驱动"）
3. 适配需求：改编分镜需强化的点（如"斗法动作拆解、情绪节奏把控、场景氛围营造"）

小说文本：
{st.session_state.novel_target_chapter[:2000]}"""
        analyze_result = call_llm(analyze_prompt, temperature=0.3, uploaded_image=uploaded_image, is_comic_creation=False)
        
        # 解析分析结果并生成导演推荐列表
        if not analyze_result:
            st.session_state.novel_type = "未知类型"
            st.session_state.novel_trait = "均衡型"
            st.session_state.adapt_demand = "情节还原+情绪表达"
        else:
            parts = [p.strip() for p in analyze_result.split("\n") if p.strip()]
            st.session_state.novel_type = parts[0].replace("1. 类型：", "") if len(parts) >= 1 else "未知类型"
            st.session_state.novel_trait = parts[1].replace("2. 特质：", "") if len(parts) >= 2 else "均衡型"
            st.session_state.adapt_demand = parts[2].replace("3. 适配需求：", "") if len(parts) >= 3 else "情节还原+情绪表达"

        # 生成导演推荐列表
        prompt = f"""作为资深内容改编顾问，根据小说【{st.session_state.novel_type}】（特质：{st.session_state.novel_trait}，改编需求：{st.session_state.adapt_demand}），从全球顶尖导演/漫画家人才库中推荐最适合的专家，严格按格式返回：
    1. 每行一个专家，格式：专家姓名|专业领域特长（3个以内）|改编理念（15字内）|分镜优势（20字内）
    2. 返回任意数量的专家（至少1个，最多不限），仅返回内容，无额外标题/注释

    要求：推荐参考全球顶尖导演/漫画家的人格化智能体，包括：
    - 电影导演：王家卫（氛围营造）、诺兰（结构设计）、黑泽明（视觉叙事）
    - 动画导演：宫崎骏（情感细腻）、今敏（现实与梦境）、新海诚（画面美感）
    - 漫画家：鸟山明（动作设计）、青山刚昌（悬疑布局）、尾田荣一郎（节奏把控）
    - 国产动画导演：原力动画团队（真人动捕技术）、铸梦动画团队（特效表现）

    人格化智能体设计要点：
    - 王家卫：擅长氛围营造，光影运用独特，情感表达细腻
    - 诺兰：结构设计大师，非线性叙事，时间操控能力强
    - 宫崎骏：环保主题，人文关怀，细腻情感表达
    - 新海诚：画面美感，青春主题，光影表现力强
    - 鸟山明：动作设计简洁有力，角色个性鲜明
    - 尾田荣一郎：节奏把控精准，团队协作，世界观构建"""

        director_list = call_llm(prompt, temperature=0.3, uploaded_image=uploaded_image, is_comic_creation=False)
        st.session_state.director_recommend_list = director_list.split('\n') if director_list else []

        # 添加可编辑区域让用户修改推荐结果
        st.text_area("编辑推荐结果", value='\n'.join(st.session_state.director_recommend_list), key="edit_director_recommendations")

        return True if st.session_state.director_recommend_list else False


def generate_director_persona_simple(director_name, novel_type, complexity, adapt_demand):
    """
    生成导演的智能体人格描述
    :param director_name: 导演名称
    :param novel_type: 小说类型
    :param complexity: 情节复杂度
    :param adapt_demand: 改编需求
    :return: 导演人格描述
    """
    # 根据导演名称生成对应的人格描述
    persona_map = {
        "王家卫": "擅长氛围营造，光影运用独特，情感表达细腻",
        "诺兰": "结构设计大师，非线性叙事，时间操控能力强",
        "黑泽明": "视觉叙事大师，构图美学，人物塑造经典",
        "宫崎骏": "环保主题，人文关怀，细腻情感表达",
        "新海诚": "画面美感，青春主题，光影表现力强",
        "鸟山明": "动作设计简洁有力，角色个性鲜明",
        "青山刚昌": "悬疑布局，推理逻辑严密",
        "尾田荣一郎": "节奏把控精准，团队协作，世界观构建",
        "原力动画团队": "真人动捕技术，UE5渲染，细节把控",
        "铸梦动画团队": "特效表现，快节奏战斗，宏大场景"
    }
    
    return persona_map.get(director_name, "专业导演，擅长各类题材的改编")
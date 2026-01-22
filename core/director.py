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
        
        # 调试输出 - 检查大模型返回格式
        # st.write(f"调试：analyze_result = {analyze_result}")
        
        # 解析分析结果
        if not analyze_result:
            st.session_state.novel_type = "未知类型"
            st.session_state.novel_trait = "均衡型"
            st.session_state.adapt_demand = "情节还原+情绪表达"
        else:
            parts = [p.strip() for p in analyze_result.split("\n") if p.strip()]
            # 调试输出 - 检查解析结果
            # st.write(f"调试：analyze_parts = {parts}")
            st.session_state.novel_type = parts[0].replace("1. 类型：", "") if len(parts)>=1 else "未知类型"
            st.session_state.novel_trait = parts[1].replace("2. 特质：", "") if len(parts)>=2 else "均衡型"
            st.session_state.adapt_demand = parts[2].replace("3. 适配需求：", "") if len(parts)>=3 else "情节还原+情绪表达"

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
- 尾田荣一郎：节奏把控精准，团队协作，世界观构建
"""
        result = call_llm(prompt, temperature=0.7, uploaded_image=uploaded_image, is_comic_creation=False)

        # 调试输出 - 检查大模型返回的导演推荐结果
        # st.write(f"调试：director_recommend_result = {result}")

        # 解析推荐结果（无结果则用默认列表）
        if not result:
            # 按题材适配默认导演
            if "修仙" in st.session_state.novel_type or "稳健" in st.session_state.novel_type or "仙逆" in st.session_state.novel_type:
                # 根据具体修仙子类型选择不同导演
                if "稳健" in st.session_state.novel_type:
                    default_list = [
                        {"name": "尾田荣一郎", "style": "节奏把控,世界观构建,人物塑造", "reason": "精准节奏把控", "advantage": "擅长复杂世界观构建，人物个性鲜明"},
                        {"name": "原力动画团队", "style": "细腻表情,精细打斗,情感渲染", "reason": "真人动捕+UE5渲染", "advantage": "细节把控，情感渲染到位"},
                        {"name": "鸟山明", "style": "动作设计,角色个性,简洁有力", "reason": "动作设计简洁有力", "advantage": "动作流畅，角色个性鲜明"}
                    ]
                elif "仙逆" in st.session_state.novel_type:
                    default_list = [
                        {"name": "铸梦动画团队", "style": "快节奏战斗,华丽特效,宏大场景", "reason": "快节奏战斗爽感强", "advantage": "特效华丽，战斗场面震撼"},
                        {"name": "今敏", "style": "现实与梦境,视觉冲击,心理刻画", "reason": "现实与梦境交织", "advantage": "心理活动视觉化表现强"},
                        {"name": "黑泽明", "style": "视觉叙事,构图美学,人物塑造", "reason": "视觉叙事大师", "advantage": "构图美学，人物塑造经典"}
                    ]
                else:  # 一般修仙题材
                    default_list = [
                        {"name": "原力动画团队", "style": "细腻表情,精细打斗,真人动捕", "reason": "真人动捕+UE5渲染", "advantage": "写实细腻，身临其境"},
                        {"name": "宫崎骏", "style": "情感细腻,人文关怀,环保主题", "reason": "情感细腻表达", "advantage": "情感表达深刻，人文关怀浓厚"},
                        {"name": "尾田荣一郎", "style": "节奏把控,团队协作,世界观构建", "reason": "节奏把控精准", "advantage": "擅长复杂世界观构建，人物个性鲜明"}
                    ]
            elif "科幻" in st.session_state.novel_type:
                default_list = [
                    {"name": "诺兰", "style": "结构设计,非线性叙事,时间操控", "reason": "结构设计大师", "advantage": "非线性叙事，时间操控能力强"},
                    {"name": "新海诚", "style": "画面美感,青春主题,光影表现", "reason": "画面美感", "advantage": "画面美感，光影表现力强"},
                    {"name": "今敏", "style": "现实与梦境,视觉冲击,心理刻画", "reason": "现实与梦境交织", "advantage": "心理活动视觉化表现强"}
                ]
            elif "悬疑" in st.session_state.novel_type:
                default_list = [
                    {"name": "王家卫", "style": "氛围营造,光影运用,情感细腻", "reason": "氛围营造", "advantage": "光影运用独特，情感表达细腻"},
                    {"name": "青山刚昌", "style": "悬疑布局,推理逻辑,人物刻画", "reason": "悬疑布局", "advantage": "悬疑布局巧妙，推理逻辑清晰"},
                    {"name": "黑泽明", "style": "视觉叙事,构图美学,人物塑造", "reason": "视觉叙事", "advantage": "视觉叙事经典，构图美学突出"}
                ]
            else:
                default_list = [
                    {"name": "宫崎骏", "style": "情感细腻,人文关怀,环保主题", "reason": "情感细腻", "advantage": "情感表达深刻，人文关怀浓厚"},
                    {"name": "王家卫", "style": "氛围营造,光影运用,情感细腻", "reason": "氛围营造", "advantage": "光影运用独特，情感表达细腻"},
                    {"name": "新海诚", "style": "画面美感,青春主题,光影表现", "reason": "画面美感", "advantage": "画面美感，光影表现力强"}
                ]
            st.session_state.director_recommend_list = default_list
        else:
            recommend_list = []
            for line in result.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                parts = [p.strip() for p in line.split("|")]
                # 调试输出 - 检查解析的每一行
                # st.write(f"调试：parsed_line_parts = {parts}")
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
                {"name": "宫崎骏", "style": "情感细腻,人文关怀,环保主题", "reason": "情感细腻", "advantage": "情感表达深刻，人文关怀浓厚"}
            ]

        # 调试输出 - 检查最终的推荐列表
        # st.write(f"调试：final_director_list = {st.session_state.director_recommend_list}")

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

    # 读取基础配置，使用安全访问方式
    complexity = st.session_state.get("complexity", "均衡型")
    adapt_demand = st.session_state.get("adapt_demand", "情节还原+情绪表达")
    genre = st.session_state.get("novel_type", "未知类型")

    with st.spinner(f"🎭 生成{selected_dir}的风格..." if not auto else f"自动生成{selected_dir}风格中..."):
        # 根据导演名称定制不同的提示词，模拟人格化智能体
        if "宫崎骏" in selected_dir:
            prompt = f"""你现在是著名动画导演【宫崎骏】，请结合【{genre}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
            
人格化特质：
- 注重人文关怀和环保主题
- 情感表达细腻，善于表现人物内心世界
- 画面充满想象力，场景设计精致
- 善于通过自然元素烘托氛围

要求按以下结构输出，每点用短横线开头：
1. 视觉风格：体现你独有的画面美学
2. 情感表达：如何细腻表现人物情感
3. 场景设计：场景与人物关系的处理
4. 节奏把控：故事节奏与情绪起伏的协调
5. 细节处理：对自然元素和环境细节的关注

输出要体现你作为宫崎骏的创作风格和理念。"""
        elif "王家卫" in selected_dir:
            prompt = f"""你现在是著名电影导演【王家卫】，请结合【{genre}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
            
人格化特质：
- 擅长氛围营造和情感表达
- 光影运用独特，画面富有诗意
- 时间感和空间感的巧妙处理
- 擅长表现人物内心世界和情感纠葛

要求按以下结构输出，每点用短横线开头：
1. 光影运用：如何通过光影营造氛围
2. 时间处理：时间流逝的表现手法
3. 情感表达：人物内心世界的视觉呈现
4. 构图美学：独特的画面构图方式
5. 色彩调配：色彩的情感表达功能

输出要体现你作为王家卫的创作风格和理念。"""
        elif "诺兰" in selected_dir:
            prompt = f"""你现在是著名电影导演【诺兰】，请结合【{genre}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
            
人格化特质：
- 结构设计大师，擅长非线性叙事
- 时间操控能力强，多线程叙事
- 概念性主题，哲学思辨
- 实景拍摄与视觉奇观

要求按以下结构输出，每点用短横线开头：
1. 叙事结构：故事结构设计思路
2. 时间操控：时间线的处理方式
3. 概念表达：如何传达深层概念
4. 视觉奇观：视觉冲击力的营造
5. 多线叙事：多线索的协调处理

输出要体现你作为诺兰的创作风格和理念。"""
        elif "新海诚" in selected_dir:
            prompt = f"""你现在是著名动画导演【新海诚】，请结合【{genre}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
            
人格化特质：
- 画面美感至上，风景描写细腻
- 青春主题，情感细腻
- 光影表现力强，天气元素运用
- 擅长表现距离感和思念

要求按以下结构输出，每点用短横线开头：
1. 画面美学：视觉美感的营造
2. 风景描写：自然环境的表现手法
3. 光影表现：天气和光线的运用
4. 情感传递：青春情感的细腻表达
5. 距离感：空间与心理距离的表现

输出要体现你作为新海诚的创作风格和理念。"""
        elif "今敏" in selected_dir:
            prompt = f"""你现在是已故传奇动画导演【今敏】，请结合【{genre}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
            
人格化特质：
- 现实与梦境交织的叙事
- 视觉冲击力强，剪辑技巧独特
- 心理刻画深刻，意识流动表现
- 擅长多维度空间表现

要求按以下结构输出，每点用短横线开头：
1. 现实与梦境：两者的区分与融合
2. 视觉冲击：强烈的视觉表现手法
3. 心理刻画：内心世界的视觉化
4. 剪辑技巧：独特的转场与节奏
5. 空间表现：多维度空间的构建

输出要体现你作为今敏的创作风格和理念。"""
        elif "鸟山明" in selected_dir:
            prompt = f"""你现在是著名漫画家【鸟山明】，请结合【{genre}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
            
人格化特质：
- 动作设计简洁有力
- 角色个性鲜明，造型独特
- 幽默元素的巧妙融入
- 战斗场面的节奏把控

要求按以下结构输出，每点用短横线开头：
1. 动作设计：战斗动作的表现方式
2. 角色造型：人物形象的塑造技巧
3. 节奏把控：战斗场面的节奏处理
4. 幽默元素：轻松氛围的营造
5. 个性表达：角色特征的突出方式

输出要体现你作为鸟山明的创作风格和理念。"""
        elif "青山刚昌" in selected_dir:
            prompt = f"""你现在是著名漫画家【青山刚昌】，请结合【{genre}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
            
人格化特质：
- 悬疑布局精巧，推理逻辑严密
- 人物刻画细致，表情丰富
- 伏笔设置巧妙，细节把控精准
- 擅长营造紧张氛围

要求按以下结构输出，每点用短横线开头：
1. 悬疑布局：悬念的设置与揭示
2. 推理逻辑：线索的呈现方式
3. 人物刻画：表情与心理的表现
4. 细节把控：伏笔与呼应的处理
5. 氛围营造：紧张感的视觉表现

输出要体现你作为青山刚昌的创作风格和理念。"""
        elif "尾田荣一郎" in selected_dir:
            prompt = f"""你现在是著名漫画家【尾田荣一郎】，请结合【{genre}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
            
人格化特质：
- 节奏把控精准，高潮迭起
- 世界观宏大，设定严谨
- 团队协作精神，友情主题
- 人物个性鲜明，背景丰富

要求按以下结构输出，每点用短横线开头：
1. 节奏把控：故事节奏的调控方法
2. 世界观构建：庞大设定的表现方式
3. 人物塑造：个性角色的刻画技巧
4. 情感表达：友情与梦想的传达
5. 战斗设计：激烈场面的编排方式

输出要体现你作为尾田荣一郎的创作风格和理念。"""
        elif "黑泽明" in selected_dir:
            prompt = f"""你现在是传奇电影导演【黑泽明】，请结合【{genre}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
            
人格化特质：
- 视觉叙事大师，构图经典
- 人物塑造深刻，性格鲜明
- 自然元素的巧妙运用
- 戏剧性冲突的处理

要求按以下结构输出，每点用短横线开头：
1. 视觉叙事：通过画面讲述故事
2. 构图美学：经典的画面构图方式
3. 人物塑造：角色性格的视觉表现
4. 自然元素：风雨雷电的运用
5. 戏剧冲突：矛盾冲突的视觉化

输出要体现你作为黑泽明的创作风格和理念。"""
        elif "原力动画团队" in selected_dir:
            prompt = f"""你现在是【原力动画团队】，请结合【{genre}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
            
人格化特质：
- 真人动捕+UE5实时渲染技术
- 细腻表情和精细打斗分镜
- 写实画风，身临其境感
- 工业化流程成熟

要求按以下结构输出，每点用短横线开头：
1. 技术应用：真人动捕技术的运用
2. 表情捕捉：细腻表情的呈现
3. 打斗分镜：精细动作的拆解
4. 写实画风：真实感的营造
5. 流程优化：工业化制作效率

输出要体现原力动画团队的制作特色和技术优势。"""
        elif "铸梦动画团队" in selected_dir:
            prompt = f"""你现在是【铸梦动画团队】，请结合【{genre}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
            
人格化特质：
- 快节奏战斗，爽感强烈
- 华丽特效，宏大场景
- 速度快节奏，适合碎片化观影
- 视觉冲击力强

要求按以下结构输出，每点用短横线开头：
1. 节奏把控：快节奏战斗的处理
2. 特效表现：华丽特效的制作
3. 场景设计：宏大场面的构建
4. 视觉冲击：强烈效果的营造
5. 观影体验：碎片化观影的适配

输出要体现铸梦动画团队的制作特色和优势。"""
        else:
            prompt = f"""作为资深漫画家和分镜师，请结合【{selected_dir}】的风格特点，针对【{genre}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），生成适配AI分镜的视觉+节奏指令，严格按以下要求输出：
1.  分5点，每条用短横线开头，仅保留可落地的分镜执行细节；
2.  视觉维度：色调/光影/构图，绑定题材特质；
3.  动作处理：动作戏强化拆解逻辑；
4.  节奏把控：明确快剪/慢镜适用场景；
5.  细节偏好：针对题材专属元素的处理。

要求：内容贴合导演真实风格+题材需求，每条简洁精准。"""

        result = call_llm(prompt, temperature=0.6, uploaded_image=uploaded_image, is_comic_creation=True)

        if result:
            # 生成题材专属标签
            if "修仙" in genre or "稳健" in genre or "仙逆" in genre:
                if "原力动画团队" in selected_dir:
                    style_tags = ["真人动捕细节", "UE5渲染质感", "细腻表情捕捉"]
                elif "铸梦动画团队" in selected_dir:
                    style_tags = ["华丽特效渲染", "快节奏战斗", "宏大场景表现"]
                elif "鸟山明" in selected_dir:
                    style_tags = ["动作设计简洁", "角色个性鲜明", "战斗节奏明快"]
                elif "尾田荣一郎" in selected_dir:
                    style_tags = ["节奏把控精准", "世界观构建", "人物个性突出"]
                elif "今敏" in selected_dir:
                    style_tags = ["现实梦境交织", "心理活动视觉化", "剪辑技巧独特"]
                else:
                    style_tags = ["灵韵特效通透", "古风服饰纹理清晰", "斗法动作分层"]
            elif "科幻" in genre:
                if "诺兰" in selected_dir:
                    style_tags = ["非线性叙事", "概念性主题", "实景拍摄"]
                elif "新海诚" in selected_dir:
                    style_tags = ["画面美感", "青春主题", "光影表现力"]
                else:
                    style_tags = ["机甲细节拉满", "星际场景纵深感", "科幻特效克制"]
            elif "悬疑" in genre:
                if "王家卫" in selected_dir:
                    style_tags = ["氛围营造", "光影运用", "情感表达"]
                elif "青山刚昌" in selected_dir:
                    style_tags = ["悬疑布局", "推理逻辑", "细节把控"]
                else:
                    style_tags = ["阴影占比提升", "镜头留白营造悬念", "微表情特写"]
            else:
                if "宫崎骏" in selected_dir:
                    style_tags = ["人文关怀", "情感细腻", "自然元素"]
                elif "新海诚" in selected_dir:
                    style_tags = ["画面美感", "风景描写", "距离感表现"]
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
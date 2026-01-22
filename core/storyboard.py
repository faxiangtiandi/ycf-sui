import streamlit as st
import json
from .llm import call_llm
from .generator import parse_storyboards_from_raw, generate_universal_image_prompt  # 导入缺失的函数

def extract_novel_core_elements(novel_text, uploaded_image=None):
    """
    从小说文本中提取核心元素（人物、场景、情节等）
    :param novel_text: 小说文本内容
    :param uploaded_image: 参考图片（可选）
    :return: 核心元素字典
    """
    # 使用LLM提取核心元素
    prompt = f"""请从以下小说文本中提取核心元素，严格按JSON格式返回：
    {{
        "main_characters": [
            {{
                "name": "姓名",
                "gender": "性别",
                "age": "年龄",
                "appearance": "外貌特征",
                "personality": "性格特点"
            }}
        ],
        "key_scenes": [
            {{
                "scene_name": "场景名称",
                "spatial_relations": "空间关系描述",
                "environment": "环境细节",
                "emotion": "情绪氛围"
            }}
        ],
        "plot_points": [
            {{
                "point": "情节要点",
                "type": "类型（动作/对话/心理）"
            }}
        ]
    }}

    小说文本：
    {novel_text[:2000]}"""
    
    # 调用LLM获取结果
    result = call_llm(prompt, temperature=0.3, uploaded_image=uploaded_image, is_comic_creation=False)
    
    if not result:
        return {
            "main_characters": [{"name": "主角", "gender": "未知", "age": "成年", "appearance": "普通外貌", "personality": "未知"}],
            "key_scenes": [{"scene_name": "默认场景", "spatial_relations": "人物在室内", "environment": "贴合题材场景", "emotion": "平静"}],
            "plot_points": [{"point": "情节开始", "type": "动作"}]
        }
    
    try:
        return json.loads(result)
    except Exception:
        return {
            "main_characters": [{"name": "主角", "gender": "未知", "age": "成年", "appearance": "普通外貌", "personality": "未知"}],
            "key_scenes": [{"scene_name": "默认场景", "spatial_relations": "人物在室内", "environment": "贴合题材场景", "emotion": "平静"}],
            "plot_points": [{"point": "情节开始", "type": "动作"}]
        }


def generate_storyboards(auto=False, uploaded_image=None):
    """
    核心分镜生成函数
    :param auto: 是否全自动模式
    :param uploaded_image: 参考图片
    :return: 是否生成成功
    """
    st.session_state.stop_flag = False
    st.session_state.is_running = True
    
    # 基础校验
    if not st.session_state.novel_target_chapter.strip():
        st.warning("⚠️ 请先填写目标章节内容！")
        st.session_state.is_running = False
        return False
    
    from .llm import get_valid_config
    if not get_valid_config():
        st.error("❌ 无有效API配置！请填写至少一个模式的API信息")
        st.session_state.is_running = False
        return False
    
    # 重置分镜状态
    st.session_state.storyboards = []
    st.session_state.comfyui_prompts = []
    st.session_state.optimized_prompts = []
    st.session_state.negative_prompt = ""
    st.session_state.video_prompts = []
    
    with st.spinner("🎬 生成动态漫分镜..." if not auto else "自动生成分镜中..."):
        # 提取小说核心元素（已包含推荐的导演）
        core_elements = extract_novel_core_elements(st.session_state.novel_target_chapter, uploaded_image)
        
        # 从分析结果中获取推荐的导演
        recommended_director = st.session_state.get("recommended_director", "默认导演")
        recommendation_reason = st.session_state.get("recommendation_reason", "适合该类型小说")
        
        # 分析小说类型和复杂度
        type_prompt = f"分析以下文本的类型，仅返回类型名称：\n{st.session_state.novel_target_chapter[:2000]}"
        st.session_state.novel_type = call_llm(type_prompt, uploaded_image=uploaded_image, is_comic_creation=True) or "未知类型"
        
        complexity_prompt = f"""分析以下文本的情节复杂度，仅返回结果（动作/特效密集型、对话/心理型、均衡型）：
        文本：{st.session_state.novel_target_chapter[:2000]}"""
        complexity = call_llm(complexity_prompt, temperature=0.3, uploaded_image=uploaded_image, is_comic_creation=True) or "均衡型"
        st.session_state.complexity = complexity
        
        # 检查停止标志
        if st.session_state.stop_flag:
            st.warning("⚠️ 生成已手动停止！")
            st.session_state.is_running = False
            return False
        
        # 生成推荐导演的智能体人格
        director_persona = generate_director_persona(recommended_director, st.session_state.novel_type, complexity, st.session_state.complexity)
        st.session_state.director_persona = director_persona
        
        # 构建视觉风格指令
        director_style = st.session_state.director_persona or "冷青灰高对比色调，阴影厚重占比60%，构图紧凑留白少"
        
        # 生成分镜
        prompt = f"""作为专业的分镜设计师，请根据以下信息生成分镜脚本：
        - 小说类型：{st.session_state.novel_type}
        - 情节复杂度：{st.session_state.complexity}
        - 导演风格：{director_style}
        - 核心人物：{core_elements['main_characters'][0]['name']}，{core_elements['main_characters'][0]['gender']}，{core_elements['main_characters'][0]['age']}，{core_elements['main_characters'][0]['appearance']}
        - 关键场景：{core_elements['key_scenes'][0]['scene_name']}，{core_elements['key_scenes'][0]['spatial_relations']}，{core_elements['key_scenes'][0]['environment']}，{core_elements['key_scenes'][0]['emotion']}
        - 情节要点：{core_elements['plot_points'][0]['point']}，{core_elements['plot_points'][0]['type']}

        请按照以下格式输出分镜：
        镜头1：[镜头描述]
        【中文结构化提示词（文生图专用）】
        风格描述：[风格描述]
        镜头方向：[镜头方向]
        艺术风格：[艺术风格]
        画质要求：[画质要求]
        人物特征：[人物特征]
        场景细节：[场景细节]
        【英文结构化提示词（文生图专用）】
        [英文提示词]
        【图生视频专用提示词】
        [视频提示词]
        ===== 分割线：下一个镜头 =====
        """
        
        result = call_llm(prompt, temperature=0.7, uploaded_image=uploaded_image, is_comic_creation=True)
        
        if not result:
            st.error("❌ 分镜生成失败，请检查API配置")
            st.session_state.is_running = False
            return False
        
        # 解析分镜结果
        storyboards = parse_storyboards_from_raw(result, core_elements, st.session_state.novel_type, director_style)
        st.session_state.storyboards = storyboards
        
        # 生成优化后的提示词
        optimized_prompts = []
        for sb in storyboards:
            optimized_prompt = generate_universal_image_prompt(
                {
                    "scene_core": sb["scene_core"],
                    "emotion": sb["emotion"],
                    "camera": sb["camera"],
                    "atmosphere": sb["atmosphere"],
                    "character_feature": sb["character_feature"],
                    "environment": sb["environment"],
                    "visual_style": director_style
                },
                core_elements
            )["positive"]
            optimized_prompts.append(optimized_prompt)
        
        st.session_state.optimized_prompts = optimized_prompts
        
        # 生成ComfyUI提示词
        comfyui_prompts = []
        for sb in storyboards:
            comfyui_prompts.append(sb["comfyui_prompt"])
        
        st.session_state.comfyui_prompts = comfyui_prompts
        
        # 生成视频提示词
        video_prompts = []
        for sb in storyboards:
            video_prompts.append(sb["video_prompt"])
        
        st.session_state.video_prompts = video_prompts
        
        # 生成负向提示词
        negative_prompt = generate_universal_image_prompt({}, core_elements)["negative"]
        st.session_state.negative_prompt = negative_prompt
        
        st.session_state.is_running = False
        return True


def generate_director_persona(director_name, novel_type, complexity, adapt_demand):
    """
    根据推荐的导演名称生成智能体人格
    :param director_name: 推荐的导演名称
    :param novel_type: 小说类型
    :param complexity: 情节复杂度
    :param adapt_demand: 改编需求
    :return: 导演的智能体人格描述
    """
    if "宫崎骏" in director_name:
        prompt = f"""你现在是著名动画导演【宫崎骏】，请结合【{novel_type}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
        
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
    elif "王家卫" in director_name:
        prompt = f"""你现在是著名电影导演【王家卫】，请结合【{novel_type}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
        
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
    elif "诺兰" in director_name:
        prompt = f"""你现在是著名电影导演【诺兰】，请结合【{novel_type}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
        
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
    elif "新海诚" in director_name:
        prompt = f"""你现在是著名动画导演【新海诚】，请结合【{novel_type}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
        
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
    elif "今敏" in director_name:
        prompt = f"""你现在是已故传奇动画导演【今敏】，请结合【{novel_type}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
        
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
    elif "鸟山明" in director_name:
        prompt = f"""你现在是著名漫画家【鸟山明】，请结合【{novel_type}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
        
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
    elif "青山刚昌" in director_name:
        prompt = f"""你现在是著名漫画家【青山刚昌】，请结合【{novel_type}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
        
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
    elif "尾田荣一郎" in director_name:
        prompt = f"""你现在是著名漫画家【尾田荣一郎】，请结合【{novel_type}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
        
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
    elif "黑泽明" in director_name:
        prompt = f"""你现在是传奇电影导演【黑泽明】，请结合【{novel_type}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
        
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
    elif "原力动画团队" in director_name:
        prompt = f"""你现在是【原力动画团队】，请结合【{novel_type}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
        
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
    elif "铸梦动画团队" in director_name:
        prompt = f"""你现在是【铸梦动画团队】，请结合【{novel_type}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），发挥你的人格化特质，生成适配AI分镜的视觉+节奏指令：
        
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
        prompt = f"""作为资深漫画家和分镜师，请结合【{director_name}】的风格特点，针对【{novel_type}】题材（情节复杂度：{complexity}，改编需求：{adapt_demand}），生成适配AI分镜的视觉+节奏指令，严格按以下要求输出：
1.  分5点，每条用短横线开头，仅保留可落地的分镜执行细节；
2.  视觉维度：色调/光影/构图，绑定题材特质；
3.  动作处理：动作戏强化拆解逻辑；
4.  节奏把控：明确快剪/慢镜适用场景；
5.  细节偏好：针对题材专属元素的处理。

要求：内容贴合导演真实风格+题材需求，每条简洁精准。"""

    result = call_llm(prompt, temperature=0.6, is_comic_creation=True)
    if result:
        # 生成题材专属标签
        if "修仙" in novel_type or "稳健" in novel_type or "仙逆" in novel_type:
            if "原力动画团队" in director_name:
                style_tags = ["真人动捕细节", "UE5渲染质感", "细腻表情捕捉"]
            elif "铸梦动画团队" in director_name:
                style_tags = ["华丽特效渲染", "快节奏战斗", "宏大场景表现"]
            elif "鸟山明" in director_name:
                style_tags = ["动作设计简洁", "角色个性鲜明", "战斗节奏明快"]
            elif "尾田荣一郎" in director_name:
                style_tags = ["节奏把控精准", "世界观构建", "人物个性突出"]
            elif "今敏" in director_name:
                style_tags = ["现实梦境交织", "心理活动视觉化", "剪辑技巧独特"]
            else:
                style_tags = ["灵韵特效通透", "古风服饰纹理清晰", "斗法动作分层"]
        elif "科幻" in novel_type:
            if "诺兰" in director_name:
                style_tags = ["非线性叙事", "概念性主题", "实景拍摄"]
            elif "新海诚" in director_name:
                style_tags = ["画面美感", "青春主题", "光影表现力"]
            else:
                style_tags = ["机甲细节拉满", "星际场景纵深感", "科幻特效克制"]
        elif "悬疑" in novel_type:
            if "王家卫" in director_name:
                style_tags = ["氛围营造", "光影运用", "情感表达"]
            elif "青山刚昌" in director_name:
                style_tags = ["悬疑布局", "推理逻辑", "细节把控"]
            else:
                style_tags = ["阴影占比提升", "镜头留白营造悬念", "微表情特写"]
        else:
            if "宫崎骏" in director_name:
                style_tags = ["人文关怀", "情感细腻", "自然元素"]
            elif "新海诚" in director_name:
                style_tags = ["画面美感", "风景描写", "距离感表现"]
            else:
                style_tags = ["色调统一", "光影自然", "构图平衡"]
        
        st.session_state.director_style_tags = style_tags
        return result
    else:
        # 如果API调用失败，返回默认的风格
        st.session_state.director_style_tags = ["色调统一", "光影自然", "构图平衡"]
        return f"- 视觉风格：{novel_type}题材的经典视觉表现\n- 色彩运用：符合题材氛围的色调搭配\n- 构图设计：适合漫画阅读的构图方式\n- 节奏把控：根据情节复杂度调整的节奏变化\n- 细节处理：突出题材特色的细节表现"


def validate_storyboard_consistency(uploaded_image=None):
    """
    验证分镜一致性并提供建议
    :param uploaded_image: 参考图片
    :return: 验证结果和建议
    """
    if not st.session_state.storyboards:
        st.warning("⚠️ 请先生成分镜！")
        return False

    with st.spinner("🔍 校验分镜一致性..."):
        # 构建分镜内容字符串
        storyboards_content = ""
        for idx, sb in enumerate(st.session_state.storyboards):
            storyboards_content += f"镜头 {idx+1}: {sb.get('scene', '')}\n"
            storyboards_content += f"情绪: {sb.get('emotion', '')}\n"
            storyboards_content += f"镜头: {sb.get('camera', '')}\n"
            storyboards_content += f"人物特征: {sb.get('character_feature', '')}\n"
            storyboards_content += f"场景细节: {sb.get('environment', '')}\n\n"

        # 构造验证提示词
        validate_prompt = f"""请对以下分镜内容进行一致性校验，并提供优化建议：

分镜内容：
{storyboards_content}

请从以下几个方面进行校验：
1. 人物特征一致性：检查人物外观、服装、特征等是否在各镜头中保持一致
2. 空间关系一致性：检查场景布局、物体位置、空间逻辑是否连贯
3. 情绪和氛围一致性：检查情绪表达与故事节奏是否匹配
4. 镜头语言连贯性：检查镜头切换是否自然流畅

请按以下格式返回结果：
- 发现的问题：列出发现的不一致之处
- 优化建议：提供具体的修改建议
- 总体评价：对分镜整体质量的简要评价

请确保建议具有可操作性，并与原始小说内容保持一致。"""

        result = call_llm(validate_prompt, temperature=0.5, uploaded_image=uploaded_image, is_comic_creation=True)

        if result:
            st.session_state.validation_result = result

            # 解析建议并保存
            suggestions = []
            lines = result.split("\n")
            for line in lines:
                if line.strip().startswith("- ") and ("建议" in line or "优化" in line or "调整" in line or "统一" in line):
                    suggestions.append(line.strip()[2:])  # 去掉 "- " 前缀

            st.session_state.validation_suggestions = suggestions
            st.session_state.applied_validation = False

            st.success("✅ 分镜校验完成！")
            return True
        else:
            st.error("❌ 分镜校验失败！")
            return False


def apply_validation_suggestions():
    """
    应用验证建议优化所有分镜
    :return: 是否应用成功
    """
    if not st.session_state.validation_suggestions:
        st.warning("⚠️ 无验证建议可供应用！")
        return False

    if not st.session_state.storyboards:
        st.warning("⚠️ 无分镜数据！")
        return False

    with st.spinner("✨ 应用优化建议..."):
        # 获取原始分镜数据
        original_storyboards = st.session_state.storyboards.copy()

        try:
            # 使用验证建议和原始小说内容重新生成分镜
            novel_content = st.session_state.novel_target_chapter
            suggestions_text = "\n".join(st.session_state.validation_suggestions)

            refine_prompt = f"""请根据原始小说内容和验证建议，优化以下分镜：

原始小说内容：
{novel_content}

验证建议：
{suggestions_text}

请重新生成与原始分镜数量相同的优化后分镜，确保：
1. 保持原始故事内容和情节发展
2. 应用验证建议解决发现的问题
3. 保持分镜的连贯性和流畅性
4. 优化人物特征、空间关系、情绪表达的一致性

Please use与原始分镜相同的 format output。"""

            # 调用大模型重新生成优化后的分镜
            refined_result = call_llm(refine_prompt, temperature=0.6, is_comic_creation=True)

            if refined_result:
                # 解析优化后的分镜
                from core.generator import parse_storyboards_from_raw
                refined_storyboards = parse_storyboards_from_raw(
                    refined_result, 
                    core_elements=extract_novel_core_elements(novel_content)
                )

                # 如果解析成功，更新分镜数据
                if refined_storyboards and len(refined_storyboards) > 0:
                    st.session_state.storyboards = refined_storyboards
                    st.session_state.applied_validation = True
                    st.success("✅ 优化建议应用完成！")
                    return True
                else:
                    # 如果解析失败，回滚到原始数据
                    st.session_state.storyboards = original_storyboards
                    st.error("❌ 优化后分镜解析失败，已回滚到原始数据！")
                    return False
            else:
                st.session_state.storyboards = original_storyboards
                st.error("❌ 优化建议应用失败，已回滚到原始数据！")
                return False

        except Exception as e:
            st.session_state.storyboards = original_storyboards
            st.error(f"❌ 应用优化建议时发生错误：{str(e)}，已回滚到原始数据！")
            return False

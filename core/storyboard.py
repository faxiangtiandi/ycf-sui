import re
import json
import streamlit as st
from .llm import call_llm
from .utils import image_to_base64

def extract_novel_core_elements(novel_text, uploaded_image=None):
    """
    提取小说核心元素（人物/场景）
    :param novel_text: 小说文本
    :param uploaded_image: 参考图片
    :return: 核心元素字典
    """
    prompt = f"""分析以下小说文本，严格按JSON格式返回核心元素（无额外说明）：
{{
    "main_characters": [
        {{
            "name": "核心人物姓名",
            "gender": "性别（男/女/未知）",
            "age": "年龄范围（如：20岁左右/中年）",
            "appearance": "核心外貌特征（10字内）"
        }}
    ],
    "key_scenes": [
        {{
            "location": "场景地点（如：客厅/窗外）",
            "spatial_relations": "核心空间关系（如：人物在室内，物体在窗外）"
        }}
    ]
}}

小说文本：
{novel_text[:2000]}"""
    
    result = call_llm(prompt, temperature=0.1, uploaded_image=uploaded_image)
    if not result:
        return {
            "main_characters": [{"name": "主角", "gender": "未知", "age": "成年", "appearance": "普通外貌"}],
            "key_scenes": [{"location": "室内", "spatial_relations": "人物在室内"}]
        }
    
    try:
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            core_elements = json.loads(json_match.group())
            st.session_state.novel_core_characters = core_elements.get("main_characters", [])
            st.session_state.novel_core_scenes = core_elements.get("key_scenes", [])
            return core_elements
    except:
        pass
    
    return {
        "main_characters": [{"name": "主角", "gender": "未知", "age": "成年", "appearance": "普通外貌"}],
        "key_scenes": [{"location": "室内", "spatial_relations": "人物在室内"}]
    }

def validate_storyboard_consistency(uploaded_image=None):
    """
    校验分镜一致性并生成优化建议
    :param uploaded_image: 参考图片
    :return: 是否校验成功
    """
    if not st.session_state.storyboards:
        st.warning("⚠️ 请先生成分镜再进行校验！")
        return False
    
    with st.spinner("🔍 校验分镜一致性并生成优化建议..."):
        # 提取分镜特征
        all_characters = [sb['character_feature'] for sb in st.session_state.storyboards if sb['has_character'] == "是"]
        all_scenes = [sb['environment'] for sb in st.session_state.storyboards]
        
        prompt = f"""分析以下分镜内容的一致性问题，生成具体优化建议：
1. 人物特征一致性：检查所有镜头中核心人物的姓名、性别、年龄、外貌是否统一
2. 空间关系一致性：检查场景空间关系是否合理、统一
3. 视觉风格一致性：检查色调、光影、构图是否符合导演风格

分镜人物特征：
{json.dumps(all_characters, ensure_ascii=False)}

分镜场景信息：
{json.dumps(all_scenes, ensure_ascii=False)}

导演风格：
{st.session_state.director_persona}

要求：
1. 先列出发现的问题（如有）
2. 生成可直接应用的优化建议（每条建议简洁可落地）
3. 格式：问题列表+建议列表，用短横线开头
"""
        result = call_llm(prompt, temperature=0.3, uploaded_image=uploaded_image)
        
        if result:
            st.session_state.validation_result = result
            # 解析建议列表
            suggestions = []
            lines = result.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("-") and ("建议" in line or "优化" in line or "统一" in line):
                    suggestions.append(line[1:].strip())
            st.session_state.validation_suggestions = suggestions
            st.success("✅ 分镜一致性校验完成！")
            return True
        else:
            st.error("❌ 校验失败，请重试！")
            return False

def apply_validation_suggestions():
    """一键应用校验建议到所有分镜提示词"""
    if not st.session_state.validation_suggestions:
        st.warning("⚠️ 暂无可用的优化建议！")
        return False
    
    with st.spinner("✨ 一键应用优化建议到所有提示词..."):
        # 合并建议
        suggestions = "，".join(st.session_state.validation_suggestions)
        
        # 更新所有分镜
        updated_storyboards = []
        for sb in st.session_state.storyboards:
            sb['optimized_prompt'] = f"{sb['optimized_prompt']}，{suggestions}"
            updated_storyboards.append(sb)
        
        st.session_state.storyboards = updated_storyboards
        st.session_state.optimized_prompts = [sb['optimized_prompt'] for sb in updated_storyboards]
        st.session_state.applied_validation = True
        st.success("✅ 优化建议已一键应用！")
        return True

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
        # 提取小说核心元素
        core_elements = extract_novel_core_elements(st.session_state.novel_target_chapter, uploaded_image)
        
        # 分析小说类型和复杂度
        type_prompt = f"分析以下文本的类型，仅返回类型名称：\n{st.session_state.novel_target_chapter[:2000]}"
        st.session_state.novel_type = call_llm(type_prompt, uploaded_image=uploaded_image) or "未知类型"
        
        complexity_prompt = f"""分析以下文本的情节复杂度，仅返回结果（动作/特效密集型、对话/心理型、均衡型）：
文本：{st.session_state.novel_target_chapter[:2000]}"""
        complexity = call_llm(complexity_prompt, temperature=0.3, uploaded_image=uploaded_image) or "均衡型"
        st.session_state.complexity = complexity
        
        # 检查停止标志
        if st.session_state.stop_flag:
            st.warning("⚠️ 生成已手动停止！")
            st.session_state.is_running = False
            return False
        
        # 构建视觉风格指令
        director_style = st.session_state.director_persona or "冷青灰高对比色调，阴影厚重占比60%，构图紧凑留白少"
        style_tags = st.session_state.director_style_tags or []
        visual_style = f"{director_style}，{','.join(style_tags)}，贴合{st.session_state.novel_type}题材"
        
        # 分镜密度规则
        if complexity == "动作/特效密集型":
            density_rule = "分镜密度偏高，每40-60字对应1个镜头"
        elif complexity == "对话/心理型":
            density_rule = "分镜密度适中偏低，每70-90字对应1个镜头"
        else:
            density_rule = "分镜密度均衡，每50-80字对应1个镜头"
        
        # 题材专属规则
        if "修仙" in st.session_state.novel_type or "古风" in st.session_state.novel_type:
            genre_specific = "适配修仙/古风：动作拆分为起手→释放→收尾，场景强化古风细节"
        elif "科幻" in st.session_state.novel_type:
            genre_specific = "适配科幻：机械动作拆分为启动→运行→停止，场景强化科技感"
        elif "悬疑" in st.session_state.novel_type:
            genre_specific = "适配悬疑：视觉节点拆分为铺垫→转折→爆发，场景强化空间层次感"
        else:
            genre_specific = "适配通用题材：视觉节点拆分为起承转合，保持自然的空间关系"
        
        # 导演节奏风格
        director_rhythm = "动作戏快剪，情绪戏慢镜"
        if st.session_state.director_persona:
            persona_lines = [line.strip() for line in st.session_state.director_persona.split("-") if line.strip()]
            if len(persona_lines) >=4:
                director_rhythm = persona_lines[3].strip()
        
        # 构建最终分镜提示词
        final_prompt = f"""你是资深动态漫分镜师，需严格遵循【{st.session_state.selected_director or '适配型分镜师'}】的创作逻辑（视觉风格：{visual_style}），为小说生成结构化分镜：

【核心规则1：分镜密度】
1.  {density_rule}，总镜头数符合2分钟动态漫节奏（单章1500-2500字对应45-65个镜头）；
2.  视觉节点必拆：表情微变、动作衔接、场景切换、道具细节、特效爆发；
3.  {genre_specific}。

【核心规则2：人物/空间约束（必须严格遵守）】
1.  核心人物特征保持一致：姓名、性别、年龄、外貌特征在所有镜头中统一；
2.  空间关系清晰：明确区分室内/室外、前景/背景、近/远等空间层次；
3.  悬浮/外部物体：必须远离主体至少5米，不得与主体/玻璃/墙面融合；
4.  避免人物混淆：不同角色的特征差异明显，不得出现性别/年龄错乱。

【核心规则3：格式要求】
每个镜头按以下模板输出，镜头序号从1开始，前缀标注“镜头X：[核心情节，8字内]”，镜头间用“===== 分割线：下一个镜头 =====”分隔：
镜头X：[核心情节]
【中文结构化提示词（文生图专用）】
风格描述：{st.session_state.novel_type}题材，{visual_style}，贴合小说情绪
镜头方向：[景别+拍摄角度]
艺术风格：[色调+构图+氛围]
画质要求：8K超高清，电影级质感，[细节要求]
人物特征：[固定形象+当前动作/表情]
场景细节：[完整布局+道具细节+清晰的空间关系]
【英文结构化提示词（文生图专用）】
Style Description: {st.session_state.novel_type} theme, {visual_style.replace("，", ", ")}, fits the novel's mood
Camera Direction: [Shot type + angle]
Art Style: [Color + composition + atmosphere]
Quality Requirements: 8K ultra HD, cinematic texture, [English detail]
Character Features: [Fixed image + current action/expression]
Scene Details: [Full layout + prop details + clear spatial relationships]
【图生视频专用提示词】
Video Prompt: [文生图英文提示词] + , 1-2s duration per shot, 24fps, natural motion, [运镜描述]

【当前小说原文】
{st.session_state.novel_target_chapter}

【输出示例（通用）】
镜头1：主角站立窗前
【中文结构化提示词（文生图专用）】
风格描述：悬疑题材，冷青灰高对比色调，阴影厚重占比60%，贴合悬疑氛围
镜头方向：近景，平视角度
艺术风格：冷青色调，构图紧凑，紧张氛围
画质要求：8K超高清，电影级质感，皮肤纹理可见，暗部细节清晰
人物特征：20岁女性主角，黑色长发，休闲家居服，侧身站立，眼神警惕
场景细节：客厅窗边，室内昏暗，窗外5米处悬浮模糊人影，空间层次清晰
【英文结构化提示词（文生图专用）】
Style Description: Suspense theme, cool blue-gray high contrast tones, heavy shadows accounting for 60%, fits suspense atmosphere
Camera Direction: Medium shot, eye-level angle
Art Style: Cool cyan tones, tight composition, tense atmosphere
Quality Requirements: 8K ultra HD, cinematic texture, visible skin texture, clear dark details
Character Features: 20-year-old female protagonist, long black hair, casual home wear, standing sideways, alert eyes
Scene Details: Living room by window, dim indoor lighting, blurry figure floating 5 meters outside the window, clear spatial hierarchy
【图生视频专用提示词】
Video Prompt: Style Description: Suspense theme, cool blue-gray high contrast tones, heavy shadows accounting for 60%, fits suspense atmosphere; Camera Direction: Medium shot, eye-level angle; Art Style: Cool cyan tones, tight composition, tense atmosphere; Quality Requirements: 8K ultra HD, cinematic texture, visible skin texture, clear dark details; Character Features: 20-year-old female protagonist, long black hair, casual home wear, standing sideways, alert eyes; Scene Details: Living room by window, dim indoor lighting, blurry figure floating 5 meters outside the window, clear spatial hierarchy, 1.5s duration per shot, 24fps, natural motion, smooth pan from hand to face
===== 分割线：下一个镜头 =====
"""
        
        # 调用LLM生成原始分镜
        raw_response = call_llm(final_prompt, temperature=0.4, uploaded_image=uploaded_image)
        
        if not raw_response or st.session_state.stop_flag:
            if not st.session_state.stop_flag:
                st.warning("⚠️ 分镜生成失败！")
            st.session_state.is_running = False
            return False
        
        # 解析原始分镜
        raw_clean = raw_response.strip()
        storyboard_parts = [part.strip() for part in raw_clean.split("===== 分割线：下一个镜头 =====") if part.strip()]
        
        try:
            storyboards = []
            comfy_prompts = []
            video_prompts = []
            optimized_prompts = []
            negative_prompts = []
            
            # 导入coregenerator的核心函数（生成通用提示词）
            from core.coregenerator import generate_universal_image_prompt, optimize_prompt_for_ai
            
            for idx, part in enumerate(storyboard_parts):
                # 过滤无效分镜
                if not ("【中文结构化提示词（文生图专用）】" in part and "【英文结构化提示词（文生图专用）】" in part and "【图生视频专用提示词】" in part):
                    continue
                
                # 解析镜头前缀
                scene_prefix_lines = [line.strip() for line in part.split("\n") if line.strip().startswith("镜头")]
                if not scene_prefix_lines:
                    continue
                scene_prefix = scene_prefix_lines[0]
                if "：" not in scene_prefix:
                    continue
                scene_num = scene_prefix.split("：")[0]
                scene_core = scene_prefix.split("：")[1]
                
                # 解析中文提示词
                cn_part = part.split("【中文结构化提示词（文生图专用）】")[1].split("【英文结构化提示词（文生图专用）】")[0].strip()
                style_desc_cn = ""
                camera_cn = ""
                art_style_cn = ""
                quality_cn = ""
                character_cn = ""
                scene_cn = ""
                
                for line in cn_part.split("\n"):
                    line = line.strip()
                    if line.startswith("风格描述："):
                        style_desc_cn = line.replace("风格描述：", "")
                    elif line.startswith("镜头方向："):
                        camera_cn = line.replace("镜头方向：", "")
                    elif line.startswith("艺术风格："):
                        art_style_cn = line.replace("艺术风格：", "")
                    elif line.startswith("画质要求："):
                        quality_cn = line.replace("画质要求：", "")
                    elif line.startswith("人物特征："):
                        character_cn = line.replace("人物特征：", "")
                    elif line.startswith("场景细节："):
                        scene_cn = line.replace("场景细节：", "")
                
                # 解析英文和视频提示词
                en_part = part.split("【英文结构化提示词（文生图专用）】")[1].split("【图生视频专用提示词】")[0].strip()
                video_part = part.split("【图生视频专用提示词】")[1].strip()
                
                # 解析情绪标签
                emotion = "平静"
                if "疑惑" in character_cn or "好奇" in style_desc_cn:
                    emotion = "疑惑"
                elif "惊恐" in character_cn or "惊悚" in style_desc_cn:
                    emotion = "惊恐"
                elif "无助" in character_cn or "绝望" in style_desc_cn:
                    emotion = "无助"
                elif "悲伤" in character_cn:
                    emotion = "悲伤"
                elif "喜悦" in character_cn:
                    emotion = "喜悦"
                
                # 生成通用提示词
                scene_info = {
                    "scene_core": scene_core,
                    "emotion": emotion,
                    "camera": camera_cn,
                    "atmosphere": art_style_cn,
                    "character_feature": character_cn,
                    "environment": scene_cn,
                    "visual_style": visual_style
                }
                universal_prompt = generate_universal_image_prompt(scene_info, core_elements)
                
                # 组装分镜数据
                storyboard = {
                    "scene": f"{scene_prefix}\n{cn_part}",
                    "emotion": emotion,
                    "camera": camera_cn if camera_cn else "中景，平视角度",
                    "atmosphere": art_style_cn if art_style_cn else "贴合题材氛围",
                    "has_character": "是" if character_cn and character_cn != "无" else "否",
                    "character_feature": character_cn if character_cn else "贴合题材人物特征",
                    "environment": scene_cn if scene_cn else "贴合题材场景细节",
                    "comfyui_prompt": en_part,
                    "video_prompt": video_part,
                    "optimized_prompt": universal_prompt["positive"],
                    "negative_prompt": universal_prompt["negative"]
                }
                storyboards.append(storyboard)
                comfy_prompts.append(en_part)
                video_prompts.append(video_part)
                optimized_prompts.append(universal_prompt["positive"])
                negative_prompts.append(universal_prompt["negative"])
            
            # 保存分镜数据
            if len(storyboards) == 0:
                st.error("❌ 未解析到有效分镜！")
            else:
                st.success(f"✅ 分镜生成成功！共{len(storyboards)}个镜头")
            
            st.session_state.storyboards = storyboards
            st.session_state.comfyui_prompts = comfy_prompts
            st.session_state.video_prompts = video_prompts
            st.session_state.optimized_prompts = optimized_prompts
            st.session_state.negative_prompt = negative_prompts[0] if negative_prompts else ""
            
            st.session_state.is_running = False
            return True
        except Exception as e:
            st.error(f"❌ 分镜解析失败！错误：{str(e)}")
            st.session_state.is_running = False
            return False
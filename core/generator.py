# core/generator.py
# 纯函数实现：生成提示词 / 优化提示 / 分镜解析（不依赖 Streamlit）
import re
import json

def generate_universal_image_prompt(scene_info, core_elements, novel_type=None, director_style=None):
    """
    生成通用图像提示词（正向 + 负向）。
    """
    main_char = core_elements.get("main_characters", [{}])[0] if core_elements else {}
    char_name = main_char.get("name", "主角")
    char_gender = main_char.get("gender", "未知")
    char_age = main_char.get("age", "成年")
    char_appearance = main_char.get("appearance", "普通外貌")
    spatial_relation = (core_elements.get("key_scenes") or [{}])[0].get("spatial_relations", "人物在室内")

    visual_style = scene_info.get("visual_style", director_style or "")
    emotion = scene_info.get("emotion", "平静")
    camera = scene_info.get("camera", "中景，平视角度")
    atmosphere = scene_info.get("atmosphere", "贴合题材氛围")
    character = scene_info.get("character_feature", "")
    environment = scene_info.get("environment", "")

    positive_prompt = (
        f"{novel_type or ''}题材，{visual_style}，{emotion}氛围 "
        f"镜头设置：{camera} "
        f"艺术风格：{atmosphere} "
        f"核心人物：{char_name}，{char_gender}，{char_age}，{char_appearance}，{character} "
        f"场景细节：{environment}，{spatial_relation} "
        "画质要求：8K超高清，电影级质感，自然光线过渡，清晰的暗部细节，主体特征清晰可辨"
    )
    negative_prompt = (
        "不要生成与核心人物性别/年龄不符的形象，"
        "不要混淆室内/室外空间关系，"
        "不要生成模糊的主体特征，"
        "不要生成错误的人物面部特征，"
        "不要生成不符合物理规律的空间比例"
    )
    positive_prompt = re.sub(r'\s+', ' ', positive_prompt).strip()
    negative_prompt = re.sub(r'\s+', ' ', negative_prompt).strip()
    return {"positive": positive_prompt, "negative": negative_prompt}

def optimize_prompt_for_ai(raw_prompt, negative_prompt=""):
    """
    将结构化中文提示优化为一行 AI 正向提示（启发式）。
    """
    parts = [p.strip() for p in raw_prompt.split("\n\n") if p.strip()]
    style_desc = ""
    camera_dir = ""
    art_style = ""
    quality = ""
    character = ""
    scene = ""

    for part in parts:
        if part.startswith("风格描述："):
            style_desc = part.replace("风格描述：", "").strip()
        elif part.startswith("镜头方向："):
            camera_dir = part.replace("镜头方向：", "").strip()
        elif part.startswith("艺术风格："):
            art_style = part.replace("艺术风格：", "").strip()
        elif part.startswith("画质要求："):
            quality = part.replace("画质要求：", "").strip()
        elif part.startswith("人物特征："):
            character = part.replace("人物特征：", "").strip()
        elif part.startswith("场景细节："):
            scene = part.replace("场景细节：", "").strip()

    optimized = ", ".join([q for q in [quality, character, scene, art_style, camera_dir, style_desc] if q])
    optimized = re.sub(r'\s+', ' ', optimized).strip()
    return {"positive": optimized, "negative": negative_prompt or ""}

def parse_storyboards_from_raw(raw_response, core_elements=None, novel_type=None, director_style=None):
    """
    从 LLM 原始文本解析出多个结构化分镜条目（简单启发式解析）。
    """
    if not raw_response or not isinstance(raw_response, str):
        return []

    parts = [p.strip() for p in raw_response.split("===== 分割线：下一个镜头 =====") if p.strip()]
    storyboards = []
    for part in parts:
        m = re.search(r'^(镜头\d+：\s*([^\n]+))', part)
        scene_title = m.group(1) if m else ""
        scene_core = m.group(2) if m else ""

        cn_block = ""
        en_block = ""
        video_block = ""
        if "【中文结构化提示词（文生图专用）】" in part:
            try:
                cn_block = part.split("【中文结构化提示词（文生图专用）】")[1].split("【英文结构化提示词（文生图专用）】")[0].strip()
            except Exception:
                cn_block = ""
        if "【英文结构化提示词（文生图专用）】" in part:
            try:
                en_block = part.split("【英文结构化提示词（文生图专用）】")[1].split("【图生视频专用提示词】")[0].strip()
            except Exception:
                en_block = ""
        if "【图生视频专用提示词】" in part:
            try:
                video_block = part.split("【图生视频专用提示词】")[1].strip()
            except Exception:
                video_block = ""

        def extract_cn_field(block, prefix):
            for line in block.split("\n"):
                line = line.strip()
                if line.startswith(prefix):
                    return line.replace(prefix, "").strip()
            return ""

        style_desc_cn = extract_cn_field(cn_block, "风格描述：")
        camera_cn = extract_cn_field(cn_block, "镜头方向：")
        art_style_cn = extract_cn_field(cn_block, "艺术风格：")
        quality_cn = extract_cn_field(cn_block, "画质要求：")
        character_cn = extract_cn_field(cn_block, "人物特征：")
        scene_cn = extract_cn_field(cn_block, "场景细节：")

        emotion = "平静"
        if "疑惑" in character_cn or "好奇" in style_desc_cn:
            emotion = "疑惑"
        elif "惊恐" in character_cn or "惊悚" in style_desc_cn:
            emotion = "惊恐"
        elif "悲伤" in character_cn:
            emotion = "悲伤"
        elif "喜悦" in character_cn:
            emotion = "喜悦"

        sb = {
            "scene": scene_title + ("\n" + cn_block if cn_block else ""),
            "scene_core": scene_core,
            "emotion": emotion,
            "camera": camera_cn or "中景，平视角度",
            "atmosphere": art_style_cn or (director_style or "贴合题材氛围"),
            "has_character": "是" if character_cn and character_cn != "无" else "否",
            "character_feature": character_cn or "贴合题材人物特征",
            "environment": scene_cn or "贴合题材场景细节",
            "comfyui_prompt": en_block,
            "video_prompt": video_block,
            "optimized_prompt": generate_universal_image_prompt(
                {
                    "scene_core": scene_core,
                    "emotion": emotion,
                    "camera": camera_cn,
                    "atmosphere": art_style_cn,
                    "character_feature": character_cn,
                    "environment": scene_cn,
                    "visual_style": director_style or novel_type or ""
                },
                core_elements or {}
            )["positive"],
            "negative_prompt": generate_universal_image_prompt({}, core_elements or {})["negative"]
        }
        storyboards.append(sb)
    return storyboards

import pytest
from core.generator import generate_universal_image_prompt, optimize_prompt_for_ai, parse_storyboards_from_raw

def test_generate_universal_image_prompt_basic():
    scene_info = {
        "scene_core": "主角站窗前",
        "emotion": "紧张",
        "camera": "中景",
        "atmosphere": "冷色调",
        "character_feature": "20岁女性主角",
        "environment": "客厅窗前",
        "visual_style": "悬疑风"
    }
    core_elements = {
        "main_characters": [{"name": "主角", "gender": "女", "age": "20岁", "appearance": "黑长发"}],
        "key_scenes": [{"location": "客厅", "spatial_relations": "人物在窗前"}]
    }
    res = generate_universal_image_prompt(scene_info, core_elements, novel_type="悬疑")
    assert "悬疑" in res["positive"]
    assert "不要生成" in res["negative"]

def test_optimize_prompt_for_ai_basic():
    raw = (
        "风格描述：冷青灰高对比色调\n\n"
        "镜头方向：近景，平视角度\n\n"
        "艺术风格：紧张氛围，构图紧凑\n\n"
        "画质要求：8K超高清\n\n"
        "人物特征：20岁女性，黑长发\n\n"
        "场景细节：客厅窗边，昏暗"
    )
    out = optimize_prompt_for_ai(raw, negative_prompt="no_blur")
    assert "8K超高清" in out["positive"]
    assert out["negative"] == "no_blur"

def test_parse_storyboards_from_raw_sample():
    raw = (
        "镜头1：主角站立窗前\n"
        "【中文结构化提示词（文生图专用）】\n"
        "风格描述：悬疑题材，冷青灰高对比色调\n"
        "镜头方向：近景，平视角度\n"
        "艺术风格：冷青色调，构图紧凑\n"
        "画质要求：8K超高清\n"
        "人物特征：20岁女性主角，黑长发，侧身\n"
        "场景细节：客厅窗边，室内昏暗，窗外5米处有模糊人影\n"
        "【英文结构化提示词（文生图专用）】\n"
        "Style Description: Suspense theme ...\n"
        "【图生视频专用提示词】\n"
        "Video Prompt: Style Description: Suspense ... , 1.5s duration per shot\n"
        "===== 分割线：下一个镜头 =====\n"
    )
    sbs = parse_storyboards_from_raw(raw, core_elements={"main_characters":[{"name":"主角"}]})
    assert isinstance(sbs, list)
    assert len(sbs) >= 1
    assert "主角" in sbs[0]["scene"]

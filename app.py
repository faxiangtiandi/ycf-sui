import streamlit as st

# 一键导入所有核心模块函数
from core import (
    call_llm, check_config_valid, get_valid_config,
    ai_recommend_director, generate_director_persona,
    generate_storyboards, extract_novel_core_elements, validate_storyboard_consistency, apply_validation_suggestions,
    image_to_base64, API_PRESETS,
    copy_to_clipboard_button, init_basic_config, init_session_state
)

# ========== 核心修复：提前初始化所有必要的session_state变量 ==========
def ensure_session_state_initialized():
    """确保所有必要的session_state变量都已初始化"""
    default_states = {
        # 运行状态控制
        "is_running": False,
        "stop_flag": False,
        # 导演相关
        "director_recommend_list": [],
        "selected_director": "",
        "director_persona": "",
        "director_style_tags": [],
        "director_radio": "",
        "custom_director_name": "",
        # 分镜相关
        "storyboards": [],
        "validation_result": "",
        "validation_suggestions": [],
        # API模式选择
        "selected_mode": "text_mode",
        "api_mode_selector": "文本模式",
        # 小说信息
        "novel_title": "三体·黑暗森林",  # 测试默认值
        "novel_author": "刘慈欣",  # 测试默认值
        "novel_background": "在《三体》系列的第二部中，人类文明面临着三体世界的威胁，黑暗森林法则成为宇宙文明生存的基本法则。",  # 测试默认值
        "novel_target_chapter": "叶文洁站在控制室里，面对着巨大的显示屏。屏幕上显示着遥远星系的图像，她知道那里可能存在着另一个文明。在她身后，几名技术人员忙碌地操作着设备，监测着从太空传来的信号。突然，一个清晰的信号打破了寂静，这个信号似乎携带着某种规律性的信息。",  # 测试默认值
        # 其他状态
        "expanded_prompt_idx": -1,
        "generate_mode": "手动模式",
        "novel_core_characters": [],
        "novel_core_scenes": [],
        "applied_validation": False,
        "comfyui_prompts": [],
        "optimized_prompts": [],
        "negative_prompt": "",
        "video_prompts": [],
        "novel_type": "",
        "novel_trait": "",
        "adapt_demand": "",
        "complexity": "",  # 确保这个变量被初始化
        "comfyui_prompt": "",
        "video_prompt": "",
        "optimized_prompt": "",
        "scene": "",
        "emotion": "",
        "camera": "",
        "atmosphere": "",
        "has_character": "",
        "character_feature": "",
        "environment": ""
    }
    
    # 设置默认API配置用于测试（保持不变）
    if "text_mode_api_key" not in st.session_state:
        st.session_state.text_mode_api_key = "sk-a314b066906c4221b6f6ff48fca4ff74"  # 测试用API Key
    
    if "text_mode_base_url" not in st.session_state:
        st.session_state.text_mode_base_url = "https://api.deepseek.com/v1/chat/completions"
    
    if "text_mode_model" not in st.session_state:
        st.session_state.text_mode_model = "deepseek-chat"
    
    # 更新小说信息的默认值（仅在首次初始化时设置）
    if "novel_title" not in st.session_state:
        st.session_state.novel_title = "神秘复苏"
    if "novel_author" not in st.session_state:
        st.session_state.novel_author = "佛前献花"
    if "novel_background" not in st.session_state:
        st.session_state.novel_background = """大澳市。
繁华的都市被黑夜笼罩，喧闹的城市渐渐回归宁静。
马路上车辆减少，大楼内灯光陆陆续续的熄灭，时间仿佛是一只无形的大手，有规律的操控着所有的切。
午夜，十二点。
一户居民楼的窗户亮着明亮的灯光，一位名叫秦瑶的十八岁少女此刻趴在被窝里精神亢奋的玩着手机，和网友聊着天，讨论着最近热门的一个话题。
喂，最近的报纸你看了么?简直太离谱了，居然说这个世界上有鬼诶。”
我看到了那份报纸，现在好多人都在议论这件事情，我也觉得很离谱，这天底下哪有什么鬼，都是人心在作祟罢了，肯定是炒作，想要引起恐慌，然后达成什么不可告人的目的。”
我爸妈真是离谱，居然还在家里立了一个神位，现在我每次回家都感觉家里阴森森的，我都不想待了。
“......”
就在这个时候，秦瑶的房间外传来了父亲的叮嘱声:“说了多少次了，晚上睡觉要把灯给关了。”
爸，可是晚上关灯玩手机伤眼睛诶，再说了开灯睡觉不是很好么这样房间里就比较明亮，到时候起床上厕所的时候就不会和上次一样撞到头了。”秦瑶反驳道。
“就你聪明，晚上睡觉不关灯犯忌讳懂不懂?你晚上开着灯房间里这么亮，其他人都关着灯，到时候外面有什么东西一眼就看到我们家了，要是那些东西没地方去，来我们家坐坐，到时候看你怎么办。”外面父亲的声音再次响起。
外面能有什么?我们住在二十八楼。”秦瑶不服气道。
外面父亲说道:"这是你爷爷传下来的规矩，他说，大楼就像是一根蜡烛，房间里亮着灯就等于把蜡烛点燃了，一些游荡在城市里不干净的东西就会被吸引过来，所以晚上睡觉的时候一定要把灯熄灭，尤其是你这房间，窗户朝南，灯一开，外面什么东西都能看见，所以赶紧关灯睡觉，别让我孫再叫你了，我明天还要上班呢。”
行了，行了，别神神叨叨的了，我把灯关上行了吧。”秦瑶没办法，只得将房间里的灯熄灭
然而就在她把灯熄灭的一瞬间。
砰!
窗外的玻璃突然传来一声轻微的拍击声，这让秦瑶吓了一跳。
她看向了声音传来的方向，却见窗外什么都没有，远处只有城市的灯光映照进了房间里。
是不是鸟撞上玻璃了?
秦瑶这样猜测着，随后有些好奇的凑到窗旁看了看。
等靠近之后，秦瑶这才看见，在玻璃上烙印着一张脸的轮廓，那人脸印的很清晰，可以明显的分辨出来那是一个老人的形象，此刻闭着眼睛，周围满是苍老的皱纹，神态十分安详，仿佛刚刚去世不久一般。
秦瑶伸手去擦，想要抹掉这个图案，但是很快她却手僵在了玻璃上犹如触电一般迅速的收了回来。
人脸的图案并不在朝房间的这面玻璃上，而是在外面。
“怎么会，这里可是二十八楼而且以前玻璃上绝对没有。”
秦瑶心头有些不安起来，她从小就坐在这窗边写作业，练习钢琴，背功课，窗外不知道看了多少遍。
她心中十分确认，以前窗户外是十分干净的，不会留下这样一个人脸印记。
爸，你过来看看，窗户上那是什么..
秦瑶有些心慌了，她缓缓后退远离那窗户，然后喊了一声。
但是房间外一片寂静，一点声音都没有。
秦瑶再次喊了几声，外面的父亲依旧没有回应，周围更是出奇的安静，，她感觉自己就像是被隔绝了一样，有一种被孤立，遗落的恐惧感。
窗外。
随着远处的一道灯光晃过，那映照在上面的人脸轮廓愈发的清晰了而且伴随着那道灯光在远处缓缓移动，不知道是不是光线带来的错觉秦瑶隐约觉得那张人脸好像在变得凶狠了起来，之前的安详已经荡然无存了。
“爸，爸，你快过来。”秦瑶的声音带着哭腔，
她被惊吓了，转身就想去开灯，也许开灯之后房间明亮起来，这些怪异的东西就会消失。
但是当她按动开关的时候却发现昏暗的房间依旧，卧房里的灯像是损坏掉了一样，没有任何点亮的迹象。
这下秦瑶更惊恐了
她脆弱的心理防线被彻底压垮一边喊着爸爸，一边逃似的离开自己的卧房，想要寻求家人的庇护。
那平日里轻易就可以打开的房门，这个时候不知道怎么回事，像是被一股力量吸住了一样，不管她怎么推拉都没有办法打开。
秦瑶的手在颤抖，整个人用力的拉扯着门把手。
也许是太过惊慌的原故，门被稍微带上了一点保险，所以才没有被打开，亦或者真的有一股莫名的未知力量影响着这一切。
就在秦瑶心中的恐惧达到顶端的时候。
忽的。
“砰!”
房门打开了，外面一股阴冷的空气吹了进来，空气中夹带着一股若有若无的尸臭味。
秦瑶根本就没有去关注这一些细节，急忙冲出了房间，然后喊着爸爸的同时，朝着父母的卧室方向冲去。
家里的结构她十分了解，即便是客厅没有开灯，同样昏暗，但是她依旧可以精准的找到房间......只是秦瑶往前冲了没多远，她猛地停住了脚步。
眼前并不是父母的房间，而是一面老旧的墙壁。
墙壁上阴暗潮湿，布满青色青苔。
等等，这里是哪里?
秦瑶这个时候才反应过来，她带着惊恐的目光开始环顾四周，这里根本就不是她的家，而是一处陌生，老旧的房子里，这间房子像是封存了许久，没有任何居住的痕迹。
但是最让人惊悚的是，在这房间的中间，居然摆放着一张木床，床上躺着一个人，不，准确的说是一具尸体。
那具尸体穿着黑色的布鞋，青色的寿衣，脸上画着惨白的妆容，双手交叉放在身前，神态安详，一动不动。
而且最让人恐惧的是，这尸体的长相和烙印在窗外的那张老人脸庞一模一样。
秦瑶仅仅只是看了一眼，吓的尖叫一声，瞬间僵在了原地，她浑身像是失去了知觉一样，无法再动弹了，虽然她极力的想要逃离这个地方，返回自己的房间里去，但眼睛却始终无法挪动分毫，目光一直停留在客厅中间的那具老尸身上。
这个时候。
秦瑶脑海里不知道怎么回事浮现出了自己父亲之前的话。
晚上睡觉的时候一定要关灯，否则会引来一些不干净的东西进来家里坐坐。
这就是那不干净的东西?
一具死去许久，却又不腐烂的尸体?
秦瑶感觉自己心跳的好快，极度恐惧之下，她好似要窒息了，有一种呼吸都消失了的感觉。
而且她的目光像是被什么东西给牢牢控制住了一样，不管眼睛怎么移动，视线一直在眼前这具满是皱纹的惨白老尸身上。
那死气沉沉的诡异模样，此刻深深的烙印在了她的脑海之中。
就在她以为自己就会这样窒息死去的时候。
忽的。
在秦瑶的身后，一只白皙且又冰冷的手掌拉住了她。
而她的身躯却又不受控制的缓缓往后退去。
一步，一步。
谁，谁在身后拉着我?
秦瑶心脏猛地一缩，她僵直的身体依旧无法动弹，连回头张望都做不到，但是从手掌上传来的触感可以判断，那应该是一个女人的手掌，虽然冰冷没有温度，但却十分细腻光滑
嗤嗤!当她被拉进房间里之后，房间里的灯光突然闪烁了起来。
同时那被打开的房门也在骤然之间砰地一声关上了。
客厅里躺着的那具可怕尸体被大门阻挡，消失在了视线之中。
秦瑶感觉自己的视线总算是可以挪动了，她下意识的就想转动脖子回头看去。
看看自己的身后到底有什么，是谁在拉着自己。
别回头，晚上睡觉，记得关灯。”一个冷漠悦耳的女子声音从她的身后响起。
而随着话音落下。
房间里的灯光不再闪烁，而是突然亮了起来。
秦瑶几乎本能的朝着身后看去什么都没有，只是半空之中漂浮着一些灰蒙蒙的东西，像是纸燃烧过后留下的灰烬，不过很快这些灰烬却又消失了。
心中的恐惧依旧强烈。秦瑶再次朝着那窗户处看去
原本烙印在玻璃外的那张诡异人脸此刻却不知道什么时候已经消失不见了，似乎刚才发生的一切都是幻觉。
嘎吱!
这个时候房门打开了。
秦瑶吓的浑身一颤，身体瞬间就绷直了，
“都说了多少遍了，赶紧关灯睡觉，别让我发脾气。”一位穿着睡衣的中年女子此刻带着几分怒意说道。
房间外，客厅一切正常，灯光亮起。
之前那老旧的墙壁，诡异的尸体已经消失不见了。
似乎刚才经历的一切都是幻觉
秦瑶此刻哇的一声哭了出来，扑进了自己母亲的怀里，浑身都在颤抖着
与此同时。
大澳市远处的一座老旧的大楼楼顶，一位诡异的女子矗立在那一动不动，那女子身穿一件不符合这个年代的红色嫁衣，鲜艳如血，头上盖着红色的头盖，看不清楚样子，只有一双白皙细腻的双手露在外面。
在这女子的周围，天空上飘落着灰蒙蒙的灰烬，这些灰烬随风飞舞，落入大澳市的每一个角落。
这女子不知道站立了多长时间。
等黑夜消失，太阳刚刚升起的时候，第一缕阳光照到她身上的时候她的身形渐渐变淡，正在消失。
忽的。
就在此刻。
阳光之中出现了一道声音，对着这个诡异女子发出了一个询问。
“何月莲，一加一等于几?”
“三”
几乎不假思索的一个答案说出，诡异的女子连同那一道声音一起消失不见。
寂静的城市再次复苏，车水马龙，人来人往。
夜晚黑暗之中的恐怖，无人知晓。"""
    if "novel_target_chapter" not in st.session_state:
        st.session_state.novel_target_chapter = """她看向了声音传来的方向，却见窗外什么都没有，远处只有城市的灯光映照进了房间里。
是不是鸟撞上玻璃了?
秦瑶这样猜测着，随后有些好奇的凑到窗旁看了看。
等靠近之后，秦瑶这才看见，在玻璃上烙印着一张脸的轮廓，那人脸印的很清晰，可以明显的分辨出来那是一个老人的形象，此刻闭着眼睛，周围满是苍老的皱纹，神态十分安详，仿佛刚刚去世不久一般。
秦瑶伸手去擦，想要抹掉这个图案，但是很快她却手僵在了玻璃上犹如触电一般迅速的收了回来。
人脸的图案并不在朝房间的这面玻璃上，而是在外面。
"怎么会，这里可是二十八楼而且以前玻璃上绝对没有。"
秦瑶心头有些不安起来，她从小就坐在这窗边写作业，练习钢琴，背功课，窗外不知道看了多少遍。
她心中十分确认，以前窗户外是十分干净的，不会留下这样一个人脸印记。
爸，你过来看看，窗户上那是什么..
秦瑶有些心慌了，她缓缓后退远离那窗户，然后喊了一声。
但是房间外一片寂静，一点声音都没有。
秦瑶再次喊了几声，外面的父亲依旧没有回应，周围更是出奇的安静，，她感觉自己就像是被隔绝了一样，有一种被孤立，遗落的恐惧感。
窗外。
随着远处的一道灯光晃过，那映照在上面的人脸轮廓愈发的清晰了而且伴随着那道灯光在远处缓缓移动，不知道是不是光线带来的错觉秦瑶隐约觉得那张人脸好像在变得凶狠了起来，之前的安详已经荡然无存了。
"爸，爸，你快过来。"秦瑶的声音带着哭腔，
她被惊吓了，转身就想去开灯，也许开灯之后房间明亮起来，这些怪异的东西就会消失。
但是当她按动开关的时候却发现昏暗的房间依旧，卧房里的灯像是损坏掉了一样，没有任何点亮的迹象。"""
    
    # 初始化其他未定义的变量
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

ensure_session_state_initialized()

def one_click_generate():
    """一键全自动生成"""
    st.session_state.is_running = True
    
    if not st.session_state.novel_target_chapter.strip():
        st.warning("⚠️ 请先填写目标章节内容！")
        st.session_state.is_running = False
        return
    
    if not get_valid_config():
        st.error("❌ 无有效API配置！请填写至少一个模式的API信息")
        st.session_state.is_running = False
        return
    
    # 由于已移除上传图片功能，直接设置为None
    uploaded_image = None
    
    # 调试输出 - 打印当前会话状态的关键信息
    debug_info = {
        "is_running": st.session_state.is_running,
        "stop_flag": st.session_state.stop_flag,
        "selected_mode": st.session_state.selected_mode,
        "text_mode_api_provider": st.session_state.text_mode_api_provider,
        "text_mode_base_url": st.session_state.text_mode_base_url,
        "multimodal_mode_api_provider": st.session_state.multimodal_mode_api_provider,
        "multimodal_mode_base_url": st.session_state.multimodal_mode_base_url,
        "novel_target_chapter_length": len(st.session_state.novel_target_chapter),
        "uploaded_image_exists": uploaded_image is not None
    }
    
    # 可选的调试输出（注释掉以避免在生产环境中显示）
    # st.write("当前session_state关键信息：", debug_info)
    
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
    """渲染页面UI（核心UI逻辑，修复API Key持久化）"""
    st.markdown("""
<h1 style='text-align: center; margin-bottom: 2rem;'>
🎬 导演级分镜生成器（小说漫改专属）
</h1>
""", unsafe_allow_html=True)
    
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
                
                # ========== 核心修复1：API模式选择逻辑（仅切换标记，绝不触碰Key） ==========
                # 初始化模式标记（避免首次加载无值）
                if "api_mode_selector" not in st.session_state:
                    st.session_state.api_mode_selector = "文本模式" if st.session_state.selected_mode == "text_mode" else "图文模式"
                
                api_mode = st.radio(
                    "API调用模式",
                    options=["文本模式", "图文模式"],
                    horizontal=True,
                    key="api_mode_selector",
                    # 仅更新selected_mode，完全不修改任何API配置（包括Key/地址/模型）
                    on_change=lambda: st.session_state.update({
                        "selected_mode": "text_mode" if st.session_state.api_mode_selector == "文本模式" else "multimodal_mode"
                    }),
                    # 默认选中上次的模式
                    index=0 if st.session_state.selected_mode == "text_mode" else 1
                )
                
                # ========== 文本模式配置（完全独立，Key永久保存） ==========
                if api_mode == "文本模式":
                    st.session_state.selected_mode = "text_mode"
                    
                    # 服务商选择（核心修复：切换时总是更新地址和模型）
                    provider1 = st.selectbox(
                        "API服务商",
                        options=list(API_PRESETS.keys()),
                        key="text_mode_api_provider",
                        # 修复：切换服务商时总是更新地址和模型，不考虑是否已有值
                        on_change=lambda: st.session_state.update({
                            "text_mode_base_url": API_PRESETS[st.session_state.text_mode_api_provider]["base_url"],
                            "text_mode_model": API_PRESETS[st.session_state.text_mode_api_provider]["default_model"]
                        })
                    )
                    
                    # API Key（核心：仅读取，永不主动修改，type=password不影响持久化）
                    st.text_input(
                        "API Key", 
                        value=st.session_state.text_mode_api_key,  # 使用现有值
                        key="text_mode_api_key",
                        type="password", 
                        help="DeepSeek/OpenAI填密钥，火山方舟填AK:SK",
                        placeholder="请输入文本模式API Key",
                        # 修复：添加label_visibility避免布局抖动导致重渲染
                        label_visibility="visible"
                    )
                    
                    # 接口地址（显示当前服务商的地址，但允许用户修改）
                    st.text_input(
                        "接口地址", 
                        value=st.session_state.text_mode_base_url,  # 使用现有值
                        key="text_mode_base_url",
                        placeholder="文本模式接口地址",
                        label_visibility="visible"
                    )
                    
                    # 模型名（显示当前服务商的模型，但允许用户修改）
                    st.text_input(
                        "模型名", 
                        value=st.session_state.text_mode_model,  # 使用现有值
                        key="text_mode_model",
                        placeholder="文本模式模型名",
                        label_visibility="visible"
                    )
                    
                    # 配置状态提示
                    if check_config_valid("text_mode"):
                        st.success("✅ 文本模式配置有效")
                    else:
                        if st.session_state.text_mode_api_key.strip() or st.session_state.text_mode_base_url.strip() or st.session_state.text_mode_model.strip():
                            st.error("❌ 请填写完整文本模式API信息")
                    
                    # 重置默认配置按钮（仅重置地址/模型，绝不碰Key）
                    st.button(
                        "🔄 重置文本模式默认配置",
                        on_click=lambda: st.session_state.update({
                            "text_mode_base_url": API_PRESETS[st.session_state.text_mode_api_provider]["base_url"],
                            "text_mode_model": API_PRESETS[st.session_state.text_mode_api_provider]["default_model"]
                        }),
                        type="secondary",
                        help="将接口地址/模型名恢复为所选服务商的默认值（不影响API Key）"
                    )
                
                # ========== 图文模式配置（完全独立，Key永久保存） ==========
                else:
                    st.session_state.selected_mode = "multimodal_mode"
                    
                    # 服务商选择（核心修复：切换时总是更新地址和模型）
                    provider2 = st.selectbox(
                        "API服务商",
                        options=list(API_PRESETS.keys()),
                        key="multimodal_mode_api_provider",
                        # 修复：切换服务商时总是更新地址和模型，不考虑是否已有值
                        on_change=lambda: st.session_state.update({
                            "multimodal_mode_base_url": API_PRESETS[st.session_state.multimodal_mode_api_provider]["base_url"],
                            "multimodal_mode_model": API_PRESETS[st.session_state.multimodal_mode_api_provider]["default_model"]
                        })
                    )
                    
                    # API Key（仅读取，永不修改）
                    st.text_input(
                        "API Key", 
                        value=st.session_state.multimodal_mode_api_key,  # 使用现有值
                        key="multimodal_mode_api_key",
                        type="password",
                        placeholder="请输入图文模式API Key",
                        label_visibility="visible"
                    )
                    
                    # 接口地址（显示当前服务商的地址，但允许用户修改）
                    st.text_input(
                        "接口地址", 
                        value=st.session_state.multimodal_mode_base_url,  # 使用现有值
                        key="multimodal_mode_base_url",
                        placeholder="图文模式接口地址",
                        label_visibility="visible"
                    )
                    
                    # 模型名（显示当前服务商的模型，但允许用户修改）
                    st.text_input(
                        "模型名", 
                        value=st.session_state.multimodal_mode_model,  # 使用现有值
                        key="multimodal_mode_model",
                        placeholder="图文模式模型名",
                        label_visibility="visible"
                    )
                    
                    # 配置状态提示
                    if check_config_valid("multimodal_mode"):
                        st.success("✅ 图文模式配置有效")
                    else:
                        if st.session_state.multimodal_mode_api_key.strip() or st.session_state.multimodal_mode_base_url.strip() or st.session_state.multimodal_mode_model.strip():
                            st.error("❌ 请填写完整图文模式API信息")
                    
                    # 重置默认配置按钮（仅重置地址/模型，不碰Key）
                    st.button(
                        "🔄 重置图文模式默认配置",
                        on_click=lambda: st.session_state.update({
                            "multimodal_mode_base_url": API_PRESETS[st.session_state.multimodal_mode_api_provider]["base_url"],
                            "multimodal_mode_model": API_PRESETS[st.session_state.multimodal_mode_api_provider]["default_model"]
                        }),
                        type="secondary",
                        help="将接口地址/模型名恢复为所选服务商的默认值（不影响API Key）"
                    )
            
            # 第二部分：小说信息输入
            with st.container(border=True):
                st.subheader("📝 小说信息")
                st.write('<div class="tag tag-primary">内容输入</div>', unsafe_allow_html=True)
                
                # 为测试设置默认值
                st.text_input("小说标题", value=st.session_state.novel_title, key="novel_title", placeholder="如：三体·黑暗森林", label_visibility="visible")
                st.text_input("小说作者", value=st.session_state.novel_author, key="novel_author", placeholder="如：刘慈欣", label_visibility="visible")
                st.text_area("多章节背景（可选）", value=st.session_state.novel_background, key="novel_background", height=100, placeholder="粘贴小说整体设定...", label_visibility="visible")
                st.text_area("目标章节内容（必填）", value=st.session_state.novel_target_chapter, key="novel_target_chapter", height=250, placeholder="粘贴目标章节内容...", label_visibility="visible")
        
        with main_right:
            # 提前统一获取上传图片为None（因为已移除该功能）
            uploaded_image = None
            # 第一部分：操作面板（导演和分镜生成）
            with st.container(border=True):
                st.subheader("🎬 分镜创作面板")
                st.write('<div class="tag tag-primary">核心操作</div>', unsafe_allow_html=True)
                
                # 统一获取上传图片（从session_state读取）
                uploaded_image = st.session_state.get("multimodal_mode_uploaded_image")
                
                # 导演推荐和风格生成
                row1 = st.columns([2, 2, 2])
                with row1[0]:
                    st.button(
                        "🔍 智能推荐导演",
                        on_click=lambda: ai_recommend_director(auto=False),  # 移除uploaded_image参数，并明确auto=False
                        type="secondary",
                        disabled=not st.session_state.novel_target_chapter.strip() or st.session_state.is_running
                    )
                with row1[1]:
                    selected_dir = st.session_state.selected_director or st.session_state.custom_director_name
                    st.button(
                        "✨ 生成导演风格",
                        on_click=lambda: generate_director_persona(auto=False),  # 移除uploaded_image参数，并明确auto=False
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
                    custom_dir = st.text_input("自定义导演姓名", key="custom_director_name", placeholder="输入后自动选中该导演", label_visibility="visible")
                    if custom_dir and custom_dir.strip():
                        st.session_state.selected_director = custom_dir.strip()
                with row2[1]:
                    if st.button(
                        "🎬 生成分镜",
                        key="btn_generate_storyboard",
                        type="primary",
                        disabled=not st.session_state.novel_target_chapter.strip() or st.session_state.is_running
                    ):
                        if generate_storyboards(auto=False):
                            st.rerun()
                with row2[2]:
                    if st.button(
                        "🌟 一键全自动生成",
                        key="btn_one_click_generate",
                        type="primary",
                        disabled=not st.session_state.novel_target_chapter.strip() or st.session_state.is_running
                    ):
                        one_click_generate()
                
                # 导演列表展示
                if st.session_state.director_recommend_list:
                    with st.expander("🎯 适配导演推荐列表", expanded=False):
                        director_names = [d["name"] for d in st.session_state.director_recommend_list]
                        # 修复：避免index越界
                        default_idx = director_names.index(st.session_state.director_radio) if st.session_state.director_radio in director_names else 0
                        selected_name = st.radio(
                            "选择导演",
                            options=director_names,
                            key="director_radio",
                            index=default_idx,
                            on_change=lambda: st.session_state.update({"selected_director": st.session_state.director_radio}),
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
                    
                    # 统一获取上传图片
                    uploaded_image = st.session_state.get("multimodal_mode_uploaded_image")
                    
                    # 校验按钮
                    row_validate = st.columns([2, 2])
                    with row_validate[0]:
                        st.button(
                            "🔍 校验分镜一致性",
                            on_click=lambda: validate_storyboard_consistency(),  # 移除uploaded_image参数
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
                            
                            # 显示优化建议对比
                            if st.session_state.get("validation_suggestions"):
                                with st.expander("🔍 查看优化建议详情", expanded=False):
                                    st.write("**发现的问题:**")
                                    # 从验证结果中提取问题
                                    validation_result = st.session_state.get("validation_result", "")
                                    lines = validation_result.split("\n")
                                    for line in lines:
                                        line = line.strip()
                                        if line.startswith("-") and not ("建议" in line or "优化" in line or "统一" in line or "调整" in line or "保持" in line):
                                            st.write(f"- {line[1:].strip()}")
                                    
                                    st.write("**优化建议:**")
                                    for suggestion in st.session_state["validation_suggestions"]:
                                        st.write(f"- {suggestion}")
                                    
                                    # 显示优化前后的对比
                                    if st.session_state.get("storyboards"):
                                        st.write("**优化前后对比:**")
                                        col_before, col_after = st.columns(2)
                                        
                                        with col_before:
                                            st.write("优化前:")
                                            # 显示第一个分镜的优化前提示词（即初始生成的提示词）
                                            if st.session_state["storyboards"]:
                                                # 由于我们没有保存原始提示词，使用当前优化前的提示词
                                                original_prompt = st.session_state["storyboards"][0]["optimized_prompt"]
                                                # 移除建议部分得到原始提示词
                                                for suggestion in st.session_state["validation_suggestions"]:
                                                    original_prompt = original_prompt.replace("，" + suggestion, "")
                                                st.text_area("优化前提示词:", value=original_prompt, height=150, key="before_textarea_validation")
                                            else:
                                                st.info("暂无提示词数据")
                                        
                                        with col_after:
                                            st.write("优化后:")
                                            # 显示第一个分镜的优化后提示词
                                            if st.session_state["storyboards"]:
                                                st.text_area("优化后提示词:", value=st.session_state["storyboards"][0]["optimized_prompt"], height=150, key="after_textarea_validation")
                                            else:
                                                st.info("暂无提示词数据")
            
            # 第三部分：分镜结果展示
            if st.session_state.storyboards:
                with st.container(border=True):
                    st.subheader("🎞️ 分镜生成结果")
                    st.write('<div class="tag tag-success">成果展示</div>', unsafe_allow_html=True)
                    
                    # 筛选功能
                    filter_row = st.columns([2, 2, 2])
                    with filter_row[0]:
                        emotion_filter = st.selectbox("按情绪筛选", options=["全部"] + list(set([s["emotion"] for s in st.session_state.storyboards])), label_visibility="visible")
                    with filter_row[1]:
                        # 修复：人物筛选值匹配（原逻辑用"是"/"否"，需和storyboards里的字段一致）
                        character_filter = st.selectbox("按人物筛选", options=["全部", "是", "否"], label_visibility="visible")
                    with filter_row[2]:
                        # 确保 filtered_storyboards 已初始化
                        if "storyboards" in st.session_state and st.session_state["storyboards"]:
                            # 应用筛选条件
                            filtered_storyboards = []
                            for sb in st.session_state["storyboards"]:
                                # 应用情绪筛选
                                emotion_match = emotion_filter == "全部" or sb.get("emotion", "") == emotion_filter
                                # 应用人物筛选
                                character_match = character_filter == "全部" or sb.get("has_character", "") == character_filter
                                
                                if emotion_match and character_match:
                                    filtered_storyboards.append(sb)
                        else:
                            filtered_storyboards = []

                        # 创建安全的导出数据列表，处理空值情况
                        download_data = []
                        for i, sb in enumerate(filtered_storyboards):
                            prompt = sb.get("optimized_prompt", "") or "无"
                            neg_prompt = sb.get("negative_prompt", "") or "无"
                            download_data.append(f"镜头 {i+1}：\n正向提示词：{prompt}\n负向提示词：{neg_prompt}")
                        
                        st.download_button(
                            "💾 批量导出筛选结果",
                            data="\n\n=== 分割线 ===\n\n".join(download_data) if download_data else "无分镜数据",
                            file_name=f"{st.session_state.novel_title or '小说分镜'}_{'筛选结果' if len(filtered_storyboards) != len(st.session_state.storyboards) else '完整提示词包'}.txt",
                            mime="text/plain"
                        )
                    
                    # 分镜展示（带复制按钮）
                    for idx, sb in enumerate(filtered_storyboards):
                        scene_core = sb.get('scene', '').split('：')[1].split('\n')[0] if '：' in sb.get('scene', '') else '未命名'
                        with st.expander(f"📸 镜头 {idx+1}：{scene_core}", expanded=False):
                            # 分镜基础信息
                            col_info, col_prompts = st.columns([1, 1])
                            
                            with col_info:
                                st.write("### 📝 分镜信息")
                                st.write(f"**情绪**：{sb.get('emotion', 'N/A')}")
                                st.write(f"**镜头**：{sb.get('camera', 'N/A')}")
                                st.write(f"**氛围**：{sb.get('atmosphere', 'N/A')}")
                                st.write(f"**有人物**：{sb.get('has_character', 'N/A')}")
                                
                                if sb.get('has_character', '') == "是":
                                    st.write(f"**人物特征**：{sb.get('character_feature', '')[:100] + '...' if len(str(sb.get('character_feature', ''))) > 100 else sb.get('character_feature', '')}")
                                st.write(f"**场景细节**：{sb.get('environment', '')[:100] + '...' if len(str(sb.get('environment', ''))) > 100 else sb.get('environment', '')}")
                            
                            with col_prompts:
                                # 优化提示词（带复制）
                                st.write("### 🎨 优化提示词（推荐）")
                                optimized_text = st.text_area(
                                    "优化提示词", 
                                    value=sb.get('optimized_prompt', ''), 
                                    height=180,
                                    key=f"optimized_{idx}"
                                )
                                st.code(f"📋 复制：{optimized_text[:50]}..." if len(optimized_text) > 50 else f"📋 复制：{optimized_text}", language="text")
                                
                                # ComfyUI提示词（备用）
                                st.write("### 🔧 ComfyUI提示词（备选）")
                                comfy_text = st.text_area(
                                    "ComfyUI提示词", 
                                    value=sb.get('comfyui_prompt', ''), 
                                    height=120,
                                    key=f"comfy_{idx}"
                                )
                                st.code(f"📋 复制：{comfy_text[:50]}..." if len(comfy_text) > 50 else f"📋 复制：{comfy_text}", language="text")
                                
                                # 负向提示词
                                st.write("### ⚠️ 负向提示词")
                                negative_text = st.text_area(
                                    "负向提示词", 
                                    value=sb.get('negative_prompt', ''), 
                                    height=80,
                                    key=f"negative_{idx}"
                                )
                                st.code(f"❌ 避免：{negative_text[:50]}..." if len(negative_text) > 50 else f"❌ 避免：{negative_text}", language="text")
                                
                                # 视频提示词
                                if sb.get('video_prompt'):
                                    st.write("### 🎬 视频提示词")
                                    video_text = st.text_area(
                                        "视频提示词", 
                                        value=sb.get('video_prompt', ''), 
                                        height=100,
                                        key=f"video_{idx}"
                                    )
                                    st.code(f"🎥 视频：{video_text[:50]}..." if len(video_text) > 50 else f"🎥 视频：{video_text}", language="text")
    
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
        
        ### ⚠️ 重要提示
        - API Key会保存在当前会话中，关闭浏览器/标签页后丢失（如需持久化，可手动记录）
        - 切换服务商时接口地址和模型会自动更新，但也可手动修改以使用特定模型
        - 如需使用DeepSeek的其他模型（如deepseek-coder、deepseek-reasoner等），可在选择服务商后手动修改模型名字段
        """)

# ========== 核心修复3：增强session_state初始化（确保所有Key都有默认值） ==========
def enhanced_init_session_state():
    """增强版会话状态初始化（确保API Key字段永不被清空）"""
    # 先执行原有初始化
    init_session_state()
    
    # 补充API相关字段的兜底（如果不存在则初始化，存在则保留原值）
    api_defaults = {
        # 文本模式
        "text_mode_api_key": "",
        "text_mode_base_url": "https://api.deepseek.com/v1/chat/completions",
        "text_mode_model": "deepseek-chat",
        # 图文模式
        "multimodal_mode_api_key": "",
        "multimodal_mode_base_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "multimodal_mode_model": "doubao-seed-1-8-251228",
        "multimodal_mode_image_url": "",
        # 模式标记
        "api_mode_selector": "文本模式",
        "selected_mode": "text_mode"
    }
    
    for key, default_val in api_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_val

# 主函数（仅初始化+渲染UI）
def main():
    init_basic_config()
    enhanced_init_session_state()  # 替换原有初始化，增强API字段兜底
    render_page_layout()

if __name__ == "__main__":
    main()
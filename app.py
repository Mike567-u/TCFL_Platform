import streamlit as st
import pandas as pd
import random
from datetime import datetime
from urllib.parse import quote_plus
import os
import json
import io
from gtts import gTTS

# ==========================================
# 1. 页面基础配置
# ==========================================
st.set_page_config(
    page_title="以赛促学平台 V15.1",
    page_icon="🏆",
    layout="centered",  # 手机端兼容性更好
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. 数据中心 (100% 还原 notebook 数据)
# ==========================================

# 语音生成函数（使用 gTTS）
def generate_speech(text: str) -> bytes:
    """生成中文语音"""
    try:
        tts = gTTS(text=text, lang='zh-CN', slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.getvalue()
    except Exception as e:
        st.error(f"发音生成失败: {str(e)[:50]}")
        return None

def play_audio(word: str, key_id: str):
    """播放词汇发音"""
    try:
        audio_bytes = generate_speech(word)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
    except Exception as e:
        st.warning(f"播放失败: {str(e)[:30]}")

# (1) 课程结构数据
LESSONS_DATA = [
    (1, "汉语可以这样学", "学习方法"), (2, "颜色的寓意", "文化象征"),
    (3, "幸福的水花身上泼", "节日风俗"), (4, "原来筷子有这么多讲究", "餐桌礼仪"),
    (5, "礼轻情意重", "送礼文化"), (6, "在家谁做饭", "家庭分工"),
    (7, "网购与生活", "网络购物"), (8, "移动支付真方便", "科技生活"),
    (9, "妈妈的退休生活", "老龄化"), (10, "实习不是打杂儿", "职场体验"),
    (11, "无声的蛋糕店", "社会关爱"), (12, "越来越淡的年味儿", "春节变迁"),
    (13, "孩子的零花钱", "教育观念"), (14, "我想搬出去住", "租房生活")
]

# (1.5) 课程背景知识 (课前预习)
BACKGROUND_KNOWLEDGE = {
    1: {
        "背景": "这一课探讨如何高效学习汉语。汉语学习需要多维度的方法，包括语音、文字、文化等。",
        "学习要点": ["语音系统（声调、拼音）", "汉字结构（偏旁、笔画）", "文化体验的重要性"],
        "预习任务": "思考并列举3种你认为最有效的语言学习方法，并说出理由。"
    },
    2: {
        "背景": "中国文化中，颜色不仅是视觉元素，更承载着深厚的文化寓意。红色、黄色、绿色等在中国传统文化中都有特殊的象征意义。",
        "学习要点": ["红色象征吉祥和喜庆", "黄色代表皇权和尊贵", "色彩禁忌与文化信仰"],
        "预习任务": "调查你的母文化中有哪些颜色禁忌？请举2-3个例子。"
    },
    3: {
        "背景": "泼水节是傣族的传统节日，源于对水的崇拜。它不仅是庆祝新年的方式，更体现了对美好生活的祝愿。",
        "学习要点": ["泼水节的文化起源", "节日的传统活动", "区域文化差异"],
        "预习任务": "描述你的国家或地区最重要的传统节日，及其主要活动。"
    },
    4: {
        "背景": "筷子是中国餐桌文化的重要象征，使用筷子的礼仪规范反映了中国的餐桌文明。某些行为被认为不礼貌是因为它们与传统习俗或迷信相关。",
        "学习要点": ["筷子的历史和文化", "餐桌礼仪的重要性", "文化禁忌的原因"],
        "预习任务": "总结你了解的3条筷子使用禁忌及其背后的原因。"
    },
    5: {
        "背景": "\"礼轻情意重\"是中国传统的礼仪理念，强调礼物的象征意义大于物质价值。\"面子\"文化在中国社交中扮演重要角色。",
        "学习要点": ["礼仪文化与人际关系", "\"面子\"的社会意义", "送礼的文化规范"],
        "预习任务": "在你的文化中，怎样选择和赠送礼物才是得体和尊重的？"
    },
    6: {
        "背景": "现代中国家庭正在经历性别角色的变化。越来越多家庭开始平衡家务分工，这反映了社会观念的进步。",
        "学习要点": ["传统家庭分工vs现代平等观", "性别角色的变化", "家庭关系的和谐"],
        "预习任务": "调查你周围5个家庭的家务分工方式，记录下来。"
    },
    7: {
        "背景": "网购已成为现代生活的一部分。它改变了消费方式，但也带来了新的问题，如过度消费、商品质量等。",
        "学习要点": ["电商的发展趋势", "消费心理与行为", "网购的优缺点"],
        "预习任务": "列举你最常用的3个网购平台，并分析它们的优势。"
    },
    8: {
        "背景": "移动支付在中国已经成为主流支付方式，对经济和社会产生了深远影响。同时，安全和隐私问题也不容忽视。",
        "学习要点": ["移动支付的发展历程", "支付方式的变化", "金融安全与隐私保护"],
        "预习任务": "对比2-3种主要的支付方式（现金、银行卡、移动支付），列出它们的优缺点。"
    },
    9: {
        "背景": "随着社会老龄化，退休生活的质量成为重要话题。中国老年人群体越来越重视精神生活和社交活动。",
        "学习要点": ["老龄化社会的特点", "退休生活的质量", "代际关系与社会责任"],
        "预习任务": "采访一位退休者（可以是家人或朋友），了解他/她的退休生活如何安排。"
    },
    10: {
        "背景": "实习是连接学校和职场的重要桥梁。正确理解实习的价值，有助于更好地把握职业发展机会。",
        "学习要点": ["实习的真正目的", "职场体验的重要性", "简历与学历的关系"],
        "预习任务": "查找3个你感兴趣的实习机会，分析每个职位的要求。"
    },
    11: {
        "背景": "\"无声的蛋糕店\"是一个社会实验，展示了残疾人群体的自我价值和社会贡献能力。这启发我们重新思考如何对待弱势群体。",
        "学习要点": ["社会包容性", "残疾人权益", "自强与尊重"],
        "预习任务": "调查你所在地区有哪些帮助残疾人的社会项目或企业。"
    },
    12: {
        "背景": "春节是中国最重要的传统节日，但其庆祝方式在现代社会中正在演变。这反映了文化的流变和社会的发展。",
        "学习要点": ["春节的传统与现代", "文化变迁的原因", "传统保护与创新"],
        "预习任务": "对比你祖父母时代和现在的春节庆祝方式有什么不同？"
    },
    13: {
        "背景": "零花钱教育是家庭教育的重要组成部分。如何给孩子零花钱反映了父母对自主性和责任感培养的理解。",
        "学习要点": ["理财教育的重要性", "儿童教育观念", "金钱与价值观"],
        "预习任务": "设计一个合理的零花钱管理计划，并解释你的理由。"
    },
    14: {
        "背景": "搬出去住代表着向成人独立看齐。租住生活涉及经济、法律、人际关系等多方面内容。",
        "学习要点": ["租房文化与法律", "独立生活的挑战", "成人责任与权利"],
        "预习任务": "了解你所在地区的租房市场情况，包括平均租金、常见合租情况等。"
    }
}

# (2) 精准词汇表 (Map)
VOCAB_MAP = {
    1: [('声调','shēngdiào','Tone','语音'), ('模仿','mófǎng','Imitate','方法'), ('偏旁','piānpáng','Radical','汉字'), ('体验','tǐyàn','Experience','动词'), ('相似','xiāngsì','Similar','形容词')],
    2: [('寓意','yùyì','Implied meaning','名词'), ('忌讳','jìhuì','Taboo','名词'), ('崇拜','chóngbài','Worship','动词'), ('显眼','xiǎnyǎn','Conspicuous','形容词'), ('象征','xiàngzhēng','Symbolize','动词')],
    3: [('传说','chuánshuō','Legend','名词'), ('吉祥','jíxiáng','Lucky','形容词'), ('泼水','pōshuǐ','Splash water','动词'), ('信物','xìnwù','Token','名词'), ('西双版纳','Xīshuāngbǎnnà','Place name','专名'), ('兴高采烈','xìnggāocǎiliè','In high spirits','成语')],
    4: [('分餐制','fēncānzhì','Separate dining','文化'), ('入乡随俗','rùxiāngsuísú','Do as Romans do','成语'), ('讲究','jiǎngjiu','Particular/Exquisite','形容词'), ('夹','jiā','Pick up (with chopsticks)','动词'), ('餐具','cānjù','Tableware','名词'), ('乞丐','qǐgài','Beggar','名词'), ('鱼刺','yúcì','Fish bone','名词'), ('挑','tiāo','Pick/Poke','动词'), ('牙签','yáqiān','Toothpick','名词')],
    5: [('礼尚往来','lǐshàngwǎnglái','Courtesy demands reciprocity','成语'), ('做客','zuòkè','Be a guest','动词'), ('面子','miànzi','Face/Prestige','文化')],
    6: [('承担','chéngdān','Undertake','动词'), ('体贴','tǐtiē','Considerate','形容词'), ('家务','jiāwù','Housework','名词'), ('细','xì','Careful/Fine','形容词')],
    7: [('物流','wùliú','Logistics','名词'), ('评价','píngjià','Review','名词'), ('实体店','shítǐdiàn','Physical store','名词'), ('下单','xiàdān','Place an order','动词'), ('嫌','xián','Dislike','动词'), ('享受','xiǎngshòu','Enjoy','动词'), ('喜好','xǐhào','Preference','名词')],
    8: [('二维码','èrwéimǎ','QR Code','科技'), ('转账','zhuǎnzhàng','Transfer','金融'), ('泄露','xièlòu','Leak','安全'), ('纸币','zhǐbì','Banknote','名词'), ('细菌','xìjūn','Bacteria','名词'), ('摊','tān','Stall','名词'), ('轻易','qīngyì','Easily','副词'), ('兑换','duìhuàn','Exchange','动词'), ('汇率','huìlǜ','Exchange rate','名词'), ('损失','sǔnshī','Loss','名词'), ('显示','xiǎnshì','Display','动词'), ('摆脱','bǎituō','Break away from','动词'), ('依赖','yīlài','Rely on','动词'), ('隐私','yǐnsī','Privacy','名词'), ('保障','bǎozhàng','Guarantee','动词')],
    9: [('寂寞','jìmò','Lonely','心理'), ('丰富','fēngfù','Rich','形容词'), ('广场舞','guǎngchǎngwǔ','Square dance','文化'), ('延续','yánxù','Continue','动词')],
    10: [('简历','jiǎnlì','Resume','求职'), ('打杂','dǎzá','Do odds and ends','口语'), ('录用','lùyòng','Hire','动词'), ('项目','xiàngmù','Project','名词'), ('学历','xuélì','Education background','名词')],
    11: [('聋哑人','lóngyǎrén','Deaf-mute','名词'), ('尊重','zūnzhòng','Respect','动词'), ('自强','zìqiáng','Self-improvement','精神')],
    12: [('气氛','qìfēn','Atmosphere','名词'), ('团圆','tuányuán','Reunion','动词'), ('春运','chūnyùn','Spring Festival travel','文化'), ('习俗','xísú','Custom','名词'), ('压岁钱','yāsuìqián','Money given to children','文化'), ('放鞭炮','fàngbiānpào','Set off firecrackers','活动')],
    13: [('零花钱','línghuaqián','Pocket money','名词'), ('惯','guàn','Spoil','动词'), ('理财','lǐcái','Manage money','动词'), ('家长','jiāzhǎng','Parent','名词'), ('物质','wùzhì','Material','名词'), ('信任','xìnrèn','Trust','动词'), ('学问','xuéwen','Knowledge/Learning','名词')],
    14: [('中介','zhōngjiè','Agency','名词'), ('押金','yājīn','Deposit','名词'), ('合租','hézū','Share rent','动词')]
}

# (3) 真实赛事资讯
NEWS_DATA = [
    {'type': '重磅', 'title': '第二十五届 “汉语桥” 世界大学生中文比赛活动方案', 'date': '2026-2-10', 'source': '汉语桥官网', 'url': 'http://bridge.chinese.cn/wap/index/pc/news-detail.html?id=28626&type=notice'},
    {'type': '赛事', 'title': '2026“汉语桥” 春节联欢晚会主题节目征集公告', 'date': '2026-02-12', 'source': '汉语桥官网', 'url': 'http://bridge.chinese.cn/wap/index/pc/news-detail.html?id=28166&type=notice'},
    {'type': '考试', 'title': '第二十四届 “汉语桥" 世界大学生中文比赛活动方案', 'date': '2025-02-25', 'source': '汉语桥官网', 'url': 'http://bridge.chinese.cn/wap/index/pc/news-detail.html?id=24834&type=notice'},
    {'type': '活动', 'title': '第六届国际汉语节', 'date': '2025-09-20', 'source': '国际汉语节官网', 'url': 'https://chineselanguagefestival.com/zh/%E7%AC%AC%E5%85%AD%E5%B1%8A%E5%9B%BD%E9%99%85%E6%B1%89%E8%AF%AD%E8%8A%82_cn/'},
    {'type': '奖学金', 'title': '第二届中国研究生国际中文教育案例大赛参赛指南', 'date': '2025-05-24', 'source': '中国研究生国际中文教育案例大赛', 'url': 'https://cpipc.acge.org.cn//cw/detail/2c9080158e2ad864018e5fa55a450c49/2c90801896f759470197021604e30b1e'}
]

# 为每条资讯补上可点击的链接：优先保留已有 'url'，否则构造搜索链接作为入口
for _n in NEWS_DATA:
    if not _n.get('url'):
        _n['url'] = f"https://www.bing.com/search?q={quote_plus(_n['title'])}"

# (4) 竞赛视频
VIDEO_DATA = [
    {'cat': '汉语桥', 'title': '第二十四届“汉语桥”世界大学生中文比赛全球总决赛精彩回顾', 'desc': '精彩回顾与高光片段。', 'url': 'https://www.bilibili.com/video/BV19Be1zXEwP/?spm_id_from=333.337.search-card.all.click', 'color': '#e74c3c'},
    {'cat': '经典诵读', 'title': '“汉语桥”在福建的这场告别仪式让人泪目', 'desc': '福建赛区告别仪式现场花絮。', 'url': 'https://www.bilibili.com/video/BV1FKe2zvEaZ?spm_id_from=333.788.videopod.sections', 'color': '#3498db'},
    {'cat': '短视频', 'title': '墨西哥选手艾乐恩用传统皮影戏诉说中国传奇故事', 'desc': '选手用皮影戏讲述中国故事的精彩表演。', 'url': 'https://www.bilibili.com/video/BV1LdeGzAEWr?spm_id_from=333.788.videopod.sections', 'color': '#9b59b6'},
    {'cat': '教学示范', 'title': '我是怎么赢的汉语桥中文比赛', 'desc': '选手分享备赛经验与心得。', 'url': 'https://www.bilibili.com/video/BV1oT4y1K75c/?spm_id_from=333.337.search-card.all.click', 'color': '#2ecc71'},
    {'cat': '文化体验', 'title': '20251129 宁夏卫视 第24届汉语桥世界大学生中文比赛', 'desc': '宁夏卫视对总决赛的电视报道剪辑。', 'url': 'https://www.bilibili.com/video/BV1KnSqBMEXW/?spm_id_from=333.337.search-card.all.click', 'color': '#f1c40f'}
]

# (4.5) 学生竞赛成果展示视频
STUDENT_VIDEO_DATA = [
    {'title': '孔门问答', 'desc': '通过对话形式，深入探讨儒家文化与现代社会的关系。', 'url': 'https://www.bilibili.com/video/BV11fNFz6Eag/?vd_source=31ec2780eec4d90917efb3d81a5ab670', 'color': '#ff6b6b'},
    {'title': '弦上汉语，桥间雅韵', 'desc': '将音乐与语言完美结合，展现汉语的艺术之美。', 'url': 'https://www.bilibili.com/video/BV1hL3FzaE49/?spm_id_from=333.337.search-card.all.click&vd_source=31ec2780eec4d90917efb3d81a5ab670', 'color': '#4ecdc4'},
    {'title': '汉韵为友，弦动他乡', 'desc': '在异国他乡用汉语和音乐传递文化的温度。', 'url': 'https://www.bilibili.com/video/BV1AcgRzqEEQ/?spm_id_from=333.788.videopod.sections&vd_source=31ec2780eec4d90917efb3d81a5ab670', 'color': '#95e1d3'},
    {'title': '在青岛，汉语有海的味道', 'desc': '将城市特色与汉语学习融为一体，展现地方文化魅力。', 'url': 'https://www.bilibili.com/video/BV12ZNFz3E38/?vd_source=31ec2780eec4d90917efb3d81a5ab670', 'color': '#44b393'}
]

# (5) 扩展的汉语竞赛题库 (基础题+提高题)
def get_quiz_data():
    questions = []
    
    # 第1课 - 汉语可以这样学
    questions.extend([
        {"lid": 1, "difficulty": "基础", "type": "词汇", "q": '"体验"的意思最接近以下哪个选项？', "opts": ["理论学习", "亲身经历", "书本知识"], "ans": "亲身经历"},
        {"lid": 1, "difficulty": "基础", "type": "文化", "q": "学习汉语的最有效方法是什么？", "opts": ["只看书", "多实践和体验", "背字典"], "ans": "多实践和体验"},
        {"lid": 1, "difficulty": "提高", "type": "语言运用", "q": '用"相似"造句，以下哪个句子最恰当？', "opts": ["这两个单词的发音相似。", "这个颜色很相似。", "我相似他很聪明。"], "ans": "这两个单词的发音相似。"},
    ])
    
    # 第2课 - 颜色的寓意
    questions.extend([
        {"lid": 2, "difficulty": "基础", "type": "文化", "q": "在中国文化中，红色通常象征什么？", "opts": ["悲伤", "幸运和喜庆", "严肃"], "ans": "幸运和喜庆"},
        {"lid": 2, "difficulty": "基础", "type": "词汇", "q": '"象征"最接近以下哪个意思？', "opts": ["代表", "看起来", "变成"], "ans": "代表"},
        {"lid": 2, "difficulty": "提高", "type": "文化理解", "q": '为什么在某些文化中会"忌讳"（jìhuì）某种颜色？', "opts": ["因为这种颜色不好看", "因为文化传统中赋予了特殊含义", "因为这种颜色太显眼"], "ans": "因为文化传统中赋予了特殊含义"},
    ])
    
    # 第3课 - 幸福的水花身上泼
    questions.extend([
        {"lid": 3, "difficulty": "基础", "type": "常识", "q": "以下哪个是泼水节的传统活动？", "opts": ["放鞭炮", "泼水", "贴春联"], "ans": "泼水"},
        {"lid": 3, "difficulty": "基础", "type": "词汇", "q": '"传说"是什么意思？', "opts": ["真实的历史", "民间流传的故事", "官方记录"], "ans": "民间流传的故事"},
        {"lid": 3, "difficulty": "提高", "type": "成语理解", "q": '理解成语"兴高采烈"，以下哪个描述最准确？', "opts": ["心情低落", "非常高兴和兴奋", "工作繁忙"], "ans": "非常高兴和兴奋"},
    ])
    
    # 第4课 - 原来筷子有这么多讲究
    questions.extend([
        {"lid": 4, "difficulty": "基础", "type": "文化", "q": "为什么中国人忌讳用筷子敲碗？", "opts": ["不卫生", "像乞丐要饭", "容易打破碗"], "ans": "像乞丐要饭"},
        {"lid": 4, "difficulty": "基础", "type": "词汇", "q": '"讲究"作为形容词时意思是？', "opts": ["讨厌", "讲解", "精致、挑剔"], "ans": "精致、挑剔"},
        {"lid": 4, "difficulty": "提高", "type": "语言运用", "q": "以下哪个不是使用筷子的不礼貌行为？", "opts": ["敲碗", "插进米饭", "轻轻夹菜"], "ans": "轻轻夹菜"},
    ])
    
    # 第5课 - 礼轻情意重
    questions.extend([
        {"lid": 5, "difficulty": "基础", "type": "文化", "q": "中国有一句俗语说的是关于赠送礼物的原则是什么？", "opts": ["礼越贵越好", "礼轻情意重", "只送最贵的"], "ans": "礼轻情意重"},
        {"lid": 5, "difficulty": "基础", "type": "词汇", "q": '"做客"是什么意思？', "opts": ["做生意", "去别人家做客", "工作"], "ans": "去别人家做客"},
        {"lid": 5, "difficulty": "提高", "type": "文化理解", "q": '"面子"在中国文化中最重要的含义是什么？', "opts": ["脸部", "尊严和名誉", "表面"], "ans": "尊严和名誉"},
    ])
    
    # 第6课 - 在家谁做饭
    questions.extend([
        {"lid": 6, "difficulty": "基础", "type": "词汇", "q": '"承担"的意思是什么？', "opts": ["放弃", "担当、承担责任", "拒绝"], "ans": "担当、承担责任"},
        {"lid": 6, "difficulty": "基础", "type": "文化", "q": "现代中国家庭分工的趋势如何？", "opts": ["女性做所有家务", "家务分担变得更平等", "男性做所有家务"], "ans": "家务分担变得更平等"},
        {"lid": 6, "difficulty": "提高", "type": "语言运用", "q": '"体贴"在这句中的用法是什么："她很体贴地照顾了生病的家人"？', "opts": ["名词", "形容词", "动词"], "ans": "形容词"},
    ])
    
    # 第7课 - 网购与生活
    questions.extend([
        {"lid": 7, "difficulty": "基础", "type": "词汇", "q": '"下单"是什么意思？', "opts": ["支付订单", "下楼", "提交购买请求"], "ans": "提交购买请求"},
        {"lid": 7, "difficulty": "基础", "type": "文化", "q": "网购相比实体店的主要优势是什么？", "opts": ["更贵", "方便快捷", "品质更差"], "ans": "方便快捷"},
        {"lid": 7, "difficulty": "提高", "type": "语言运用", "q": '理解句子："顾客对商品的评价很重要"，这里"评价"是什么词性？', "opts": ["动词", "名词", "形容词"], "ans": "名词"},
    ])
    
    # 第8课 - 移动支付真方便
    questions.extend([
        {"lid": 8, "difficulty": "基础", "type": "听力理解", "q": "记者采访中，受访者认为移动支付最大的风险是什么？", "opts": ["没电", "隐私泄露", "操作复杂"], "ans": "隐私泄露"},
        {"lid": 8, "difficulty": "基础", "type": "词汇", "q": '"转账"是什么意思？', "opts": ["换账户", "将钱财从一个账户转到另一个", "删除账户"], "ans": "将钱财从一个账户转到另一个"},
        {"lid": 8, "difficulty": "提高", "type": "文化理解", "q": "关于移动支付的发展，以下说法不正确的是？", "opts": ["它改变了人们的消费方式", "它完全替代了现金", "它提高了交易效率"], "ans": "它完全替代了现金"},
    ])
    
    # 第9课 - 妈妈的退休生活
    questions.extend([
        {"lid": 9, "difficulty": "基础", "type": "词汇", "q": '"丰富"的意思是什么？', "opts": ["简单", "多样化、内容许多", "困难"], "ans": "多样化、内容许多"},
        {"lid": 9, "difficulty": "基础", "type": "文化", "q": "广场舞在中国社会的作用主要是什么？", "opts": ["赚钱", "娱乐和社交活动", "竞争"], "ans": "娱乐和社交活动"},
        {"lid": 9, "difficulty": "提高", "type": "社会理解", "q": "老龄化社会的到来对年轻人意味着什么？", "opts": ["没有影响", "需要承担更多社会责任", "生活变得更轻松"], "ans": "需要承担更多社会责任"},
    ])
    
    # 第10课 - 实习不是打杂儿
    questions.extend([
        {"lid": 10, "difficulty": "基础", "type": "词汇", "q": '"打杂"是什么意思？', "opts": ["打破东西", "做琐碎的低价值工作", "打游戏"], "ans": "做琐碎的低价值工作"},
        {"lid": 10, "difficulty": "基础", "type": "文化", "q": "实习的真正意义是什么？", "opts": ["免费工作", "获得实践经验和专业发展", "打发时间"], "ans": "获得实践经验和专业发展"},
        {"lid": 10, "difficulty": "提高", "type": "语言运用", "q": "以下哪个句子最准确地表达了实习的价值？", "opts": ["实习就是做家务", "实习是参与真实项目、学习专业知识的机会", "实习只是为了赚钱"], "ans": "实习是参与真实项目、学习专业知识的机会"},
    ])
    
    # 第11课 - 无声的蛋糕店
    questions.extend([
        {"lid": 11, "difficulty": "基础", "type": "词汇", "q": '"尊重"是什么意思？', "opts": ["害怕", "尊敬、尊重他人", "嘲笑"], "ans": "尊敬、尊重他人"},
        {"lid": 11, "difficulty": "基础", "type": "文化", "q": "无声蛋糕店想要表达什么理念？", "opts": ["蛋糕很贵", "聋哑人也能自我拯救、为社会做贡献", "蛋糕不好吃"], "ans": "聋哑人也能自我拯救、为社会做贡献"},
        {"lid": 11, "difficulty": "提高", "type": "社会理解", "q": "社会应该如何对待残疾人群体？", "opts": ["完全排斥他们", "给予尊重和平等的机会", "过度怜悯"], "ans": "给予尊重和平等的机会"},
    ])
    
    # 第12课 - 越来越淡的年味儿
    questions.extend([
        {"lid": 12, "difficulty": "基础", "type": "词汇", "q": '"习俗"是什么意思？', "opts": ["坏习惯", "社会传统活动", "新发明"], "ans": "社会传统活动"},
        {"lid": 12, "difficulty": "基础", "type": "文化", "q": "以下哪个是中国春节的传统活动？", "opts": ["冲浪", "放鞭炮、贴春联", "登山"], "ans": "放鞭炮、贴春联"},
        {"lid": 12, "difficulty": "提高", "type": "文化分析", "q": '题目"越来越淡的年味儿"反映了什么社会现象？', "opts": ["春节变得更隆重了", "传统节日的庆祝方式在改变", "人们不再庆祝春节"], "ans": "传统节日的庆祝方式在改变"},
    ])
    
    # 第13课 - 孩子的零花钱
    questions.extend([
        {"lid": 13, "difficulty": "基础", "type": "词汇", "q": '"理财"是什么意思？', "opts": ["花钱", "管理和计划金钱", "借钱"], "ans": "管理和计划金钱"},
        {"lid": 13, "difficulty": "基础", "type": "教育", "q": "给孩子零花钱的主要目的是什么？", "opts": ["让孩子买东西", "培养理财和自主的能力", "浪费钱"], "ans": "培养理财和自主的能力"},
        {"lid": 13, "difficulty": "提高", "type": "语言运用", "q": '理解"惯"的意思："父母不应该惯孩子"中，"惯"的意思最接近？', "opts": ["习惯", "溺爱、纵容", "陪伴"], "ans": "溺爱、纵容"},
    ])
    
    # 第14课 - 我想搬出去住
    questions.extend([
        {"lid": 14, "difficulty": "基础", "type": "词汇", "q": '"合租"是什么意思？', "opts": ["单独租房", "几个人一起租一套房子", "免费住房"], "ans": "几个人一起租一套房子"},
        {"lid": 14, "difficulty": "基础", "type": "生活", "q": "租房时通常需要支付哪些费用？", "opts": ["只有房租", "房租和押金", "不需要付钱"], "ans": "房租和押金"},
        {"lid": 14, "difficulty": "提高", "type": "成人独立", "q": "想要搬出去住通常反映了什么生活阶段的变化？", "opts": ["逃离家庭", "向成人独立迈进", "被赶出来"], "ans": "向成人独立迈进"},
    ])
    
    return questions

QUIZ_DATA = get_quiz_data()

# (6) 成就徽章系统
ACHIEVEMENT_BADGES = {
    "快速学习者": {"条件": "连续完成3课", "图标": "⚡", "积分": 50},
    "问题解决者": {"条件": "题库实战满分", "图标": "🎯", "积分": 100},
    "文化使者": {"条件": "完成5课预习任务", "图标": "🌍", "积分": 75},
    "全能选手": {"条件": "14课全部掌握", "图标": "👑", "积分": 500},
    "视频迷": {"条件": "观看5个竞赛视频", "图标": "📺", "积分": 30},
    "词汇大师": {"条件": "掌握100个词汇", "图标": "📚", "积分": 200},
    "任务完成者": {"条件": "提交10个课后任务", "图标": "✅", "积分": 150},
}

# ==========================================
# 3. 界面逻辑
# ==========================================

# 侧边栏导航
with st.sidebar:
    st.header("🏆 以赛促学 V15.1")
    st.info("数据源：TCFL_V15_1_Accurate_Vocab")
    
    menu = st.radio(
        "导航菜单",
        ["🔖 课前预习", "🏠 赛事资讯", "📖 重点词汇", "📺 竞赛视频", "✍️ 题库实战", "📂 课件资源", "📝 课后任务", "📊 评价系统"]
    )
    st.divider()
    st.caption("Designed by Wang Yuan")

# --- 0. 课前预习 ---
if menu == "🔖 课前预习":
    st.title("🔖 课前预习中心")
    st.info("📚 这里展示所有课程内容，帮助您课前快速预习")
    
    # 课程列表
    for idx, title, topic in LESSONS_DATA:
        with st.expander(f"💡 第 {idx} 课：{title}（{topic}）", expanded=(idx==1)):
            # 课程信息卡
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**📌 课程主题：** {topic}")
            with col2:
                st.markdown(f"**📚 课程标题：** {title}")
            
            st.divider()
            
            # 词汇预览
            if idx in VOCAB_MAP:
                st.subheader("📖 词汇预览")
                vocab_list = VOCAB_MAP[idx]
                
                # 显示该课的所有词汇
                for word, pinyin, mean, tag in vocab_list:
                    with st.container():
                        c1, c2, c3, c4 = st.columns([1.5, 1.5, 1, 0.8])
                        with c1:
                            st.markdown(f"**{word}**")
                        with c2:
                            st.markdown(f"*{pinyin}*")
                        with c3:
                            st.markdown(f"_{mean}_")
                        with c4:
                            # 发音按钮
                            if st.button(f"🔊", key=f"audio_preview_{idx}_{word}", use_container_width=True):
                                play_audio(word, f"preview_{idx}_{word}")
                        st.caption(f"📌 {tag}")
                        st.divider()
            else:
                st.info("本课节词汇资料待更新")
            
            # 课程背景知识与预习任务
            st.divider()
            if idx in BACKGROUND_KNOWLEDGE:
                bg = BACKGROUND_KNOWLEDGE[idx]
                
                # 背景知识
                with st.container():
                    st.subheader("🎓 课程背景知识")
                    st.info(bg["背景"])
                
                # 学习要点
                st.subheader("✨ 学习要点")
                for point in bg["学习要点"]:
                    st.markdown(f"• {point}")
                
                st.divider()
                
                # 预习任务
                st.subheader("📋 课前预习任务")
                st.warning(f"📝 {bg['预习任务']}")
                
                # 任务提交区域
                with st.form(f"preview_task_{idx}", clear_on_submit=True):
                    user_input = st.text_area("你的预习笔记：", placeholder="请记录你的思考和发现...", height=100, key=f"preview_{idx}")
                    submitted = st.form_submit_button("💾 保存笔记", use_container_width=True)
                    
                    if submitted and user_input:
                        st.success(f"✅ 第{idx}课的预习笔记已保存！")
                        st.balloons()

# --- 1. 赛事资讯 ---
if menu == "🏠 赛事资讯":
    st.title("📢 赛事与考试资讯")
    for news in NEWS_DATA:
        # 点击跳转：优先使用条目中的 'url'，否则构造搜索链接作为后备
        target_url = news.get('url') if news.get('url') else f"https://www.bing.com/search?q={quote_plus(news['title'])}"
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**{news['date']}**")
                # 将来源也做为可点击项（当有 url 时指向原文）
                if news.get('url'):
                    st.caption(f"来源： {news['source']}")
                else:
                    st.caption(news['source'])
            with col2:
                # 标题作为可点击链接，安全打开新标签
                st.markdown(f"##### <a href='{target_url}' target='_blank' rel='noopener noreferrer'>{news['title']}</a>", unsafe_allow_html=True)
                st.markdown(f"<span style='background:#e0f7fa;padding:2px 8px;border-radius:4px;font-size:12px'>{news['type']}</span>", unsafe_allow_html=True)
                # 当条目本身没有明确 url 时，展示一个“搜索原文”的小链接
                if not news.get('url'):
                    st.markdown(f"<div style='margin-top:4px'><a href='{target_url}' target='_blank' rel='noopener noreferrer' style='font-size:12px'>🔎 在搜索中查找原文</a></div>", unsafe_allow_html=True)
            st.divider()

# --- 2. 重点词汇 (核心功能) ---
elif menu == "📖 重点词汇":
    st.title("📖 全书词汇表 (精准版)")
    
    # 课程选择器
    lesson_options = ["全部显示"] + [f"第{i}课: {t}" for i, t, topic in LESSONS_DATA]
    selected_option = st.selectbox("选择课程章节", lesson_options)
    
    # 提取 Lesson ID
    selected_lid = None
    if selected_option != "全部显示":
        selected_lid = int(selected_option.split("课")[0].replace("第", ""))

    # 遍历并展示
    count = 0
    for lid, vocab_list in VOCAB_MAP.items():
        if selected_lid is None or selected_lid == lid:
            # 获取课程信息
            lesson_info = next((item for item in LESSONS_DATA if item[0] == lid), None)
            st.subheader(f"第 {lid} 课：{lesson_info[1]}")
            
            # 使用 DataFrame 展示，或者卡片展示
            # 这里为了手机端体验，使用类似卡片的布局
            for word, pinyin, mean, tag in vocab_list:
                count += 1
                with st.container():
                    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.2, 0.8])
                    with c1:
                        st.markdown(f"**{word}**")
                    with c2:
                        st.markdown(f"*{pinyin}*")
                    with c3:
                        st.write(f"📝 {mean}")
                    with c4:
                        # 发音按钮
                        if st.button(f"🔊", key=f"audio_vocab_{lid}_{word}", use_container_width=True):
                            play_audio(word, f"vocab_{lid}_{word}")
                    st.markdown(f"<div style='text-align:right'><span style='background:#fff3cd;padding:4px;border-radius:4px;'>{tag}</span></div>", unsafe_allow_html=True)
                    st.divider()
    
    if count == 0:
        st.warning("本章节暂无重点词汇数据。")

# --- 3. 竞赛视频 ---
elif menu == "📺 竞赛视频":
    st.title("📺 视频资源库")
    
    # 创建两个分栏：精选资源 和 学生成果展示
    tab1, tab2 = st.tabs(["✨ 精选资源", "🎓 学生成果展示"])
    
    with tab1:
        st.caption("精选 Bilibili 教学与竞赛资源")
        
        cols = st.columns(1) # 手机端单列显示
        for v in VIDEO_DATA:
            with st.expander(f"▶️ {v['title']} ({v['cat']})"):
                st.write(v['desc'])
                st.link_button("点击跳转观看", v['url'])
    
    with tab2:
        st.caption("🌟 我们优秀学生的竞赛成果展示")
        st.divider()
        
        for idx, vid in enumerate(STUDENT_VIDEO_DATA):
            with st.container():
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    st.markdown(f"<div style='padding:10px; background:{vid['color']}; border-radius:8px; text-align:center; color:white;'><b>🏆</b></div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"### 🎬 {vid['title']}")
                    st.markdown(f"*{vid['desc']}*")
                    st.link_button("观看视频", vid['url'], use_container_width=True)
                
                # 观后感评论框
                st.markdown("#### 💬 分享你的观后感")
                comment = st.text_area(
                    "你的评论：",
                    placeholder="请分享你对这个作品的想法和感受...",
                    height=80,
                    key=f"student_comment_{idx}_{vid['title']}"
                )
                
                if comment:
                    # 添加提交按钮
                    col_submit1, col_submit2 = st.columns([1, 3])
                    with col_submit1:
                        if st.button("📝 提交评论", key=f"submit_btn_{idx}_{vid['title']}"):
                            st.success("✅ 感谢你的评论！")
                
                st.divider()

# --- 4. 题库实战 ---
elif menu == "✍️ 题库实战":
    st.title("✍️ 竞赛题库实战")
    
    # 难度筛选
    difficulty_filter = st.radio("选择难度级别", ["全部", "基础", "提高"], horizontal=True)
    
    # 按难度筛选题目
    filtered_quiz = QUIZ_DATA
    if difficulty_filter != "全部":
        filtered_quiz = [q for q in QUIZ_DATA if q.get("difficulty") == difficulty_filter]
    
    # 显示统计信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总题数", len(filtered_quiz))
    with col2:
        st.metric("基础题", len([q for q in QUIZ_DATA if q.get("difficulty") == "基础"]))
    with col3:
        st.metric("提高题", len([q for q in QUIZ_DATA if q.get("difficulty") == "提高"]))
    
    st.divider()
    
    if len(filtered_quiz) == 0:
        st.warning("没有符合条件的题目")
    else:
        with st.form("quiz_main"):
            score = 0
            total = len(filtered_quiz)
            
            for i, q in enumerate(filtered_quiz):
                # 题目头部：显示课程、难度、题型
                difficulty_badge = "⭐" if q.get("difficulty") == "基础" else "⭐⭐"
                st.markdown(f"**第 {i+1} 题** | 第{q['lid']}课 | {difficulty_badge} | [{q['type']}]")
                st.markdown(f"### {q['q']}")
                
                # 选项单选
                user_ans = st.radio("请选择:", q['opts'], key=f"q_{q['lid']}_{i}", index=None, label_visibility="collapsed")
                st.divider()
            
            submitted = st.form_submit_button("📊 提交答卷", use_container_width=True)
            
            if submitted:
                correct = 0
                errors = []
                
                for i, q in enumerate(filtered_quiz):
                    u_ans = st.session_state.get(f"q_{q['lid']}_{i}")
                    if u_ans == q['ans']:
                        correct += 1
                    else:
                        errors.append({
                            "num": i + 1,
                            "question": q['q'],
                            "your_ans": u_ans if u_ans else "未作答",
                            "correct_ans": q['ans']
                        })
                
                final_score = int(correct / total * 100) if total > 0 else 0
                
                # 成绩展示
                st.divider()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("你的得分", f"{final_score} 分", f"{correct}/{total}")
                with col2:
                    accuracy = int(correct / total * 100) if total > 0 else 0
                    st.metric("准确率", f"{accuracy}%")
                with col3:
                    if final_score >= 80:
                        st.metric("评价", "优秀 🎉")
                    elif final_score >= 60:
                        st.metric("评价", "及格 ✓")
                    else:
                        st.metric("评价", "需努力")
                
                # 错题详解
                if errors:
                    st.warning(f"您有 {len(errors)} 题答错了，请查看以下详解：")
                    st.divider()
                    for err in errors:
                        with st.expander(f"❌ 第 {err['num']} 题：{err['question'][:40]}..."):
                            st.markdown(f"**❌ 你的答案：** {err['your_ans']}")
                            st.markdown(f"**✅ 正确答案：** {err['correct_ans']}")
                else:
                    st.success("🎉 完美！所有题目都答对了！")
                    st.balloons()

# --- 5. 课件资源 ---
elif menu == "📂 课件资源":
    st.title("📂 教学资源下载")

    uploads_dir = "uploads"
    file_list = []

    # 优先读取仓库中的 uploads/ 目录（用户将课件放在此处）
    if os.path.isdir(uploads_dir):
        files = sorted(os.listdir(uploads_dir))
        for fname in files:
            fpath = os.path.join(uploads_dir, fname)
            if os.path.isfile(fpath):
                size_kb = max(1, os.path.getsize(fpath) // 1024)
                ext = os.path.splitext(fname)[1].lstrip('.').upper() or 'File'
                # 课程列保留为文件名的前缀（若命名包含“第N课”则保留，否则空）
                lesson_label = fname.split('_')[0] if '_' in fname else ''
                file_list.append([lesson_label, fname, ext, f"{size_kb}KB", fpath])

    # 如果 uploads 为空或不存在，回退到原先的演示性生成逻辑
    if not file_list:
        for idx, title, topic in LESSONS_DATA:
            file_list.append([f"第{idx}课", f"第{idx}课_{topic}_教学课件.pptx", "PPT", "5MB", None])
            file_list.append([f"第{idx}课", f"第{idx}课_{topic}_课文录音.mp3", "音频", "3MB", None])
            file_list.append([f"第{idx}课", f"第{idx}课_{topic}_生词表.docx", "文档", "1MB", None])

    df_files = pd.DataFrame(file_list, columns=["课程", "文件名", "类型", "大小", "_path"])
    st.dataframe(df_files.drop(columns=['_path']), hide_index=True, use_container_width=True)

    # 为每个文件提供单独的下载按钮（仅当文件已上传到 uploads/ 时）
    for row in file_list:
        lesson, fname, ftype, fsize, fpath = row
        cols = st.columns([4, 1, 1])
        with cols[0]:
            st.write(f"**{fname}** — {lesson}")
        with cols[1]:
            st.write(f"{ftype} · {fsize}")
        with cols[2]:
            if fpath and os.path.isfile(fpath):
                try:
                    with open(fpath, 'rb') as _f:
                        data = _f.read()
                    st.download_button(label="⬇️ 下载", data=data, file_name=fname, mime='application/octet-stream')
                except Exception as e:
                    st.warning(f"无法读取文件：{fname}")
            else:
                st.button("⬇️ 演示下载", disabled=True)

# --- 6. 课后任务 ---
elif menu == "📝 课后任务":
    st.title("📝 产出任务 (Output)")
    
    task_actions = ['演讲', '采访', '写作', '辩论', '角色扮演']
    
    for idx, title, topic in LESSONS_DATA:
        # 简单模拟原代码中的随机任务生成逻辑，但为了展示固定下来
        action = task_actions[idx % 5] 
        with st.expander(f"第 {idx} 课：{topic} ({action})"):
            st.info(f"截止日期：2025-06-30")
            st.write(f"任务描述：结合本课所学词汇，完成关于“{topic}”的{action}，并在此提交作品。")
            st.file_uploader("上传作业", key=f"up_{idx}")

# --- 7. 评价系统 ---
elif menu == "📊 评价系统":
    st.title("📊 学习者画像")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("词汇掌握度", "85%", "+5%")
    with col2:
        st.metric("任务完成率", "92%", "+2%")
        
    st.subheader("📋 教师评语")
    st.markdown("---")
    
    # 教师信息和评语
    with st.container():
        col_teacher = st.columns([1, 3])
        with col_teacher[0]:
            st.markdown("**👩‍🏫 教师**")
            st.write("王媛")
        with col_teacher[1]:
            st.markdown("**📝 评语**")
            st.write("该生在\"移动支付\"和\"网购\"话题上表现出色，掌握词汇运用能力强。建议加强\"传统文化\"部分的学习，深化对文化内涵的理解。继续努力！")
    
    st.markdown("---")
    st.caption("📅 评价日期：2026-02-12")


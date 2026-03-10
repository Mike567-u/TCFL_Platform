import streamlit as st
import pandas as pd
import random
from datetime import datetime
from urllib.parse import quote_plus
import os

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

# (5) 动态生成题库 (逻辑移植)
def get_quiz_data():
    questions = []
    for idx, title, topic in LESSONS_DATA:
        if idx == 4:
            questions.append({"lid": idx, "type": "文化", "q": "为什么中国人忌讳用筷子敲碗？", "opts": ["不卫生", "像乞丐要饭", "容易打破碗"], "ans": "像乞丐要饭"})
        elif idx == 8:
            questions.append({"lid": idx, "type": "听力", "q": "记者采访中，受访者认为移动支付最大的风险是？", "opts": ["没电", "隐私泄露", "操作复杂"], "ans": "隐私泄露"})
        elif idx == 3:
            questions.append({"lid": idx, "type": "常识", "q": "泼水节是哪个民族的传统节日？", "opts": ["汉族", "傣族", "回族"], "ans": "傣族"})
        else:
            questions.append({"lid": idx, "type": "阅读", "q": f"关于“{topic}”，下列说法正确的是？", "opts": ["完全支持", "辩证看待", "坚决反对"], "ans": "辩证看待"})
    return questions

QUIZ_DATA = get_quiz_data()

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
                        c1, c2, c3 = st.columns([2, 2, 1])
                        with c1:
                            st.markdown(f"**{word}**")
                        with c2:
                            st.markdown(f"*{pinyin}*")
                        with c3:
                            st.markdown(f"_{mean}_")
                        st.caption(f"📌 分类：{tag}")
                        st.divider()
            else:
                st.info("本课节词汇资料待更新")

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
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{word}** ({pinyin})")
                        st.write(f"📝 {mean}")
                    with c2:
                        st.markdown(f"<div style='text-align:right'><span style='background:#fff3cd;padding:4px;border-radius:4px;'>{tag}</span></div>", unsafe_allow_html=True)
                    st.divider()
    
    if count == 0:
        st.warning("本章节暂无重点词汇数据。")

# --- 3. 竞赛视频 ---
elif menu == "📺 竞赛视频":
    st.title("📺 视频资源库")
    st.caption("精选 Bilibili 教学与竞赛资源")
    
    cols = st.columns(1) # 手机端单列显示
    for v in VIDEO_DATA:
        with st.expander(f"▶️ {v['title']} ({v['cat']})"):
            st.write(v['desc'])
            st.link_button("点击跳转观看", v['url'])

# --- 4. 题库实战 ---
elif menu == "✍️ 题库实战":
    st.title("✍️ 每日一练")
    st.progress(0, text="当前进度")
    
    with st.form("quiz_main"):
        score = 0
        total = len(QUIZ_DATA)
        
        for i, q in enumerate(QUIZ_DATA):
            st.markdown(f"**{i+1}. [{q['type']}] {q['q']}**")
            # 唯一的 key 避免冲突
            user_ans = st.radio("请选择:", q['opts'], key=f"q_{i}", index=None)
            st.divider()
            
        submitted = st.form_submit_button("提交试卷")
        
        if submitted:
            correct = 0
            for i, q in enumerate(QUIZ_DATA):
                u_ans = st.session_state.get(f"q_{i}")
                if u_ans == q['ans']:
                    correct += 1
                else:
                    st.error(f"第 {i+1} 题错误。正确答案：{q['ans']}")
            
            final_score = int(correct / total * 100)
            st.metric("你的得分", f"{final_score} 分")
            if final_score == 100:
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

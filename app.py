import streamlit as st
import pandas as pd
import random
from datetime import datetime

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
    {'type': '重磅', 'title': '教育部：2025年世界中文大会将在北京召开', 'date': '2025-11-15', 'source': '教育部官网'},
    {'type': '赛事', 'title': '第24届“汉语桥”世界大学生中文比赛海外预赛启动', 'date': '2025-03-20', 'source': '汉语桥组委会'},
    {'type': '考试', 'title': '2025年 HSK、HSKK 考试日程表发布', 'date': '2025-01-05', 'source': '汉考国际'},
    {'type': '活动', 'title': '“国际中文日”：共绘中外文明交流互鉴新画卷', 'date': '2025-04-20', 'source': '语合中心'},
    {'type': '奖学金', 'title': '2025年国际中文教师奖学金申请办法', 'date': '2025-03-01', 'source': 'CLEC'}
]

# (4) 竞赛视频
VIDEO_DATA = [
    {'cat': '汉语桥', 'title': '第21届“汉语桥”总决赛：天下一家', 'desc': '感受全球中文高手的巅峰对决。', 'url': 'https://www.bilibili.com/video/BV1Rd4y1B7hB', 'color': '#e74c3c'},
    {'cat': '经典诵读', 'title': '中华经典诵读大赛：《将进酒》', 'desc': '气势磅礴的唐诗朗诵示范。', 'url': 'https://www.bilibili.com/video/BV1Rs411X7na', 'color': '#3498db'},
    {'cat': '短视频', 'title': 'HSK短视频大赛金奖：我的中国故事', 'desc': '用镜头记录真实的留学生活。', 'url': 'https://www.bilibili.com/video/BV1XK4y1t7Xn', 'color': '#9b59b6'},
    {'cat': '教学示范', 'title': '《新时代汉语口语》名师示范课', 'desc': '北语名师讲解口语表达技巧。', 'url': 'https://www.bilibili.com/video/BV1Wt411v7Vj', 'color': '#2ecc71'},
    {'cat': '文化体验', 'title': '李子柒：中国非遗文化之美', 'desc': '深度体验中国传统手工技艺。', 'url': 'https://www.bilibili.com/video/BV1bb411r7Fp', 'color': '#f1c40f'}
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
        ["🏠 赛事资讯", "📖 重点词汇", "📺 竞赛视频", "✍️ 题库实战", "📂 课件资源", "📝 课后任务", "📊 评价系统"]
    )
    st.divider()
    st.caption("Designed by Wang Yuan")

# --- 1. 赛事资讯 ---
if menu == "🏠 赛事资讯":
    st.title("📢 赛事与考试资讯")
    for news in NEWS_DATA:
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**{news['date']}**")
                st.caption(news['source'])
            with col2:
                st.markdown(f"##### {news['title']}")
                st.markdown(f"<span style='background:#e0f7fa;padding:2px 8px;border-radius:4px;font-size:12px'>{news['type']}</span>", unsafe_allow_html=True)
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
    
    # 动态生成文件列表数据
    file_list = []
    for idx, title, topic in LESSONS_DATA:
        file_list.append([f"第{idx}课", f"第{idx}课_{topic}_教学课件.pptx", "PPT", "5MB"])
        file_list.append([f"第{idx}课", f"第{idx}课_{topic}_课文录音.mp3", "音频", "3MB"])
        file_list.append([f"第{idx}课", f"第{idx}课_{topic}_生词表.docx", "文档", "1MB"])
    
    df_files = pd.DataFrame(file_list, columns=["课程", "文件名", "类型", "大小"])
    st.dataframe(df_files, hide_index=True, use_container_width=True)
    st.button("⬇️ 批量下载 (演示)")

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
        
    st.subheader("能力雷达图")
    # 简单的模拟数据
    chart_data = pd.DataFrame(dict(
        r=[85, 90, 70, 80, 95],
        theta=['词汇','语法','文化','口语','任务']
    ))
    st.write("（此处为雷达图占位，Streamlit 需安装 plotly 库显示复杂图表，为保持极简暂用文本描述）")
    st.info("导师评语：该生在“移动支付”和“网购”话题上表现出色，建议加强“传统文化”部分的学习。")
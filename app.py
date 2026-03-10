import streamlit as st
import sqlite3
import random
import string

# ==========================================
# 1. 数据库初始化 (包含完整角色阵营)
# ==========================================
def init_db():
    conn = sqlite3.connect('campus_event.db')
    c = conn.cursor()
    
    # 兑换码表
    c.execute('''CREATE TABLE IF NOT EXISTS codes
                 (code TEXT PRIMARY KEY, is_used INTEGER)''')
    
    # 盲盒库存表
    c.execute('''CREATE TABLE IF NOT EXISTS boxes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  npc TEXT, 
                  content TEXT, 
                  is_drawn INTEGER)''')
    
    # 初始化一些测试数据
    c.execute("SELECT COUNT(*) FROM codes")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO codes (code, is_used) VALUES (?, ?)", 
                      [('VIP2026', 0), ('TEST888', 0)])
        
        # 初始化六大阵营的初始盲盒
        boxes_data = [
            ('Cooper (情报掮客)', '一份极其罕见的期末复习资料汇总...', 0),
            ('Eggo (淘金客)', '运气不错！这是一张食堂免费大鸡腿券，请截图找工作人员核销。', 0),
            ('Alice (落魄贵族)', '这件真丝衬衫是我最后的倔强，希望它的下一个主人能好好对待它...', 0),
            ('Bob (退伍老兵)', '我的旧战靴走过很多路，现在交给你了。周末有空一起去操场跑圈吗？', 0),
            ('Flash (投机向导)', '前方高能！发现一个隐秘的校园天台打卡点，坐标在这...', 0),
            ('David (破产父亲)', '这几本旧书是我以前买给孩子的，他长大了，送给需要的人吧。', 0)
        ]
        c.executemany("INSERT INTO boxes (npc, content, is_drawn) VALUES (?, ?, ?)", boxes_data)
        
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. 状态初始化
# ==========================================
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'box_result' not in st.session_state:
    st.session_state.box_result = ""

# ==========================================
# 3. 侧边栏：账户与核销区
# ==========================================
st.sidebar.title("♻️ 焕新计划")
st.sidebar.header("🪙 我的账户")
st.sidebar.info(f"当前可用积分：**{st.session_state.points}** 分")

code_input = st.sidebar.text_input("输入捐衣兑换码：", placeholder="例如: VIP2026")
if st.sidebar.button("兑换积分"):
    if code_input:
        conn = sqlite3.connect('campus_event.db')
        c = conn.cursor()
        c.execute("SELECT is_used FROM codes WHERE code=?", (code_input,))
        result = c.fetchone()
        
        if result is None:
            st.sidebar.error("❌ 兑换码不存在！")
        elif result[0] == 1:
            st.sidebar.warning("⚠️ 此兑换码已被使用！")
        else:
            c.execute("UPDATE codes SET is_used=1 WHERE code=?", (code_input,))
            conn.commit()
            st.session_state.points += 50
            st.session_state.box_result = "" 
            st.sidebar.success("🎉 兑换成功！积分 +50")
            st.rerun()
        conn.close()

st.sidebar.markdown("---")
st.sidebar.caption("提示：每捐赠1kg衣物可找工作人员领取1个兑换码。")

# ==========================================
# 4. 页面主体：三大功能分页
# ==========================================
tab1, tab2, tab3 = st.tabs(["🎁 开启盲盒", "✍️ 存入盲盒", "⚙️ 后台管理"])

# ----------------- Tab 1: 抽取盲盒 -----------------
with tab1:
    st.markdown("### 选择你要接触的神秘人物（每次消耗10积分）")
    
    def draw_box(npc_name):
        if st.session_state.points < 10:
            st.error("积分不足！去线下捐赠旧衣获取兑换码吧。")
            return
            
        conn = sqlite3.connect('campus_event.db')
        c = conn.cursor()
        c.execute("SELECT id, content FROM boxes WHERE npc=? AND is_drawn=0", (npc_name,))
        available_boxes = c.fetchall()
        
        if not available_boxes:
            st.warning(f"😭 【{npc_name}】的库存已被抽空，去看看别人吧！")
        else:
            st.session_state.points -= 10
            chosen_box = random.choice(available_boxes)
            c.execute("UPDATE boxes SET is_drawn=1 WHERE id=?", (chosen_box[0],))
            conn.commit()
            st.session_state.box_result = chosen_box[1]
            st.rerun()
        conn.close()

    # 两行三列排布六个角色
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👑 Alice\n(落魄贵族)", use_container_width=True): draw_box('Alice (落魄贵族)')
        if st.button("🪖 Bob\n(退伍老兵)", use_container_width=True): draw_box('Bob (退伍老兵)')
    with col2:
        if st.button("🕵️ Cooper\n(情报掮客)", use_container_width=True): draw_box('Cooper (情报掮客)')
        if st.button("💼 David\n(破产父亲)", use_container_width=True): draw_box('David (破产父亲)')
    with col3:
        if st.button("💰 Eggo\n(淘金客)", use_container_width=True): draw_box('Eggo (淘金客)')
        if st.button("🗺️ Flash\n(投机向导)", use_container_width=True): draw_box('Flash (投机向导)')

    if st.session_state.box_result:
        st.markdown("---")
        st.success("🎉 抽取成功！这是留给你的信息：")
        with st.container(border=True):
            st.write(st.session_state.box_result)

# ----------------- Tab 2: 存入盲盒 -----------------
with tab2:
    st.markdown("### 留下你的足迹，将盲盒投入奖池")
    st.info("💡 你可以在这里留下给陌生人的祝福、推荐一首歌、或者挂个求助/组队信息。")
    
    npc_choices = ['Alice (落魄贵族)', 'Bob (退伍老兵)', 'Cooper (情报掮客)', 'David (破产父亲)', 'Eggo (淘金客)', 'Flash (投机向导)']
    selected_npc = st.selectbox("选择由哪位NPC来保管你的盲盒：", npc_choices)
    
    user_content = st.text_area("盲盒内容（支持放入链接）：", height=150)
    
    if st.button("📥 封存盲盒，投入奖池"):
        if len(user_content.strip()) < 5:
            st.warning("字数太少啦，多写点什么吧！")
        else:
            conn = sqlite3.connect('campus_event.db')
            c = conn.cursor()
            c.execute("INSERT INTO boxes (npc, content, is_drawn) VALUES (?, ?, 0)", (selected_npc, user_content))
            conn.commit()
            conn.close()
            st.success("✨ 盲盒已成功封存！感谢你为这个校园故事添砖加瓦。")

# ----------------- Tab 3: 后台管理 (仅供负责人) -----------------
with tab3:
    st.markdown("### 🔑 活动负责人专用：生成兑换码")
    st.caption("线下收到旧衣后，将生成的兑换码发给同学即可。")
    
    if st.button("⚙️ 一键生成 5 个新兑换码"):
        conn = sqlite3.connect('campus_event.db')
        c = conn.cursor()
        new_codes = []
        for _ in range(5):
            # 生成6位随机大写字母+数字的兑换码
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            new_codes.append(code)
            c.execute("INSERT INTO codes (code, is_used) VALUES (?, 0)", (code,))
        conn.commit()
        conn.close()
        st.success("生成成功！最新批次的码如下：")
        for idx, code in enumerate(new_codes):
            st.code(code)
            
    st.markdown("---")
    # 查看当前有多少未被抽走的盲盒
    conn = sqlite3.connect('campus_event.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM boxes WHERE is_drawn=0")
    remain_boxes = c.fetchone()[0]
    conn.close()
    st.metric(label="当前奖池剩余盲盒总数", value=remain_boxes)

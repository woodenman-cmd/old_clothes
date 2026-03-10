import streamlit as st
import random

# ==========================================
# 1. 状态初始化（保证刷新网页后积分不丢失）
# ==========================================
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'box_result' not in st.session_state:
    st.session_state.box_result = ""

# ==========================================
# 2. 页面标题与侧边栏（个人账户区）
# ==========================================
st.title("♻️ 焕新计划：校园社交盲盒")
st.markdown("捐出闲置衣物，抽取专属你的校园奇遇！")

st.sidebar.header("🪙 我的账户")
st.sidebar.info(f"当前可用环保积分：**{st.session_state.points}** 分")

st.sidebar.markdown("---")
st.sidebar.subheader("获取积分")
code_input = st.sidebar.text_input("输入线下捐赠获取的兑换码：", placeholder="测试请输入 VIP2026")

if st.sidebar.button("兑换积分"):
    if code_input == "VIP2026":
        st.session_state.points += 50
        st.session_state.box_result = "" # 清空之前的抽奖结果
        st.sidebar.success("兑换成功！积分 +50")
        st.rerun()  # 刷新页面更新积分
    elif code_input != "":
        st.sidebar.error("无效的兑换码")

# ==========================================
# 3. 盲盒数据池（不用数据库，直接写死测试数据）
# ==========================================
# 情报盲盒：放一些硬核资料、学习相关的链接
cooper_boxes = [
    "🎓 **情报掉落**：[2026美赛(MCM/ICM) LaTeX排版速成指南](https://example.com/mcm)",
    "💻 **情报掉落**：[Streamlit 快速部署教程](https://example.com/deploy)",
    "📚 **情报掉落**：期末高数复习重点笔记.pdf (提取码: 1234)"
]

# 福利盲盒：放实体奖励或优惠券
eggo_boxes = [
    "🍗 **福利掉落**：恭喜抽中【食堂二楼免费大鸡腿券】1张！请截图找工作人员核销。",
    "☕ **福利掉落**：恭喜抽中【瑞幸9.9元代金券】一张！兑换码：RX99001",
    "😭 **福利掉落**：很遗憾，这个盲盒是空的。感谢你为环保做出的贡献！"
]

# 走心盲盒：放同学们的留言、故事
bob_boxes = [
    "💌 **走心留言**：这件格子衫陪我熬过了无数个Debug报Segmentation fault的夜晚，希望下一个主人代码永无Bug！",
    "💌 **走心留言**：周末有没有人一起去打球？想组个局，加V：Test_WeChat_001",
    "💌 **走心留言**：祝抽到这个盲盒的陌生人，今天也能遇到开心的事情！"
]

# 抽卡通用逻辑
def draw_box(box_type_name, data_pool):
    if st.session_state.points >= 10:
        st.session_state.points -= 10  # 扣除积分
        # 随机从列表里抽一条数据
        st.session_state.box_result = random.choice(data_pool)
        st.rerun()
    else:
        st.error(f"积分不足！抽取【{box_type_name}】需要 10 积分。")

# ==========================================
# 4. 主页面：三大盲盒抽取区
# ==========================================
st.write("### 🎁 请选择你要开启的盲盒（每次消耗 10 积分）")

# 将页面分成三列，并排三个按钮，用 Emoji 代替图片
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🕵️\nCooper的情报箱\n(学习/干货)", use_container_width=True):
        draw_box("情报箱", cooper_boxes)

with col2:
    if st.button("💰\nEggo的福利袋\n(实物/优惠)", use_container_width=True):
        draw_box("福利袋", eggo_boxes)

with col3:
    if st.button("💌\nBob的旧信件\n(留言/交友)", use_container_width=True):
        draw_box("旧信件", bob_boxes)

st.markdown("---")

# ==========================================
# 5. 结果展示区
# ==========================================
if st.session_state.box_result:
    st.success("🎉 抽取成功！查看你的盲盒内容：")
    # 用一个好看的框把内容装起来
    with st.container(border=True):
        st.markdown(st.session_state.box_result)
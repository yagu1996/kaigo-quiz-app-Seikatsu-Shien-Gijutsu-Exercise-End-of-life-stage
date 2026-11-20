# -*- coding: utf-8 -*-
"""
Streamlit Quiz Application for Care Work Education (Chapter 6).
Features:
- Full ruby annotation on all kanji
- Class, Student ID, Name input
- Random 10, Topic-based, All 70 questions modes
- Instant feedback and textbook explanations
- Google Classroom submission generator and direct link
"""
import streamlit as st
import json
import random
import datetime
import hashlib
import os
import re

# Page config
st.set_page_config(
    page_title="生活支援技術 第6章 練習問題アプリ",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for cinematic warm tone, rubi styling, cards
def inject_custom_css(font_scale="標準"):
    font_size_map = {
        "標準": ("1.15rem", "0.58rem", "2.1"),
        "大": ("1.30rem", "0.65rem", "2.3"),
        "特大": ("1.48rem", "0.74rem", "2.5")
    }
    body_fs, rt_fs, lh = font_size_map.get(font_scale, font_size_map["標準"])
    
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@600;700&display=swap');
    
    html, body, [class*="css"], .stApp {{
        font-family: 'Noto Sans JP', sans-serif;
        color: #1e293b !important;
        background-color: #f8f9fa !important;
    }}
    
    p, span, div, label, li {{
        color: #1e293b;
    }}
    
    /* Ruby styling */
    ruby {{
        font-size: {body_fs};
        line-height: {lh};
        letter-spacing: 0.02em;
    }}
    
    rt {{
        font-size: {rt_fs};
        color: #576574;
        font-weight: 500;
        letter-spacing: 0.03em;
        user-select: none;
    }}
    
    /* Header Card */
    .app-header {{
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 50%, #4a6572 100%);
        padding: 24px 30px;
        border-radius: 14px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        border-left: 6px solid #e67e22;
    }}
    .app-header h1 {{
        color: #ffffff !important;
        font-family: 'Noto Serif JP', serif;
        font-size: 1.85rem !important;
        margin: 0 0 10px 0 !important;
        font-weight: 700;
    }}
    .app-header p {{
        color: #ecf0f1 !important;
        font-size: 0.95rem;
        margin: 0;
    }}
    
    /* Question Card */
    .question-card {{
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #3498db;
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }}
    .question-meta {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        color: #7f8c8d;
        font-size: 0.9rem;
        font-weight: 600;
    }}
    .topic-badge {{
        background-color: #ebf5fb;
        color: #2980b9;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
    }}
    
    /* Choice Container */
    .choice-card {{
        background-color: #fdfaf6;
        border: 2px solid #eddecb;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
        display: flex;
        align-items: flex-start;
        transition: all 0.2s ease;
    }}
    .choice-badge {{
        background-color: #d35400;
        color: white;
        font-weight: 700;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 14px;
        flex-shrink: 0;
        font-size: 0.95rem;
    }}
    .choice-text {{
        flex-grow: 1;
    }}
    
    /* Feedback card */
    .feedback-card {{
        padding: 20px 24px;
        border-radius: 12px;
        margin-top: 15px;
        margin-bottom: 20px;
    }}
    .feedback-correct {{
        background-color: #eafaf1;
        border: 2px solid #2ecc71;
    }}
    .feedback-incorrect {{
        background-color: #fdedec;
        border: 2px solid #e74c3c;
    }}
    
    /* Explanation Box */
    .explanation-box {{
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 18px 22px;
        border: 1px solid #dfe4ea;
        margin-top: 15px;
    }}
    
    /* Google Classroom block */
    .classroom-card {{
        background: linear-gradient(135deg, #1e7e34 0%, #28a745 100%);
        color: white;
        padding: 22px 26px;
        border-radius: 12px;
        margin-top: 25px;
        margin-bottom: 25px;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Load questions data
@st.cache_data
def load_questions():
    json_path = os.path.join(os.path.dirname(__file__), "questions.json")
    if not os.path.exists(json_path):
        # Fallback to local scratch path
        json_path = "/workspace/scratch/streamlit_care_app/questions.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Verification code generator
def generate_verification_code(student_id, student_class, score, total):
    raw = f"{student_id}_{student_class}_{score}_{total}_CARE_2026_SECRET"
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8].upper()
    return f"SEC-{student_id}-{student_class}-{score}OF{total}-{h}"

def main():
    questions_data = load_questions()
    
    # Sidebar
    st.sidebar.title("⚙️ 演習設定・学生情報")
    
    font_scale = st.sidebar.select_slider(
        "🔤 文字・ルビの大きさ",
        options=["標準", "大", "特大"],
        value="標準"
    )
    inject_custom_css(font_scale)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 受講者情報入力")
    
    student_class = st.sidebar.selectbox(
        "クラスを選択",
        options=["26A", "26B"],
        index=0
    )
    
    student_id = st.sidebar.text_input(
        "学籍番号（半角数字）",
        placeholder="例: 9269999",
        value=st.session_state.get("student_id", "")
    )
    
    student_name = st.sidebar.text_input(
        "氏名 / ニックネーム",
        placeholder="例: Your nickname",
        value=st.session_state.get("student_name", "")
    )
    
    st.session_state["student_class"] = student_class
    st.session_state["student_id"] = student_id
    st.session_state["student_name"] = student_name
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📚 演習モード選択")
    
    mode_options = [
        "1. ランダム10問演習（手軽に復習）",
        "2. テーマ別集中演習（分野ごとに学習）",
        "3. 全70問総合チャレンジ（総復習・模擬試験）"
    ]
    selected_mode = st.sidebar.radio("モードを選択してください", mode_options)
    
    selected_topic_id = None
    if selected_mode.startswith("2."):
        topic_list = [
            (1, "第1節 ケアの意義と意思決定支援（ACP等）"),
            (2, "第1節 全人的苦痛（トータルペイン）"),
            (3, "第1節 死の受容過程（5段階説）"),
            (4, "第2節 身体変化と日常生活支援（食事・排泄・清潔）"),
            (5, "第2節 苦痛の緩和とペインスケール・緩和ケア"),
            (6, "第2節 臨死期の兆候とケア・家族支援"),
            (7, "第2節 逝去後のケア（エンゼルケア・死亡診断）"),
            (8, "第3節 亡くなった後のケア・多職種連携")
        ]
        topic_choice = st.sidebar.selectbox(
            "演習するテーマを選択",
            topic_list,
            format_func=lambda x: x[1]
        )
        selected_topic_id = topic_choice[0]
        
    start_button = st.sidebar.button("🚀 演習を開始する / リセット", type="primary", use_container_width=True)
    
    # Initialize Quiz Session
    if "quiz_active" not in st.session_state or start_button:
        # Filter questions based on mode
        if selected_mode.startswith("1."):
            pool = list(questions_data)
            random.shuffle(pool)
            quiz_qs = pool[:10]
        elif selected_mode.startswith("2."):
            quiz_qs = [q for q in questions_data if q["topic_id"] == selected_topic_id]
        else:
            quiz_qs = list(questions_data)
            
        st.session_state["quiz_questions"] = quiz_qs
        st.session_state["current_idx"] = 0
        st.session_state["user_answers"] = {}
        st.session_state["answered_current"] = False
        st.session_state["quiz_active"] = True
        st.session_state["quiz_completed"] = False
        st.session_state["mode_name"] = selected_mode
        st.session_state["start_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if start_button:
            st.rerun()

    # Main Screen Header
    st.markdown("""
    <div class="app-header">
        <h1>No.7 生活支援技術 第6章 人生の最終段階における介護</h1>
        <p>介護福祉専門職のための演習・学習支援システム ｜ 全問題ルビ完全対応 ｜ Google Classroom 提出連携</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if student info is filled
    if not student_id.strip() or not student_name.strip():
        st.warning("⚠️ サイドバーで【学籍番号】と【氏名 / ニックネーム】を入力してください。入力すると演習結果をGoogle Classroomに提出できるようになります。")

    quiz_qs = st.session_state.get("quiz_questions", [])
    total_q = len(quiz_qs)
    curr_idx = st.session_state.get("current_idx", 0)
    completed = st.session_state.get("quiz_completed", False)
    
    if not quiz_qs:
        st.info("サイドバーの『🚀 演習を開始する』ボタンを押してください。")
        return
        
    # If completed, show results and Google Classroom submission block
    if completed or curr_idx >= total_q:
        st.session_state["quiz_completed"] = True
        render_results_screen(quiz_qs, student_class, student_id, student_name)
        return

    # Render Current Question
    current_q = quiz_qs[curr_idx]
    progress = (curr_idx + 1) / total_q
    
    st.progress(progress)
    
    # Question Card HTML
    q_html = f"""
    <div class="question-card">
        <div class="question-meta">
            <span>第 {curr_idx + 1} 問 / 全 {total_q} 問</span>
            <span class="topic-badge">{current_q["topic_name"]}</span>
        </div>
        <div style="font-size: 1.25rem; font-weight: 700; line-height: 2.2;">
            {current_q["question"]}
        </div>
    </div>
    """
    st.markdown(q_html, unsafe_allow_html=True)
    
    # Render Choices Cards
    choice_labels = ["A", "B", "C", "D"]
    for i, choice_text in enumerate(current_q["choices"]):
        c_html = f"""
        <div class="choice-card">
            <div class="choice-badge">{choice_labels[i]}</div>
            <div class="choice-text">{choice_text}</div>
        </div>
        """
        st.markdown(c_html, unsafe_allow_html=True)
        
    answered = st.session_state.get("answered_current", False)
    
    if not answered:
        st.markdown("##### 📌 あなたの回答を選択してください：")
        col_btns = st.columns(4)
        for i in range(4):
            with col_btns[i]:
                if st.button(f"選択肢 {choice_labels[i]} を回答", key=f"ans_btn_{curr_idx}_{i}", use_container_width=True, type="secondary"):
                    st.session_state["user_answers"][curr_idx] = i
                    st.session_state["answered_current"] = True
                    st.rerun()
    else:
        # Show Feedback
        user_choice = st.session_state["user_answers"].get(curr_idx)
        correct_idx = current_q["answer_index"]
        is_correct = (user_choice == correct_idx)
        
        if is_correct:
            st.markdown(f"""
            <div class="feedback-card feedback-correct">
                <h3 style="color: #27ae60; margin: 0 0 10px 0;">🎉 正解です！（選択肢 {choice_labels[correct_idx]}）</h3>
                <div style="font-size: 1.1rem; line-height: 2.1;">
                    <strong>【解説】：</strong> {current_q["explanation"]}
                </div>
                <div style="margin-top: 10px; font-weight: 600; color: #2c3e50;">
                    🔑 教科書の重要語句： {current_q["keyword"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="feedback-card feedback-incorrect">
                <h3 style="color: #c0392b; margin: 0 0 10px 0;">❌ 不正解…（あなたの回答：{choice_labels[user_choice]} ／ 正解：{choice_labels[correct_idx]}）</h3>
                <div style="font-size: 1.1rem; line-height: 2.1;">
                    <strong>【解説】：</strong> {current_q["explanation"]}
                </div>
                <div style="margin-top: 10px; font-weight: 600; color: #2c3e50;">
                    🔑 教科書の重要語句： {current_q["keyword"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        col_next, col_space = st.columns([1, 2])
        with col_next:
            if curr_idx + 1 < total_q:
                if st.button("➡️ 次の問題へ進む", type="primary", use_container_width=True):
                    st.session_state["current_idx"] += 1
                    st.session_state["answered_current"] = False
                    st.rerun()
            else:
                if st.button("🏁 成績確認・レポート画面へ", type="primary", use_container_width=True):
                    st.session_state["current_idx"] += 1
                    st.session_state["quiz_completed"] = True
                    st.rerun()

def render_results_screen(quiz_qs, student_class, student_id, student_name):
    total_q = len(quiz_qs)
    user_answers = st.session_state.get("user_answers", {})
    score = 0
    topic_stats = {}
    
    for idx, q in enumerate(quiz_qs):
        t_id = q["topic_id"]
        t_name = q["topic_name"]
        if t_id not in topic_stats:
            topic_stats[t_id] = {"name": t_name, "total": 0, "correct": 0}
        topic_stats[t_id]["total"] += 1
        
        user_ans = user_answers.get(idx)
        if user_ans == q["answer_index"]:
            score += 1
            topic_stats[t_id]["correct"] += 1
            
    pct = round((score / total_q) * 100, 1) if total_q > 0 else 0
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    v_code = generate_verification_code(student_id or "NONE", student_class, score, total_q)
    
    st.markdown("## 📊 演習結果サマリー")
    
    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("得点", f"{score} / {total_q} 問")
    m2.metric("正答率", f"{pct} %")
    m3.metric("学籍番号", student_id if student_id else "未入力")
    m4.metric("クラス / 氏名", f"{student_class} / {student_name if student_name else '未入力'}")
    
    # Topic breakdown
    st.subheader("📑 テーマ別 正答率内訳")
    for tid in sorted(topic_stats.keys()):
        stat = topic_stats[tid]
        tpct = round((stat["correct"] / stat["total"]) * 100, 1) if stat["total"] > 0 else 0
        c_title, c_bar, c_score = st.columns([4, 4, 2])
        with c_title:
            st.markdown(f"**{stat['name']}**", unsafe_allow_html=True)
        with c_bar:
            st.progress(tpct / 100.0)
        with c_score:
            st.write(f"{stat['correct']} / {stat['total']} 問 ({tpct}%)")
            
    # Google Classroom submission section
    st.markdown("---")
    st.markdown("""
    <div class="classroom-card">
        <h2 style="color: white; margin-top: 0;">📤 Google Classroom 提出用テキスト</h2>
        <p style="font-size: 1rem; color: #f1f2f6;">
            以下の枠内の提出レポートをコピーし、Google Classroomの該当課題の「コメント」または「提出用ファイル」として提出してください。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate clean text report
    report_lines = [
        "==================================================",
        "【生活支援技術 第6章 人生の最終段階における介護 練習問題レポート】",
        "--------------------------------------------------",
        "■ 受講者情報",
        f"  ・クラス: {student_class}",
        f"  ・学籍番号: {student_id if student_id else '未入力'}",
        f"  ・氏名 / ニックネーム: {student_name if student_name else '未入力'}",
        f"  ・実施日時: {now_str}",
        "■ 成績結果",
        f"  ・実施モード: {st.session_state.get('mode_name', '演習')}",
        f"  ・得点: {score} / {total_q} 点",
        f"  ・正答率: {pct} %",
        f"  ・評価: {'S判定（大変素晴らしい理解度です！）' if pct >= 90 else 'A判定（よく理解できています）' if pct >= 80 else 'B判定（合格ラインです。復習しましょう）' if pct >= 60 else 'C判定（もう一度教科書を確認しましょう）'}",
        "■ 分野別正答状況",
    ]
    for tid in sorted(topic_stats.keys()):
        stat = topic_stats[tid]
        # Remove HTML tags for clean text report
        clean_name = re.sub(r'<rt>.*?</rt>', '', stat["name"])
        clean_name = re.sub(r'<.*?>', '', clean_name)
        tpct = round((stat["correct"] / stat["total"]) * 100, 1) if stat["total"] > 0 else 0
        report_lines.append(f"  ・{clean_name}: {stat['correct']}/{stat['total']}問 ({tpct}%)")
        
    report_lines.extend([
        "--------------------------------------------------",
        f"■ 提出認証コード（改ざん防止用トークン）:",
        f"  {v_code}",
        "=================================================="
    ])
    report_text = "\n".join(report_lines)
    
    st.code(report_text, language="text")
    
    c_dl, c_link = st.columns([1, 1])
    with c_dl:
        fname = f"第6章練習問題_{student_class}_{student_id or 'guest'}_提出結果.txt"
        st.download_button(
            label="📥 提出用テキストファイルをダウンロード",
            data=report_text,
            file_name=fname,
            mime="text/plain",
            use_container_width=True,
            type="primary"
        )
    with c_link:
        st.link_button(
            "🌐 Google Classroom を開く",
            "https://classroom.google.com/",
            use_container_width=True
        )
        
    # Review Incorrect Answers
    incorrect_qs = []
    for idx, q in enumerate(quiz_qs):
        if user_answers.get(idx) != q["answer_index"]:
            incorrect_qs.append((idx, q))
            
    if incorrect_qs:
        st.markdown("---")
        st.subheader(f"🔍 まちがえた問題の復習（全 {len(incorrect_qs)} 問）")
        choice_labels = ["A", "B", "C", "D"]
        for q_idx, q in incorrect_qs:
            with st.expander(f"第 {q_idx + 1} 問：{re.sub(r'<rt>.*?</rt>', '', re.sub(r'<.*?>', '', q['question']))[:35]}..."):
                st.markdown(f"<div style='font-size: 1.15rem; font-weight: 700; line-height: 2.1;'>{q['question']}</div>", unsafe_allow_html=True)
                user_ans = user_answers.get(q_idx)
                user_ans_label = choice_labels[user_ans] if (user_ans is not None and 0 <= user_ans < len(choice_labels)) else "未回答"
                st.markdown(f"**あなたの回答：** 選択肢 {user_ans_label} ❌")
                st.markdown(f"**正解：** 選択肢 {choice_labels[q['answer_index']]} ⭕")
                st.markdown(f"**【解説】：** {q['explanation']}", unsafe_allow_html=True)
                st.markdown(f"**🔑 重要語句：** {q['keyword']}", unsafe_allow_html=True)
                
    st.markdown("---")
    if st.button("🔄 もう一度演習する", type="secondary"):
        st.session_state["quiz_active"] = False
        st.session_state["quiz_completed"] = False
        st.rerun()

if __name__ == "__main__":
    main()

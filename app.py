import streamlit as st
from transcript_utils import extract_video_id, fetch_timestamped_transcript
from ai_engine import generate_revision_pack, evaluate_student_answer
from database import init_db, save_lecture_pack, load_lecture_pack, list_saved_lectures
from models import LectureRevisionPack

st.set_page_config(page_title="Lecture Revision AI", page_icon="🎓", layout="wide")
init_db()

# --- Initialize Session State ---
if "current_pack" not in st.session_state:
    st.session_state.current_pack = None
if "video_id" not in st.session_state:
    st.session_state.video_id = None
if "video_start_sec" not in st.session_state:
    st.session_state.video_start_sec = 0
if "evaluations" not in st.session_state:
    st.session_state.evaluations = {}

# --- Sidebar: Saved Lectures & Input ---
with st.sidebar:
    st.title("🎓 RevisionBuddy")
    st.caption("Turn any lecture video into exam Q&As, model answers, and timestamped explanations.")

    input_mode = st.radio("Input Method:", ["YouTube URL", "Paste Transcript Text"])

    transcript_text_input = ""
    youtube_url = ""
    video_id_input = "local_lecture"

    if input_mode == "YouTube URL":
        youtube_url = st.text_input("Paste YouTube Lecture URL:", placeholder="https://www.youtube.com/watch?v=...")
    else:
        video_id_input = st.text_input("Lecture ID / Name:", value="lecture_custom")
        transcript_text_input = st.text_area("Paste Transcript / Notes Text:", placeholder="Paste the lecture transcript or notes here...")

    force_regen = st.checkbox("Force re-generate (ignore cache)", value=False)

    if st.button("🚀 Generate Revision Pack", type="primary", use_container_width=True):
        try:
            st.session_state.evaluations = {}
            
            if input_mode == "YouTube URL":
                if not youtube_url:
                    st.warning("Please paste a YouTube URL first.")
                    st.stop()
                vid = extract_video_id(youtube_url)
                st.session_state.video_id = vid
                st.session_state.video_start_sec = 0

                cached = None if force_regen else load_lecture_pack(vid)
                if cached:
                    st.session_state.current_pack = cached
                    st.success("Loaded instantly from your saved revision history!")
                else:
                    with st.spinner("Extracting timestamped transcript..."):
                        transcript = fetch_timestamped_transcript(vid)
                    with st.spinner("RevisionBuddy is preparing exam questions & model answers..."):
                        pack = generate_revision_pack(transcript)
                        save_lecture_pack(vid, pack)
                        st.session_state.current_pack = pack
                    st.success("Revision Pack Ready!")
            else:
                if not transcript_text_input.strip():
                    st.warning("Please paste some transcript text first.")
                    st.stop()
                st.session_state.video_id = video_id_input
                st.session_state.video_start_sec = 0
                with st.spinner("RevisionBuddy is generating exam questions from your text..."):
                    pack = generate_revision_pack(transcript_text_input)
                    save_lecture_pack(video_id_input, pack)
                    st.session_state.current_pack = pack
                st.success("Revision Pack Ready!")

        except Exception as e:
            st.error(f"Error: {e}")
            st.info("💡 **Tip:** YouTube blocks cloud server IPs. Switch the **Input Method** above to **'Paste Transcript Text'** to generate revision packs instantly without any limits!")

    st.divider()
    st.subheader("📚 Saved Lectures")
    for saved_vid, saved_title in list_saved_lectures():
        if st.button(f"📼 {saved_title[:32]}...", key=f"hist_{saved_vid}", use_container_width=True):
            st.session_state.video_id = saved_vid
            st.session_state.current_pack = load_lecture_pack(saved_vid)
            st.session_state.video_start_sec = 0
            st.session_state.evaluations = {}
            st.rerun()

# --- Helper to export Cheat Sheet ---
def build_markdown_cheatsheet(pack: LectureRevisionPack) -> str:
    md = [f"# {pack.lecture_title} - Exam Revision Sheet\n"]
    md.append("## 📌 Core Summary")
    for pt in pack.executive_summary:
        md.append(f"- {pt}")
    md.append("\n## 📐 Key Formulas & Definitions")
    for f in pack.formulas_and_definitions:
        md.append(f"- {f}")
    md.append("\n## 📝 Exam Questions & Model Answers")
    for idx, q in enumerate(pack.questions_and_answers, 1):
        md.append(f"\n### Q{idx}. [{q.question_type} | {q.difficulty}] {q.question} *(Ref: {q.timestamp_str})*")
        md.append(f"**Model Answer:** {q.model_answer}\n")
        md.append("**Key Points to Include:**")
        for kp in q.key_points:
            md.append(f"- {kp}")
    return "\n".join(md)

# --- Main Workspace ---
pack: LectureRevisionPack = st.session_state.current_pack

if not pack:
    st.info("👈 Paste a YouTube lecture link in the sidebar to generate your interactive Exam Revision Pack.")
else:
    col_video, col_summary = st.columns([1.15, 1])

    with col_video:
        st.subheader(f"📺 {pack.lecture_title}")
        st.video(
            f"https://www.youtube.com/watch?v={st.session_state.video_id}",
            start_time=st.session_state.video_start_sec
        )
        if st.session_state.video_start_sec > 0:
            mins, secs = divmod(st.session_state.video_start_sec, 60)
            st.caption(f"🎯 Jumped to professor's explanation at **{mins:02d}:{secs:02d}**")

    with col_summary:
        st.subheader("⚡ High-Yield Summary")
        for bullet in pack.executive_summary:
            st.markdown(f"- {bullet}")

        if pack.formulas_and_definitions:
            with st.expander("📐 Key Formulas & Definitions", expanded=True):
                for item in pack.formulas_and_definitions:
                    st.markdown(f"- `{item}`")

        st.download_button(
            label="📥 Download Revision Cheat Sheet (.md)",
            data=build_markdown_cheatsheet(pack),
            file_name=f"revision_{st.session_state.video_id}.md",
            mime="text/markdown",
            use_container_width=True
        )

    st.divider()

    # --- Interactive Q&A Bank ---
    st.subheader("🎯 Active Exam Revision & Self-Test")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        selected_type = st.selectbox(
            "Filter by Question Type:",
            ["All", "Short_2_Marks", "Deep_5_Marks", "Viva_Question", "MCQ"]
        )
    with filter_col2:
        selected_diff = st.selectbox("Filter by Difficulty:", ["All", "Easy", "Medium", "Hard"])

    for idx, qa in enumerate(pack.questions_and_answers):
        if selected_type != "All" and qa.question_type != selected_type:
            continue
        if selected_diff != "All" and qa.difficulty != selected_diff:
            continue

        with st.container(border=True):
            head_col, btn_col = st.columns([4, 1.2])
            with head_col:
                st.markdown(
                    f"**Q{idx+1}. [{qa.question_type} • {qa.difficulty}]** ({qa.topic})  \n"
                    f"#### {qa.question}"
                )
            with btn_col:
                if st.button(f"▶ Watch [{qa.timestamp_str}]", key=f"jump_{idx}", use_container_width=True):
                    st.session_state.video_start_sec = qa.timestamp_seconds
                    st.rerun()

            # If MCQ, allow interactive selection
            if qa.question_type == "MCQ" and qa.options:
                st.radio("Choose an option:", qa.options, key=f"mcq_{idx}", index=None)

            # Student Self-Test Area (Write Your Own Answer before peeking)
            with st.expander("✍️ Practice Writing Your Answer (AI Exam Grader)"):
                student_ans = st.text_area(
                    "Type your answer as you would in an exam/viva:",
                    key=f"ans_input_{idx}",
                    height=90
                )
                if st.button("Check My Answer", key=f"grade_btn_{idx}"):
                    if not student_ans.strip():
                        st.warning("Write a brief answer first so the AI can grade it!")
                    else:
                        with st.spinner("Grading your response against lecture key points..."):
                            eval_res = evaluate_student_answer(qa, student_ans)
                            st.session_state.evaluations[idx] = eval_res

                if idx in st.session_state.evaluations:
                    ev = st.session_state.evaluations[idx]
                    st.markdown(f"**Score: {ev.score_out_of_10}/10 — {ev.verdict}**")
                    st.success(f"**What you got right:** {ev.what_you_got_right}")
                    if ev.what_you_missed:
                        st.warning("**Key points missed:**\n" + "\n".join(f"- {m}" for m in ev.what_you_missed))
                    st.info(f"💡 **Exam Tip:** {ev.improved_answer_tip}")

            # Reveal Model Answer & Key Bullet Points
            with st.expander("👁️ Reveal Professor's Model Answer & Key Points"):
                st.markdown(f"**Model Answer:**\n\n{qa.model_answer}")
                st.markdown("**Key Points for Full Marks:**")
                for kp in qa.key_points:
                    st.markdown(f"- ✅ {kp}")
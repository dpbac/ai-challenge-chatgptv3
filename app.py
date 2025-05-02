import streamlit as st
from statements import STATEMENTS
from themes import THEME_DESCRIPTIONS
from scoring import adjust_scores, normalize_scores

st.set_page_config(page_title="AI Quest Quiz", layout="centered")

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'likert_answers' not in st.session_state:
    st.session_state.likert_answers = [3] * len(STATEMENTS)
if 'explored_themes' not in st.session_state:
    st.session_state.explored_themes = []
if 'reuse_preferences' not in st.session_state:
    st.session_state.reuse_preferences = {}
if 'interests' not in st.session_state:
    st.session_state.interests = []
if 'confidence' not in st.session_state:
    st.session_state.confidence = ""
if 'ambition' not in st.session_state:
    st.session_state.ambition = ""
if 'final_scores' not in st.session_state:
    st.session_state.final_scores = {}
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = None

def advance_step():
    st.session_state.step += 1
    st.rerun()

def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Step 0: Welcome
if st.session_state.step == 0:
    st.title("🎓 AI Interest & Motivation Quiz")
    st.write("Discover which AI topics align best with your interests and experiences.")
    if st.button("Start →", key="start_button"):
        advance_step()

# Step 1: Select multiple exploration themes
elif st.session_state.step == 1:
    st.subheader("🧭 What did you explore before?")
    with st.form("exploration_form"):
        st.session_state.explored_themes = [
            theme for theme in THEME_DESCRIPTIONS.keys()
            if st.checkbox(theme, key=f"explored_{theme}")
        ]
        if st.form_submit_button("Next →", use_container_width=True):
            if st.session_state.explored_themes:
                advance_step()
            else:
                st.warning("Please select at least one theme to continue.")

# Step 2: Per-theme reuse preferences in a form
elif st.session_state.step == 2:
    st.subheader("🔎 For each explored theme, do you want to go deeper?")
    with st.form("reuse_form"):
        for theme in st.session_state.explored_themes:
            st.session_state.reuse_preferences[theme] = st.radio(
                f"{theme}", ["Yes", "No"], key=f"reuse_{theme}"
            )
        if st.form_submit_button("Next →", use_container_width=True):
            advance_step()

# Step 3: Likert-style motivation quiz inside a form
elif st.session_state.step == 3:
    st.subheader("💬 What motivates you in AI?")
    with st.form("likert_form"):
        st.caption("Use the scale from 1 (Strongly Disagree) to 5 (Strongly Agree)")
        for i, (statement, _) in enumerate(STATEMENTS):
            st.session_state.likert_answers[i] = st.slider(
                statement, min_value=1, max_value=5,
                value=st.session_state.likert_answers[i],
                key=f"likert_{i}"
            )
        if st.form_submit_button("Next →", use_container_width=True):
            advance_step()

# Step 4: About you
elif st.session_state.step == 4:
    st.subheader("🌟 About You")
    with st.form("about_you_form"):
        st.write("Which AI topics are you interested in?")
        interest_options = [
            "Generative AI (images, music, text)",
            "AI in health & medicine",
            "Climate change & sustainability",
            "Recommender systems",
            "Accessibility & assistive tech",
            "AI in education"
        ]
        st.session_state.interests = [
            topic for topic in interest_options if st.checkbox(topic, key=f"interest_{topic}")
        ]
        st.session_state.confidence = st.radio("How confident are you with AI tools?", ["Low", "Medium", "High"])
        st.session_state.ambition = st.radio("What level of challenge are you looking for?", ["Light exploration", "Moderate challenge", "Portfolio-level deep dive"])
        if st.form_submit_button("Show My Results →", use_container_width=True):
            advance_step()

# Step 5: Results
elif st.session_state.step == 5:
    st.subheader("🏆 Your Top AI Themes")

    raw_scores = {}
    for i, (_, themes) in enumerate(STATEMENTS):
        for theme in themes:
            raw_scores[theme] = raw_scores.get(theme, 0) + st.session_state.likert_answers[i]

    raw_scores = adjust_scores(raw_scores, st.session_state.reuse_preferences)
    norm_scores = normalize_scores(raw_scores)
    top3 = sorted(norm_scores.items(), key=lambda x: x[1], reverse=True)[:3]

    total = sum([score for _, score in top3])
    if total > 0:
        top3 = [(theme, int((score / total) * 100)) for theme, score in top3]

    for theme, percent in top3:
        st.markdown(f"**{theme}** — {percent}% match")
        st.caption(f"{THEME_DESCRIPTIONS.get(theme)} Example use cases: …")

    selected_topic = st.radio("Which one would you like to work on?", [t[0] for t in top3])
    st.session_state.selected_topic = selected_topic

    if st.button("Generate My Prompt →", key="generate_prompt", use_container_width=True):
        advance_step()

# Step 6: Final prompt
elif st.session_state.step == 6:
    st.subheader("💬 Your Personalized Prompt")

    reuse_summaries = [
        f"{t} ({'go deeper' if p == 'Yes' else 'try something new'})"
        for t, p in st.session_state.reuse_preferences.items()
    ]
    reuse_summary = ", ".join(reuse_summaries)

    prompt = (
        f"Hi, I'm interested in working on **{st.session_state.selected_topic}**.\n"
        f"Previously, I explored: {reuse_summary}.\n"
        f"Can you suggest real-world project ideas, datasets, and ethical questions I should consider?"
    )

    st.code(prompt, language="markdown")
    st.markdown("[Open in ChatGPT](https://chat.openai.com)", unsafe_allow_html=True)

    if st.button("🔁 Restart", key="restart_button", use_container_width=True):
        reset_app()

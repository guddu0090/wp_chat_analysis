import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

import helper
import preprocesser

st.set_page_config(page_title="WhatsApp Chat Analysis", layout="wide")
st.title("📊 WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a chat (.txt)", type="txt")

# ───────────────────────── Early-exit ───────────────────────
if uploaded_file is None:
    st.info("⬆️ Upload a chat export to begin.")
    st.stop()

# ───────────────────── Parse & display data ─────────────────
df = preprocesser.preprocess(uploaded_file.getvalue().decode("utf-8"))

st.subheader("First 20 parsed rows")
st.dataframe(df.head(20), use_container_width=True)

# ─────────────── User selector  ───────────────
users = sorted(df["user"].unique().tolist())
users.insert(0, "Overall")
chosen_user = st.sidebar.selectbox("Analyze for", users)

if st.sidebar.button("Run analysis"):
    # ─────────── Summary stats ───────────
    msgs, words, media, links = helper.fetch_stats(chosen_user, df)

    a, b, c, d = st.columns(4)
    a.metric("Messages", msgs)
    b.metric("Words", words)
    c.metric("Media", media)
    d.metric("Links", links)

    st.markdown("---")

    # ─────────── Most busy users ──────────
    if chosen_user == "Overall":
        st.subheader("🔥 Most active participants")
        busy = helper.most_busy_users(df)
        fig_busy, ax_busy = plt.subplots()
        ax_busy.bar(busy.index, busy.values, color="skyblue")
        ax_busy.set_ylabel("Messages")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig_busy)
        st.dataframe(busy.rename("Messages"))

        st.markdown("---")

    # ─────────── Word cloud ──────────────
    st.subheader("☁️ Word cloud")
    cloud = helper.create_word_cloud(chosen_user, df)
    fig_wc, ax_wc = plt.subplots()
    ax_wc.imshow(cloud, interpolation="bilinear")
    ax_wc.axis("off")
    st.pyplot(fig_wc)

    # ───────── Common words ──────────────
    st.subheader("🔠 Most common words")
    common_df = helper.most_common_words(chosen_user, df)
    fig_cw, ax_cw = plt.subplots(figsize=(6, 4))
    ax_cw.bar(common_df["Word"], common_df["Count"], color="orange")
    plt.xticks(rotation=90)
    st.pyplot(fig_cw)
    st.dataframe(common_df)

    # ───────── Emoji usage ───────────────
    st.subheader("😄 Emoji usage")
    emoji_df = helper.emoji_helper(chosen_user, df)
    if not emoji_df.empty:
        e1, e2 = st.columns([1, 2])
        with e1:
            fig_e, ax_e = plt.subplots()
            ax_e.pie(emoji_df["Count"].head(10),
                     labels=emoji_df["Emoji"].head(10),
                     autopct="%1.1f%%", startangle=90)
            st.pyplot(fig_e)
        with e2:
            st.dataframe(emoji_df.head(20))
    else:
        st.info("No emojis found.")

    st.markdown("---")

    # ───────── Activity heatmap ───────────
    st.subheader("📅 Weekly activity heat-map")
    heat = helper.activity_heatmap(chosen_user, df)
    fig_h, ax_h = plt.subplots(figsize=(10, 4))
    sns.heatmap(heat, cmap="YlGnBu", ax=ax_h)
    st.pyplot(fig_h)

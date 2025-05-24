import re
from collections import Counter

import pandas as pd
from wordcloud import WordCloud
import emoji


# ─────────────────── Basic stats ────────────────────
def fetch_stats(selected_user: str, df: pd.DataFrame):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    num_messages = len(df)
    num_words    = df["message"].str.split().str.len().sum()

    media_keywords = [
        "<Media omitted>", "<image omitted>", "<video omitted>",
        "<audio omitted>", "image omitted", "video omitted",
        "audio omitted>", "sticker omitted", "gif omitted",
        "attached media", "[Photo]", "[Video]", "[GIF]"
    ]
    pat = "|".join(re.escape(k) for k in media_keywords)
    num_media = df["message"].str.contains(pat, case=False, regex=True, na=False).sum()

    url_pat   = r"https?://\S+"
    num_links = df["message"].str.contains(url_pat, regex=True, na=False).sum()

    return num_messages, num_words, num_media, num_links


# ───────────── Busiest users (overall) ──────────────
def most_busy_users(df: pd.DataFrame, top_n: int = 5):
    return df["user"].value_counts().head(top_n)


# ───────────────── Word cloud ───────────────────────
def create_word_cloud(selected_user: str, df: pd.DataFrame):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    txt = df["message"].str.cat(sep=" ")
    wc = WordCloud(
        width=600, height=600, background_color="white",
        min_font_size=10, collocations=False
    ).generate(txt)

    return wc


# ──────────────── Common words ──────────────────────
def most_common_words(selected_user: str, df: pd.DataFrame, top_n: int = 20):
    stop_words = set()
    try:
        with open("stop_hinglisg.txt", "r", encoding="utf-8") as f:
            stop_words = {w.strip().lower() for w in f if w.strip()}
    except FileNotFoundError:
        pass

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    df = df[
        (df["user"] != "group_notification")
        & (df["message"].str.strip() != "<Media omitted>")
    ]

    words = []
    for msg in df["message"].dropna():
        for w in re.findall(r"\b\w+\b", msg.lower()):
            if w not in stop_words:
                words.append(w)

    return pd.DataFrame(Counter(words).most_common(top_n),
                        columns=["Word", "Count"])


# ───────────────── Emoji counts (emoji v1 & v2) ─────────────────
def emoji_helper(selected_user: str, df: pd.DataFrame):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    lookup = getattr(emoji, "EMOJI_DATA",
             getattr(emoji, "UNICODE_EMOJI", {}))

    emjs = []
    for msg in df["message"].dropna():
        emjs.extend([ch for ch in msg if ch in lookup])

    return pd.DataFrame(Counter(emjs).most_common(),
                        columns=["Emoji", "Count"])


# ─────────────────── Timelines & Activity ───────────────────
def monthly_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    tl = (
        df.groupby(["year", "month_num", "month"])
          .size().reset_index(name="messages")
          .sort_values(["year", "month_num"])
    )
    tl["label"] = tl.apply(lambda r: f"{r.month}-{r.year}", axis=1)
    return tl


def daily_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]
    return df.groupby("only_date").size().reset_index(name="messages")


def week_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]
    return df["day_name"].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]
    return df["month"].value_counts()




def activity_heatmap(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # Try to extract or convert datetime columns as needed
    if 'message_date' not in df.columns:
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
            df['message_date'] = df['datetime']
        else:
            raise ValueError("DataFrame must contain either 'message_date' or 'datetime' columns")

    df['message_date'] = pd.to_datetime(df['message_date'], errors='coerce')

    df['day_name'] = df['message_date'].dt.day_name()
    df['hour'] = df['message_date'].dt.hour
    df['period'] = df['hour'].apply(lambda x: f"{x}-{(x + 1)%24}")

    heatmap_data = df.pivot_table(index="day_name", columns="period", values="message", aggfunc="count").fillna(0)
    return heatmap_data

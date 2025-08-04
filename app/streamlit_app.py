import streamlit as st
import pandas as pd
import re

# Placeholder poster and platform icons (PNG format)
PLACEHOLDER_IMAGE = "https://via.placeholder.com/200x300?text=No+Image"
POPCORN_ICON = "https://upload.wikimedia.org/wikipedia/commons/c/c8/Popcorn_icon.png"
NETFLIX_LOGO = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Netflix_Logomark.png/640px-Netflix_Logomark.png"
PRIME_LOGO = "https://upload.wikimedia.org/wikipedia/commons/2/27/Amazon_Prime_logo.png"

# -----------------------------
# Load Streaming Data
# -----------------------------
@st.cache_data
def load_streaming_data():
    df = pd.read_csv("data/streaming_availability.csv")
    df.rename(columns=lambda x: x.strip(), inplace=True)
    df["TitleClean"] = df["Title"].astype(str).str.strip()
    return df

# -----------------------------
# Load Movie Metadata
# -----------------------------
@st.cache_data
def load_movies_meta():
    meta = pd.read_csv("data/movies.dat", sep="::", engine="python",
                       encoding="ISO-8859-1",
                       names=["movieId", "title", "genres"])
    meta["clean_title"] = meta["title"].apply(lambda x: re.sub(r"\s\(\d{4}\)$", "", x))
    meta["genre_list"] = meta["genres"].apply(lambda x: x.split("|"))
    return meta

stream_df = load_streaming_data()
meta = load_movies_meta()

# Merge metadata with streaming titles
combined = stream_df.merge(
    meta[["clean_title", "genre_list"]],
    how="left",
    left_on="TitleClean", right_on="clean_title"
)

# Replace missing genres with empty list
combined["genre_list"] = combined["genre_list"].apply(lambda x: x if isinstance(x, list) else [])

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.markdown("# 🎥 Streaming-based Movie Recommender")

# Year filter
min_year = int(combined["Year"].min())
max_year = int(combined["Year"].max())
year_selected = st.slider("Select minimum release year:", min_year, max_year, 2000)

# Platform filter
platform_options = ["All", "Netflix Only", "Prime Video Only"]
selected_platform = st.selectbox("Filter by Platform:", platform_options)

# Genre filter
all_genres = sorted({g for sub in combined["genre_list"] for g in sub})
selected_genres = st.multiselect("Filter by genre(s):", all_genres)

# Apply filters
df = combined[combined["Year"] >= year_selected]
if selected_platform == "Netflix Only":
    df = df[df["Netflix"] == 1]
elif selected_platform == "Prime Video Only":
    df = df[df["Prime.Video"] == 1]

if selected_genres:
    df = df[df["genre_list"].apply(lambda gl: all(g in gl for g in selected_genres))]

if df.empty:
    st.warning("No movies found. Try adjusting the filters.")
else:
    title_choices = sorted(df["TitleClean"].unique())
    search_title = st.selectbox("Choose a movie:", title_choices)
    top_n = st.slider("Number of recommendations:", 1, 10, 5)

    if st.button("🚀 Recommend"):
        st.toast("🎉 Generating recommendations...")

        base_genres = set(df.loc[df["TitleClean"] == search_title, "genre_list"].iloc[0])
        candidates = []
        for _, row in df.iterrows():
            if row["TitleClean"] == search_title:
                continue
            overlap = len(base_genres & set(row["genre_list"]))
            if overlap > 0:
                candidates.append((row["TitleClean"], overlap))

        recommendations = [t for t, _ in sorted(candidates, key=lambda x: x[1], reverse=True)][:top_n]

        if not recommendations:
            st.info("No similar genre matches found.")
        else:
            st.subheader("🍿 Top Recommendations")
            for i, title in enumerate(recommendations, 1):
                row = df[df["TitleClean"] == title].iloc[0]
                col1, col2, col3 = st.columns([1, 4, 1])

                with col1:
                    st.image(PLACEHOLDER_IMAGE, width=80)

                with col2:
                    st.markdown(f"**{i}. {title}**")

                with col3:
                    st.image(POPCORN_ICON, width=30)
                    if int(row.get("Netflix", 0)) == 1:
                        st.image(NETFLIX_LOGO, width=50)
                    if int(row.get("Prime.Video", 0)) == 1:
                        st.image(PRIME_LOGO, width=50)

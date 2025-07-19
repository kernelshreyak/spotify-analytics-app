import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import streamlit as st
import plotly.express as px

# Configure page layout to use full width
st.set_page_config(page_title="Spotify Analytics", layout="wide")

# Load environment variables
load_dotenv()

# Spotify OAuth setup and explicit token retrieval
os.environ["SPOTIPY_CLIENT_ID"] = os.getenv("SPOTIPY_CLIENT_ID")
os.environ["SPOTIPY_CLIENT_SECRET"] = os.getenv("SPOTIPY_CLIENT_SECRET")
os.environ["SPOTIPY_REDIRECT_URI"] = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8501")

scope = "user-top-read user-read-recently-played"
# Use OAuth manager to get token
auth_manager = SpotifyOAuth(
    scope=scope,
    cache_path=".cache",
    show_dialog=True
)
token = auth_manager.get_access_token(as_dict=False)
sp = spotipy.Spotify(auth=token)

# Fetch current user's display name
user_profile = sp.current_user()
display_name = user_profile.get('display_name') or user_profile.get('id')
st.title(f"🎧 {display_name}'s Spotify Analytics Dashboard")

# Fetch top artists and tracks
top_artists = sp.current_user_top_artists(limit=20, time_range="medium_term")["items"]
top_tracks = sp.current_user_top_tracks(limit=20, time_range="medium_term")["items"]

# Build DataFrames for display
df_art = pd.DataFrame([
    {"Rank": i+1, "Artist": a["name"], "Popularity": a["popularity"], "Followers": a["followers"]["total"]}
    for i, a in enumerate(top_artists)
])

df_trk = pd.DataFrame([
    {"Rank": i+1, "Track": t["name"], "Artist": t["artists"][0]["name"], "Popularity": t["popularity"], "Track ID": t["id"]}
    for i, t in enumerate(top_tracks)
])

# Display full-width tables
st.header("Top Artists")
st.dataframe(df_art, use_container_width=True)

st.header("Top Tracks")
st.dataframe(df_trk.drop(columns=["Track ID"]), use_container_width=True)

# Advanced analytics section
st.header("🎶 Advanced Analytics")
# Breakdown: number of top tracks per artist
st.subheader("Artist Presence in Top Tracks")
# Count top tracks per artist
df_artist_track_counts = (
    df_trk.groupby('Artist')['Track']
    .count()
    .reset_index(name='Top Track Count')
    .sort_values('Top Track Count', ascending=False)
)
# Display bar chart of counts
st.bar_chart(df_artist_track_counts.set_index('Artist'))

# Detailed track listing per artist
st.subheader("Top Tracks by Artist")
for artist in df_artist_track_counts['Artist']:
    artist_tracks = df_trk[df_trk['Artist'] == artist]
    with st.expander(f"{artist} ({len(artist_tracks)} Top Tracks)"):
        st.table(
            artist_tracks[['Track']]
            .reset_index(drop=True)
        )

# Footer caption
st.caption("Data fetched via Spotipy (Spotify Web API)")

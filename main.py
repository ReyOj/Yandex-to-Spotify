import spotipy
from spotipy.oauth2 import SpotifyOAuth
from yandex_music import Client
from fuzzywuzzy import fuzz

SPOTIFY_CLIENT_ID = ''
SPOTIFY_CLIENT_SECRET = ''
SPOTIFY_REDIRECT_URI = 'http://:8888/callback'
YANDEX_MUSIC_TOKEN = ''
LOG_FILE = "not_added_tracks.log"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-library-read user-library-modify",
    cache_path=".spotify_cache"
))

ya_client = Client(YANDEX_MUSIC_TOKEN).init()

def find_track_on_spotify(title, artists):
    query = f"{title} {' '.join(artists)}"
    results = sp.search(q=query, type='track', limit=1)

    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        spotify_title = track['name']  # Название трека на Spotify
        spotify_artists = [artist['name'] for artist in track['artists']]  # Исполнители Spotify

        # Сравниваем названия с помощью fuzzy matching
        title_similarity = fuzz.ratio(title.lower(), spotify_title.lower())
        # Условия добавления: высокая похожесть названия и совпадение исполнителя
        if title_similarity > 90:
            return track['id']  # Возвращаем ID, если трек подходит

    return None

def log_not_added(track_info, reason):
    """Логирует треки, которые не были добавлены."""
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(
            f"Track: {track_info.title}, Artists: {[artist.name for artist in track_info.artists]}, Reason: {reason}\n"
        )

def add_tracks_to_spotify_favorites(track_ids):
    sp.current_user_saved_tracks_add([track_ids])

favorites = ya_client.users_likes_tracks()
favorites = reversed(favorites)
i=0
for track in favorites:
    i += 1
    if i > 3267:
        track_info = track.fetch_track()
        spotify_track_id = find_track_on_spotify(track_info.title, [artist.name for artist in track_info.artists])
        if spotify_track_id:
            add_tracks_to_spotify_favorites(spotify_track_id)
            print(f"{i}. {track_info.title}, {[artist.name for artist in track_info.artists]}")
        else:
            reason = "No match found"  # Укажите причину
            log_not_added(track_info, reason)
            print(f"{i}. Not found: {track_info.title}, {[artist.name for artist in track_info.artists]}")
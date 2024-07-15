import spotipy
import json
import os
from spotipy.oauth2 import SpotifyOAuth

def oauth_info(filename='spotify_credentials.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    else:
        print("""
Please go to the Spotify Developer Dashboard (https://developer.spotify.com/dashboard/applications) to create an app and get your OAuth information.
You will need the Client ID, Client Secret, and Redirect URI.

For the Redirect URI, a common practice for local development is to use 'http://localhost:8888/callback'.
This means you will set up your application to listen on localhost port 8888, and after authentication, Spotify will redirect to this URI.
Make sure to add 'http://localhost:8888/callback' (or your chosen URI) in your app settings on the Spotify Developer Dashboard under 'Edit Settings' -> 'Redirect URIs'.
""")

        oauth_info = {
            "client_id": input("Enter your Spotify client ID: "),
            "client_secret": input("Enter your Spotify client secret: "),
            "redirect_uri": input("Enter your Spotify redirect URI (e.g., http://localhost:8888/callback): "),
            "scope": "user-library-read user-read-currently-playing user-read-playback-state"
        }
        with open(filename, 'w') as file:
            json.dump(oauth_info, file, indent=4)
        return oauth_info

auth_info = oauth_info()

# Set up the authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=auth_info["client_id"],
                                               client_secret=auth_info["client_secret"],
                                               redirect_uri=auth_info["redirect_uri"],
                                               scope=auth_info["scope"]))

def fetch_info(playlist_id):
    tracks = sp.playlist_tracks(playlist_id, limit=100)
    all_tracks_info = []
    artist_ids = set()

    for item in tracks['items']:
        artist_ids.add(item['track']['artists'][0]['id'])

    artist_genres = {}
    for i in range(0, len(artist_ids), 50):
        batch = list(artist_ids)[i:i+50]
        artists_info = sp.artists(batch)['artists']
        for artist in artists_info:
            artist_genres[artist['id']] = artist['genres'][0] if artist['genres'] else "No genre available"

    for item in tracks['items']:
        track_name = item['track']['name']
        artist_id = item['track']['artists'][0]['id']
        genre = artist_genres[artist_id]
        all_tracks_info.append((track_name, item['track']['artists'][0]['name'], genre))

    return all_tracks_info

def fetch_user_playlists():
    playlists = sp.current_user_playlists()
    playlist_info = []
    for i, playlist in enumerate(playlists['items'], start=1):
        print(f"{i}: {playlist['name']} (ID: {playlist['id']})")
        playlist_info.append((playlist['name'], playlist['id']))
    return playlist_info

def choose_playlist():
    playlist_info = fetch_user_playlists()
    if not playlist_info:
        print("No playlists found.")
        return None, None
    while True:
        try:
            selection = int(input("Enter the number of the playlist you want to analyze: ")) - 1
            if 0 <= selection < len(playlist_info):
                return playlist_info[selection]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")

def main():
    playlist_name, playlist_id = choose_playlist()
    if playlist_id:
        all_songs_with_genre = fetch_info(playlist_id)
        songs_data = [{"track_name": track_name, "artist_name": artist_name, "genre": genre} for track_name, artist_name, genre in all_songs_with_genre]
        safe_playlist_name = playlist_name.replace(' ', '_').replace('\'', '')
        filename = f"{safe_playlist_name}_songs.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(songs_data, f, ensure_ascii=False, indent=4)
        print(f"Data has been written to {filename}")
    else:
        print("Operation cancelled or no playlist selected.")

if __name__ == "__main__":
    main()
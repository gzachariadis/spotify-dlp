from methods import *

CLIENT_ID="318477ce3d1c4c00858c6c2c427709a2"
CLIENT_SECRET="de27703ea6864814a4da0dbcc25a8808"
redirect_uri = "http://localhost:8888/callback"
cache_path="/home/{0}/.cache/cache.txt".format(get_username())

def spotify_authentication():
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=redirect_uri,
                                               cache_path=cache_path))
    spotify.trace = False
    time.sleep(5.0)
    return spotify

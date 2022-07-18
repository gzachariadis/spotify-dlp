from turtle import up
import spotipy
from spotipy import SpotifyOAuth
from config import CLIENT_ID, CLIENT_SECRET,redirect_uri, cache_path
import time
from methods import *
import json

def spotify_authentication():
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=redirect_uri,
                                               cache_path=cache_path))
    spotify.trace = False
    time.sleep(5.0)
    return spotify

def did_i_identify_artist_correctly(artist):
    spotify = spotify_authentication()

    resulting_artists = []
    # resulting_tracks = search_results['tracks']['items']
    print("Searching Spotify for {}....".format(artist))
    try:
        for offset in range(0, 1000, 50):
            search_results = spotify.search(artist.strip(),limit=50,offset=offset,type="artist")
            time.sleep(2.0)       
            resulting_artists.extend(search_results['artists']['items'])
    except:
        print("Error Searching Artist on Spotify....")

    artists_found = find_values("name",json.dumps(resulting_artists))

    if artist.strip() in artists_found:
        print("Artist was identified correctly as {}".format(artist.strip()))
        return artist
    else:
        for i in artists_found:
            if i.lower() == artist.lower():
                print("Artist was identified correctly as {}".format(artist.strip()))
                return artist
    return 

def search_tracks_to_find_artist(youtube_title,track):
    time.sleep(30.0)
    spotify = spotify_authentication()

    # resulting_tracks = search_results['tracks']['items']
    print("Searching Spotify with full video title....Please sit tight...")
    for offset in range(0, 100, 1):
        search_results = spotify.search(track.strip(),limit=1,offset=offset,type="track")
        time.sleep(2.0) 
        try:
            track_artist = str(search_results['tracks']['items'][0]['artists'][0]['name']).strip()
        except IndexError:
            continue

        try:
            track_name = clean_track_for_extraction(search_results['tracks']['items'][0]['name']).strip()
        except IndexError:
            continue 

        substring_index = [m.start() for m in re.finditer(track_artist.lower(), youtube_title.lower())]
        
        if substring_index is not None:
            if len(set(substring_index)) != 0:
                potential_artist_name = str(youtube_title[list(set(substring_index))[0]:]).lower().strip()
                if potential_artist_name == track_artist.lower().strip():
                    time.sleep(5.0)
                    print("Artist was successfully identified as {0}".format(track_artist))
                    return track_artist

        if track_artist.lower().strip() in youtube_title.lower().strip():
            if track_name.lower().strip() == track.lower().strip():
                time.sleep(3.0)
                print("Artist was successfully identified as {0}".format(track_artist))
                return track_artist
    
    print("Spotify can't track an exact match...")
    return

def did_i_identify_track_correctly(artist,track):
    spotify = spotify_authentication()
    
    track = clean_track_for_extraction(track)

    # resulting_tracks = search_results['tracks']['items']
    print("Searching Spotify for {0} ....Please sit tight...".format(clean_track_for_extraction(track)))
    try:
        for offset in range(0, 100, 1):
            search_results = spotify.search(track.strip(),limit=1,offset=offset,type="track")
            time.sleep(2.0) 
            track_artist = (search_results['tracks']['items'][0]['artists'][0]['name']).strip()
            track_name = clean_track_for_extraction(search_results['tracks']['items'][0]['name']).strip()
            track_id = search_results['tracks']['items'][0]['id']

            if track_artist.lower().strip() == artist.lower().strip():
                if track_name.lower().strip() == track.lower().strip():
                    time.sleep(3.0)
                    print("Track was successfully identified as {0} by {1}".format(convert_string(track).strip(),convert_string(artist)).strip())
                    return convert_string(track_name).strip(), str(track_id).strip()
    except:
        try:
            search_results = spotify.search(track.strip(),limit=1,offset=0,type="track")
            time.sleep(2.0) 
            track_artist = (search_results['tracks']['items'][0]['artists'][0]['name']).strip()
            track_name = clean_track_for_extraction(search_results['tracks']['items'][0]['name']).strip()
            track_id = search_results['tracks']['items'][0]['id']

            if track_artist.lower().strip() == artist.lower().strip():
                if track_name.lower().strip() == track.lower().strip():
                    time.sleep(3.0)
                    print("Track was successfully identified as {0} by {1}".format(convert_string(track),convert_string(artist)))
                    return convert_string(track_name), str(track_id).strip()
        except:
            print("Spotify can't track an exact song match...")
            return 

    print("Spotify can't track an exact match...")
    return

def settle_artist(youtube_artist,creator,channel,uploader):
    print("Title seems to misidentify the artist, sit tight, trying alternatives....")
    variables_list = []
    
    if youtube_artist:
        if youtube_artist is not None:
            variables_list.append(youtube_artist)
    
    if creator:
        if creator is not None:
            variables_list.append(creator)
    
    if channel:
        if creator is not None:
            variables_list.append(channel)
        
    if uploader:
        if uploader is not None:
            variables_list.append(uploader)
  
    if len(variables_list) == 1:
        artist = did_i_identify_artist_correctly(clean_artist(variables_list[0]))
        if artist is not None:
            return convert_string(artist).split()
        else:
            print("Search Failed. Unable to identify artist using Spotify...")
            print("Testing {} as artist.".format(clean_artist(variables_list[0])))
            return clean_artist(str(variables_list[0]))
    else:
        for variable in variables_list:
            artist = did_i_identify_artist_correctly(clean_artist(str(variable)))
            if artist is None:
                continue
            else:
                return convert_string(artist).split()


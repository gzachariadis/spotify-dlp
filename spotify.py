from operator import length_hint
from tabnanny import check
from textwrap import indent
from turtle import up
import spotipy
from spotipy import SpotifyOAuth
from config import CLIENT_ID, CLIENT_SECRET,redirect_uri, cache_path
import time
from methods import *
import json
from difflib import SequenceMatcher
import math
from methods import *
from datetime import datetime

def spotify_authentication():
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=redirect_uri,
                                               cache_path=cache_path))
    spotify.trace = False
    time.sleep(10.0)
    return spotify

def did_i_identify_artist_correctly(artist):
    spotify = spotify_authentication()

    resulting_artists = []
    # resulting_tracks = search_results['tracks']['items']
    print("Searching Spotify for {}....".format(artist).strip())
    try:
        for offset in range(0, 1000, 50):
            search_results = spotify.search(str(artist).strip(),limit=50,offset=offset,type="artist")
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

def settle_title(track):
    spotify = spotify_authentication()

    results = spotify.search(track.strip(),limit=1,offset=0,type="track")
    full_tracks = []
    while results:
        full_tracks.extend(results['tracks']['items'][0])
        tracks = spotify.next(results['tracks']['items'])  # eventually will be `None` on the final page
  
        return tracks


def search_track_by_youtube_video_title(track,artist):
    # Initiate two objects one for songs matching the artist and one for the final result
    search_results = {}
    song = {}
    closely_matching = {}
    valid = ("y","yes","no","n")
    negative = ("no","n")
    # Authenticate token with spotify
    spotify = spotify_authentication()

    # Seach the first 1000 results for artist + track combo
    print("Acquiring Tracks....")
    for offset in range(0, 1000, 50):
        results = spotify.search(q='artist:' + artist.strip() + ' track:' + track.strip(),limit=50,offset=offset,type = 'track')
        for each_track in results["tracks"]["items"]:
            check_artist = math.trunc(similar(str(each_track['artists'][0]['name']).lower().strip(),str(artist).lower().strip()))
            if int(check_artist) == int(100):
                # if track artist matches the artist found previously, give me all their matching records
                search_results[each_track['id']] = each_track['name']
    
    for key,value in search_results.items():
        # check if a song by the artist matches closely the title
        check_song = math.trunc(similar(str(value).lower().strip(),str(track).lower().strip()))
    
        if int(check_song) == int(100):
            song[key] = value
            return song 
        elif int(check_song) > int(75):
            closely_matching[check_song] = key,value
    
    if closely_matching:
        print("Found {} closely matching songs in Spotify Database...".format(int(len(closely_matching))))
        for key,value in closely_matching.items():
            is_your_track = input("is \"{}\" the correct track? [y/n] ".format(value[1]))
            while is_your_track.lower() not in valid:
                print("Not a Valid Answer,try again....")
                is_your_track = input("is \"{}\" the correct track? [y/n] ".format(value[1]))
            if is_your_track.lower() in negative:
                continue
            else:
                song[value[0]] = value[1]
                return song

def search_track_with_cleaned_title(track,artist):
    # Initiate two objects one for songs matching the artist and one for the final result
    search_results = {}
    song = {}

    # Authenticate token with spotify
    spotify = spotify_authentication()

    # Seach the first 1000 results for artist + track combo
    print("Searching Tracks Now....")
    for offset in range(0, 1000, 50):
        results = spotify.search(q='artist:' + artist.strip() + ' track:' + track.strip(),limit=50,offset=offset,type = 'track')
        for each_track in results["tracks"]["items"]:
            check_artist = math.trunc(similar(str(each_track['artists'][0]['name']).lower().strip(),str(artist).lower().strip()))
            if int(check_artist) == int(100):
                # if track artist matches the artist found previously, give me all their matching records
                search_results[each_track['id']] = each_track['name']
    
    for key,value in search_results.items():

        # check if a song by the artist matches closely the title
        check_song = math.trunc(similar(str(value).lower().strip(),str(track).lower().strip()))
    
        if int(check_song) == int(100):
            song[key] = value
            return song


def get_artist_id(artist):
    spotify = spotify_authentication()

    for offset in range(0,1000,50):
        results = spotify.search(artist.strip(),limit=50,offset=offset,type="artist")
        time.sleep(3.0)       
        for each_artist in results["artists"]["items"]:
            check_artist = math.trunc(similar(str(each_artist['name']).lower().strip(),str(artist).lower().strip()))
            if int(check_artist) == int(100):
                # if track artist matches the artist found previously, give me all their matching records
                return each_artist['id']

def get_artist_genres(artist_id):
    spotify = spotify_authentication()
    results = spotify.artist(artist_id)
    return results['genres']

def get_artist_albums(artist_id):
    albums_dictionary = {}
    time.sleep(10.0)
    spotify = spotify_authentication()
    
    # Search for a single artist by name
    result = spotify.artist_albums(artist_id,album_type='album',limit=50,offset=0)
    
    for each_album in result["items"]:
        albums_dictionary[each_album['id']] = str(each_album['name']).strip()
    
    return albums_dictionary

def get_artist_singles(artist_id):
    singles_dictionary = {}
    time.sleep(10.0)
    spotify = spotify_authentication()

    # Search for a single artist by name
    result = spotify.artist_albums(artist_id,album_type='single',limit=50,offset=0)

    for single in result["items"]:
        singles_dictionary[single['id']] = str(single['name']).strip()
    
    return singles_dictionary

def get_album_info(albums_dictionary):
    album_information = {}
    spotify = spotify_authentication()
    featuring_artists = []
    for key in albums_dictionary.keys():
        album = spotify.album(key)

        for x in album['tracks']['items']:
            print(x['name'])
            print(x['track_number'])
             # Search for featuring artists
            if len(x['artists']) > 1:
                check_artist = math.trunc(similar(str(x['name']).lower().strip(),str(artist).lower().strip()))
                if int(check_artist) != int(100):
                    print(x['name'])
                    featuring_artists.append(x['name'])

        album_information[album['id']] = album['label'], album['total_tracks'], album['genres'], album['release_date']
        
    return album_information

def get_all_albums_tracks(albums_dictionary,artist):
    # For each Album in Albums Dictionary look up tracks and create a dictionary
    tracks_dictionary = {}
    spotify = spotify_authentication()
    featuring_artists = []

    print("Searching all album tracks...")

    for key, value in albums_dictionary.items():
        # Search for Album using URI
        time.sleep(5.0)

        # get album tracks
        album_track_list = spotify.album_tracks(key,limit=50,offset=0)

        for each_track in album_track_list['items']:            
            # Search for featuring artists
            for x in each_track['artists']:
                if len(each_track['artists']) > 1:
                    check_artist = math.trunc(similar(str(x['name']).lower().strip(),str(artist).lower().strip()))
                    if int(check_artist) != int(100):
                        featuring_artists.append(x['name'])
            
            tracks_dictionary[each_track['id']] = key, value[0], value[1], value[2], each_track['name'], each_track['track_number'], set(featuring_artists)
            featuring_artists.clear()
            
    return tracks_dictionary

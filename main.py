# Importing Additional Files
from operator import ge
from textwrap import indent
from config import CLIENT_ID, CLIENT_SECRET,redirect_uri, cache_path
from methods import *
from spotify import *

# Importing Required Libraries
import sys
import json

# Pull json from bash
f = sys.argv[1]

# The information pulled from youtube
youtube_information = json.loads(f)

# Set the youtube video title to variable
youtube_video_full_title = youtube_information['fulltitle']

print("Video title identified as {}.".format(youtube_video_full_title).strip())

# Remove Things that might mess with identification
youtube_video_full_title = deEmojify(youtube_video_full_title)
youtube_video_full_title = clear_title(youtube_video_full_title)
youtube_video_full_title = re.sub(r"[\%\/\\\&\?\,\'\;\:\!\-\:\)]{2,}", '', youtube_video_full_title)
youtube_video_full_title = re.sub(r"\s{2,}", " ", youtube_video_full_title)

print("Cleaned title a bit for processing...")
print("New Title {}".format(youtube_video_full_title))

# Find all seperator objects
the_seperator_object = find_separator(youtube_video_full_title)
# Find the last instance of a seperator object
the_seperator_index = find_correct_seperator_index(the_seperator_object)

# Cut the youtube video title to two pieces, one for artist and one for song title using the seperator
title_extracted_track, title_extracted_artist = youtube_video_full_title[the_seperator_index:], youtube_video_full_title[:the_seperator_index]


# Clean the artist and title to begin spotify searches
artist = clean_artist(title_extracted_artist)
track = clean_track(title_extracted_track)

print("Video title suggests artist is {}".format(artist))
# Search Spotify for Artist with that name
artist = did_i_identify_artist_correctly(artist)

# If you can't identify Artist - Song then try Song - Artist
if artist is None:
    print("Artist extraction failed, trying reverse search...")

    # Try to find artist by using a Artist - Song method
    title_extracted_artist, title_extracted_track = youtube_video_full_title[the_seperator_index:], youtube_video_full_title[:the_seperator_index]
    
    # Clean the artist and title to begin spotify searches
    artist = clean_artist(title_extracted_artist)
    track = clean_track(title_extracted_track)
    
    print("Video title suggests artist is {}".format(artist))

    # Search Spotify for Artist with new artist name
    artist = did_i_identify_artist_correctly(artist)

# if artist from title is not able, use other alternatives
if artist is None:
    artist = settle_artist(youtube_information['artist'],youtube_information['creator'],youtube_information['channel'],youtube_information['uploader'])

    if artist is not None:
        artist = convert_string(artist)

    # Let's test the uploader,creator,channel name etc. for artist info
    if artist is not None:
        temporary_artist = did_i_identify_artist_correctly(artist)

try:
    # If you find it in those information, good! stop
    if temporary_artist is not None:
        artist = temporary_artist.strip()
    # if you don't, let's test the title again for an artist name
    elif temporary_artist is None:
        temporary_artist = search_tracks_to_find_artist(youtube_video_full_title,clean_track_for_extraction(title_extracted_track))
    
    if temporary_artist is not None:
        artist = temporary_artist.strip()
except NameError:
    pass

print("\n")
print("Moving on to track identification....")

print("Processing Track as a potential Remix...")

spotify_track_dict_info = search_track_by_youtube_video_title(clean_track_for_extraction(title_extracted_track),artist)

if spotify_track_dict_info is None:
    print("Processing Track as an Original....")
    spotify_track_dict_info = search_track_with_cleaned_title(clean_track(title_extracted_track),artist)

if spotify_track_dict_info is None:
    # Try other means to determinte track title
    print("Unable to find a match....Trying Alternatives")
    if youtube_information['track'] is not None:
        spotify_track_dict_info = search_track_by_youtube_video_title(clean_track(youtube_information['track']))
    else:
        print("Alternatives Methods of Extraction Failed...")

if spotify_track_dict_info is None:
    print("All methods were unsuccessful at determining the track. Try another video...")
    sys.exit()

print(spotify_track_dict_info)

genre = ""
print("\n")
print("Identifying Track Genre.....")

if youtube_information['genre'] != "NA":
    genre = youtube_information['genre']

if not genre:
    print("Youtube Video did not specify Music Genre, trying Spotify database....")
    artist_genres = get_artist_genres(get_artist_id(artist))

    if artist_genres:
        genre = clean_up_genres(artist_genres)
    else:
        print("Spotify Artist has no Music Genres attached to their profile...")

print(genre)
print("\n")

artist_albums = get_artist_albums(get_artist_id(artist))

artist_singles = get_artist_singles(get_artist_id(artist))

artist_album_information = get_album_info(artist_albums)

single_album_information = get_album_info(artist_singles)

final_info = get_all_albums_tracks(artist_albums,artist,artist_album_information)

single_info = get_all_albums_tracks(artist_singles,artist,single_album_information)

"""
for key in final_info.keys():
    print(key)

for key in single_info.keys():
    print(key)

"""

yt_dlp_info = return_yt_info(final_info,single_info,spotify_track_dict_info)
# print(len(spotify_track_dict_info.keys()))

try:
    print(yt_dlp_info)
except NameError:
    for key in spotify_track_dict_info.keys():
        get_track_by_id(key,artist)



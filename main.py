# Importing Additional Files
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

# Remove Things that might mess with identification
youtube_video_full_title = deEmojify(youtube_video_full_title)
youtube_video_full_title = clear_title(youtube_video_full_title)
youtube_video_full_title = re.sub(r"[\%\/\\\&\?\,\'\;\:\!\-\:\)]{2,}", '', youtube_video_full_title)

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
    artist = convert_string(settle_artist(youtube_information['artist'],youtube_information['creator'],youtube_information['channel'],youtube_information['uploader']))

# Let's test the uploader,creator,channel name etc. for artist info
if artist is not None:
   temporary_artist = did_i_identify_artist_correctly(artist)

# If you find it in those information, good! stop
if temporary_artist is not None:
    artist = temporary_artist.strip()

# if you don't, let's test the title again for an artist name
elif temporary_artist is None:
    temporary_artist = search_tracks_to_find_artist(youtube_video_full_title,clean_track_for_extraction(title_extracted_track))
    if temporary_artist is not None:
        artist = temporary_artist.strip()

print("Moving on to track identification....")

print(track)

try:
    # Search for track on spotify
    track,track_id = did_i_identify_track_correctly(artist,clean_track_for_extraction(title_extracted_track))
except:
    try:
        # if I can't identify the track as a remix then try as a single
        print("Can't identify track as a variation (eg. remix). Processing track as an original...")
        track,track_id = did_i_identify_track_correctly(artist,clean_track(title_extracted_track))
    except:
        pass

# Try other means to determinte track title
print(clean_artist(artist),clean_track(track))







print(artist,track)


from methods import *
from spotify import *
import sys
import json
# Pull json from bash
f = sys.argv[1]

# The information pulled from youtube
youtube_information = json.loads(f)

# Set the youtube video title to variable
youtube_video_full_title = youtube_information['fulltitle']

# print("Video title identified as {}".format(youtube_video_full_title).strip())

print(youtube_video_full_title)

youtube_video_full_title = remove_emoji(youtube_video_full_title)

youtube_video_full_title = deEmojify(youtube_video_full_title)

youtube_video_full_title = remove_emojis(youtube_video_full_title)

youtube_video_full_title = remove_emojis_v2(youtube_video_full_title)

youtube_video_full_title = smiley_cleaner(youtube_video_full_title)

youtube_video_full_title = remove_chinese(youtube_video_full_title)

youtube_video_full_title = seperate_backslash_words(youtube_video_full_title)

youtube_video_full_title = replace_special_seperators(youtube_video_full_title)

# print(find_tags(youtube_video_full_title))

youtube_video_full_title = clean_unrequired_from_parenthesis(youtube_video_full_title)

youtube_video_full_title = clean_second_dash(youtube_video_full_title)

youtube_video_full_title = clean_brackets(youtube_video_full_title)

youtube_video_full_title = clean_unrequired_from_bracket(youtube_video_full_title)

youtube_video_full_title = second_parenthesis(youtube_video_full_title)
     
youtube_video_full_title = remove_quotes_from_string(youtube_video_full_title)

youtube_video_full_title = ade_seperate_track_artist(youtube_video_full_title)

youtube_video_full_title = strip_specific_words(youtube_video_full_title)

youtube_video_full_title = remove_miscellaneous(youtube_video_full_title)

youtube_video_full_title = final_cleanup(youtube_video_full_title)

youtube_video_full_title = replace_seperators(youtube_video_full_title,replace_the_seperators)

youtube_video_full_title = spaces_for_seperator(youtube_video_full_title)

youtube_video_full_title = capitalize_words_with_dots(youtube_video_full_title)

youtube_video_full_title = fix_seperated_words(youtube_video_full_title)

youtube_video_full_title = fix_full_parenthesis(youtube_video_full_title)

youtube_video_full_title = re.sub(r"\s{2,}", " ", youtube_video_full_title)

print(youtube_video_full_title)
print("\n")


"""
if no special characters with spaces then try first word as artist, if correct add a dash after it.
if no special characters and first word no artist try first two. 

Omri - idk wts





Blue (Da Ba Dee) - Dv7)

"""

# Find all seperator objects
the_seperator_object = find_separator(youtube_video_full_title)

# Find the last instance of a seperator object
the_seperator_index = find_correct_seperator_index(the_seperator_object)

# Cut the youtube video title to two pieces, one for artist and one for song title using the seperator
title_extracted_track, title_extracted_artist = youtube_video_full_title[the_seperator_index:], youtube_video_full_title[:the_seperator_index]

# Clean the artist and title to begin spotify searches
artist = clean_artist(title_extracted_artist)
track = final_cleanup(title_extracted_track)

print(external_clean(track))

# Search for Remixes by the extracted Artist
if track.find("(") != -1:

    if identify_song_type(track) is True:
        print("Processing Track as a Remix....")
        print("\n")
        spotify_track_dict_info = search_track_by_youtube_video_title(track,artist)
        if spotify_track_dict_info is None:
            spotify_track_dict_info = search_track_by_youtube_video_title(external_clean(track),artist)
            print(spotify_track_dict_info)
        else:
            print(spotify_track_dict_info)




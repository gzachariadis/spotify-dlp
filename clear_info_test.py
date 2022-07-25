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

"""
print("Video title identified as {}.".format(youtube_video_full_title).strip())

# Remove Things that might mess with identification

youtube_video_full_title = deEmojify(youtube_video_full_title)
print(youtube_video_full_title)
print("\n")

print("Regexes...")
youtube_video_full_title = re.sub(r"[\%\/\\\&\?\,\'\;\:\!\-\:\)]{2,}", '', youtube_video_full_title)
youtube_video_full_title = re.sub(r"\s{2,}", " ", youtube_video_full_title)
print(youtube_video_full_title)
print("\n")

print("clean_extra_from_title")
youtube_video_full_title = clean_extra_from_title(youtube_video_full_title)
print(youtube_video_full_title)
print("\n")


print("clean_unrequired_from_parenthesis")
"""

print(youtube_video_full_title)

youtube_video_full_title = deEmojify(youtube_video_full_title)
youtube_video_full_title = seperate_backslash_words(youtube_video_full_title)
youtube_video_full_title = replace_special_seperators(youtube_video_full_title)

print(youtube_video_full_title)

youtube_video_full_title = clean_unrequired_from_parenthesis(youtube_video_full_title)

print(youtube_video_full_title)

youtube_video_full_title = clean_second_dash(youtube_video_full_title)
youtube_video_full_title = capitalize_parenthesis(youtube_video_full_title)
youtube_video_full_title = convert_string(youtube_video_full_title)

print(youtube_video_full_title)

print("\n")

youtube_video_full_title = clean_brackets(youtube_video_full_title)

print(youtube_video_full_title)

print("\n")

"""
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

print("\n")
print(artist)
print(track)
"""
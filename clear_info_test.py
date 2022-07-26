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

# print(find_tags(youtube_video_full_title))

youtube_video_full_title = clean_unrequired_from_parenthesis(youtube_video_full_title)

youtube_video_full_title = clean_second_dash(youtube_video_full_title)
youtube_video_full_title = capitalize_parenthesis(youtube_video_full_title)
youtube_video_full_title = convert_string(youtube_video_full_title)

youtube_video_full_title = clean_brackets(youtube_video_full_title)

if (youtube_video_full_title.find(')') != -1):
    all_string_parenthesis = matching_parentheses(youtube_video_full_title)
   
    if (len(all_string_parenthesis.keys()) > 1):
        keys=list(sorted(all_string_parenthesis.keys()))  #get list of keys from dictionary
        keys.pop(0)  #Remove first in list of keys
        for key in keys:
            no_delete =  re.search(r"(?i)^((?!Remix|Mix|feat|featuring|Feat[.]{1}|ft[.]{1}).)*$",youtube_video_full_title, re.IGNORECASE)
            if no_delete is not None:
                youtube_video_full_title = youtube_video_full_title[:key-1] + youtube_video_full_title[all_string_parenthesis[key]+1:]
                print(youtube_video_full_title)

youtube_video_full_title = remove_quotes_from_string(youtube_video_full_title)

youtube_video_full_title = ade_seperate_track_artist(youtube_video_full_title)

youtube_video_full_title = strip_specific_words(youtube_video_full_title)

youtube_video_full_title = remove_miscellaneous(youtube_video_full_title)

print(youtube_video_full_title)

print(capitalize_words_correctly(youtube_video_full_title))

print(capitalize_parenthesis(youtube_video_full_title))

youtube_video_full_title = final_cleanup(youtube_video_full_title)

print(youtube_video_full_title)
print("\n")



"""

Shapov & Meg \ Nerak - Breathing Deeper

If I Die Young - the Band Per - Y-lyrics! :)


Rosa Linn - Snap - Armenia -
Rosa Linn - Snap - Armenia -
FREE DOWNLOAD

Welcome to Planet Urf | Login Screen - League of Legends

EVA – 失望した [Synthwave] 🎵 from Royalty Free Planet™

Kubbi / Cascade

Ouse - ｆａｒｃｒｙツ
Ouse -

Jay Sean - Down ft. Lil Wayne
Jay Sean - DOWN Ft. Lil Wayne

Εισβολέας Featuring O Live & Τάκι Τσαν-Όλοι Μαζί Τώρα

@area21

(2η εκδοχή)

Αμερικανικα / Εισβολέας Feat. Μάριος Νταβέλης

aespa 에스파 'Life's Too Short (English Ver.)' MV

Noisia - Diplodocus (Noisia's 'Outer Edges' Remix)
Noisia - Diplodocus (Noisia S Outer Edges' Remix)

Ariana Grande - pov

Laidback Luke & Made in June Paradise (Ft. Bright Lights) | Dim Mak Records

Lauren Spencer-Smith - Fingers Crossed (Lyrics)
Lauren Spencer - Smith - Fingers Crossed
Lauren Spencer - Smith - Fingers Crossed

Passenger | Let Her Go

Ferry Corsten - Reanimate ft Clairity

Sem Vox - Get It Up (DLDK Amsterdam 2016 Anthem)


Carl Nunes -white Dress


Above & Beyond & Justine Suissa - Alright Now (Above & Beyond Club Mix) Live at Ultra 2017



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
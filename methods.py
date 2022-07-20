from __future__ import print_function
import re
import music_metadata_filter.functions as functions
import pwd
import os 
import json
from difflib import SequenceMatcher
import math
from collections import Counter
import operator
import random

YOUTUBE_TRACK_FILTER_RULES = [
    r"^\W+", # Remove special characters from the beginning of strings
    r"\([^()]*\)", #  Remove Parenthesis
    r"[\(\)]", #  Remove Parenthesis
    r"[()]",
    r"^\s+|\s+$",
    r"\*+\s?\S+\s?\*+$",
    r"\[[^\]]+\].*",  # [whatever] something else
    r"\([^)]*version\)$", # Remove Version
    r"\.(avi|wmv|mpg|mpeg|flv|mp3|flac)$", # Remove the file extensions from title
    r"((with)?\s*lyrics?( video)?\s*)", # Remove Lyrics, video with etc.
    r"(Official Track Stream*)", #  Official Track Stream
    r"(of+icial\s*)?(music\s*)?video",  # (official)? (music)? video
    r"(of+icial\s*)?(music\s*)?audio",  # (official)? (music)? audio
    r"(ALBUM TRACK\s*)?(album track\s*)",  # (ALBUM TRACK)
    r"(COVER ART\s*)?(Cover Art\s*)",  # (Cover Art)
    r"\((.*?)subt(.*?)\)",  # (subtitles espanol) https://regex101.com/r/8kVFrm/1
    r"\((.*?)archives\)",  # (something ARCHIVES)
    r"\-? (.*?) archives",  # - something ARCHIVES)
    r"\(\s*of+icial\s*\)",  # (official)
    r"\(\s*[0-9]{4}\s*\)",  # (1999)
    r"^((([a-zA-Z]{1,2})|([0-9]{1,2}))[1-9]?\. )?", # Vinyl Track Number     # https://regex101.com/r/gHh2TB/4
    r"\(\s*([a-z]*\s)?\s*[0-9]{4}([a-z])?\s*([a-z]*\s?)?\)",  # (Techno 1990)
    r"\([A-Z]{1,10}[0-9]{1,4}\)",  # (CAT001) or (A1) https://regex101.com/r/JiLQST/2
    r"\(\s*([0-9]{4}\s*)?unreleased\s*([0-9]{4}\s*)?\)",  # (unreleased) https://regex101.com/r/Z5zD8l/1
    r"\(\s*(HD|HQ|ᴴᴰ)\s*\)$",  # HD (HQ)
    r"(HD|HQ|ᴴᴰ)\s*$",  # HD (HQ)
    r"(vid[\u00E9e]o)?\s?clip\sofficiel",  # video clip officiel
    r"of+iziel+es\s*",  # offizielles
    r"(?i)(?<!^)\bWith\b\s*.\s*(.*)", # remove everything after "with"
    r"vid[\u00E9e]o\s?clip",  # video clip
    r"\sclip",  # clip
    r"full\s*album",  # Full Album
    r"\(?live.*?\)?$",  # live
    r"([|]|[\\\/]{2,}).*$",  # | something
    r"\s*[0-9]{4}\s*",  # Track (Artist remix) 1999 https://regex101.com/r/vFHEvY/2
    r"\(+\s*\)+",  # Leftovers after e.g. (official video)
    r"\(.*[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{2,4}.*\)",  # (*01/01/1999*)
    r"#[a-z0-9]*",  # Hashtag something
    r"\s[.!$%(^$_+~=/}{`]{1,}\s", #Remove special characters from end and start of words
    r"(\W)\1+",
    r"(?i)\blive\b", #  Word Live case insensitive
    r"(?i)\bremix\b", # Word Remix case insensitive
    r"(?i)\bhd\b", # Word HD case insensitive
    r"(?i)\bvideo\b", # Word Video case insensitive
    r"(?i)\bvod\b", # Word VOD case insenstivie
    r"(?i)(?=^|\b)official\b", # Word Official Case Insensitive
    r"(?i)\blyrics\b", # Word Lyrics Case Insensitive
    r"(?i)\"{0,}[(]{1,}(?=^|\b)Audio\b\"{0,}[)]{1,}", # Audio In Parenthesis
    r"(?i)\"{0,}(?=^|\b)Audio\b\"{0,}", #  Audio Case Insensitive
    r"(?i)\s{0,1}v{1}s{1,}[.]{0,}\s\s*.\s*(.*)", # Remove everything after vs
    r"(?i)\s{0,1}v{1}[e]{1,}[r]{1,}s{1,}[u]{1,}[s]{1,}[.]{0,}\s\s*.\s*(.*)", # Remove everything after versus
    r"[#@]\w+", 
    r"\s*$", #  remove multiple spaces
    r"(?<!^)f[e]{0,}[a]{0,}t[.]{0,}[u]{0,}[r]{0,}[i]{0,}[n]{0,}[g]{0,}\b\s*.\s*(.*)", # Remove everything after feat, feat. , featuring. etc.
    r"(?i)(?<!^)\bvs[.]{0,}\b\s*.\s*(.*)", #  Remove everything after vs . 
    r"(?i)(?<!^)\bf[e]{0,}[a]{0,}t[u]{0,}[r]{0,}[i]{0,}[n]{0,}[g]{0,}\b\s*.\s*(.*)", # remove everything after feat.
    r"(?i)(?<!^)\b[b]{1,}[y]{1,}\b\s{1,}\w+\s{0,}$", # remove everything after by if only one word after and end of string
    r"(?i)(?<!^)\b[b]{1,}[y]{1,}\b\s{1,}\w+\s{1,}\w+\s{1,}$",
    r"^(?:(?:[0-9]{2}[:\/,]){2}[0-9]{2,4})$", # Remove Dates
    r"[0-9]{4}\-[0-9]{2}\-[0-9]{2}",  # Remove Dates
    r"\d\d\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4}", # Remove Dates
    r"\s{1,}([1-3][0-9]{3})(\s|$)", #  Remove dates
    r"\s[A-Za-z][.]{1}\s", # Remove Middle names eg. a single letter word [.] dot
    r"^\W+",
    r"(?i)(?<!^)\b[-]\b\s*.\s*(.*)",
    r"^((([a-zA-Z]{1,2})|([0-9]{1,2}))[1-9]?\. )?",  # Remove vinyl track number -https://regex101.com/r/gHh2TB/4
    r"((PREMIERE|INCOMING)\s*:)?", # Remove "PREMIERE: " or "INCOMING: " - https://regex101.com/r/nG16TF/3
    r"^[^α-ωΑ-ΩοόΟοά-ώa-zA-Z0-9\W]+", # Remove special characters before the start of the string
    r"(?i)(?<!^)\b[x]\b\s*.\s*(.*)" #  Remove everything after a single "x" eg. Marting Garrix x Avicii
]

ARTIST_FILTER_RULES = [
    r"^\W+", # Remove special characters from the beginning of strings
    r"(?<!^)f[e]{0,}[a]{0,}t[.]{0,}[u]{0,}[r]{0,}[i]{0,}[n]{0,}[g]{0,}\b\s*.\s*(.*)", # Remove everything after feat, feat. , featuring. etc.
    r"(?i)(?<!^)\bvs[.]{0,}\b\s*.\s*(.*)", #  Remove everything after vs . 
    r"(?i)(?<!^)\bf[e]{0,}[a]{0,}t[u]{0,}[r]{0,}[i]{0,}[n]{0,}[g]{0,}\b\s*.\s*(.*)", # remove everything after feat.
    r"(?i)(?<!^)\b[x]\b\s*.\s*(.*)", #  Remove everything after a single "x" eg. Marting Garrix x Avicii
    r"\s[A-Za-z][.]{1}\s", # Remove Middle names eg. a single letter word [.] dot
    r"^[^α-ωΑ-ΩοόΟοά-ώa-zA-Z0-9\W]+", # Remove special characters before the start of the string
    r"(?i)\s{0,1}v{1}s{1,}[.]{0,}\s\s*.\s*(.*)", # Remove everything after vs
    r"(?i)\s{0,1}v{1}[e]{1,}[r]{1,}s{1,}[u]{1,}[s]{1,}[.]{0,}\s\s*.\s*(.*)", # Remove everything after versus
    r"#[a-z0-9]*",  # Hashtag something
    r"\s[.!$%(^$_+~=/}{`]{1,}\s", #Remove special characters from end and start of words
    r"([|]|[\\\/]{2,}).*$",  # | something
    r"\(\s*of+icial\s*\)",  # (official)
    r"^((([a-zA-Z]{1,2})|([0-9]{1,2}))[1-9]?\. )?", # Vinyl Track Number     # https://regex101.com/r/gHh2TB/4
    r"(?i)VEVO.*$",   #VEVO from Artist name
    r"(?i)(?=^|\b)official\b",  # Remove Official
    r"\((.*)\)",
    r"\[.*?\]",
    r"^\W+",
    r"(?i)\bft\b\s*.\s*(.*)",
    r"(?i)\s&{1}\s\s*.\s*(.*)",
    r"(?i)\s{0,1},{1}\s\s*.\s*(.*)",
    r"(?:\[[^][]*])",
    r"(?i)\bft[u]{0,}[r]{0,}[i]{0,}[n]{0,}[g]{0,}\b\s*.\s*(.*)",
    r"\([^()]*\)",
    r"[{}()!@#$]",
    r"\([^()]*\)",
    r"\[[^\]]+\]",
    r"((PREMIERE|INCOMING)\s*:)?", # Remove "PREMIERE: " or "INCOMING: " - https://regex101.com/r/nG16TF/3
    r"(?i)(?<!^)\b[&]\b\s*.\s*(.*)",
    r"^((([a-zA-Z]{1,2})|([0-9]{1,2}))[1-9]?\. )?",   # Remove vinyl track number -https://regex101.com/r/gHh2TB/4
    r"(?i)(?<!^)\s*[&]{1,}\s*.\s*(.*)"
]

CLEAR_FEATURING_ARTISTS = [
    r"(?i)^\s{0,}f[e]{0,}[a]{0,}t[.]{0,}[u]{0,}[r]{0,}[i]{0,}[n]{0,}[g]{0,}\W+\b",
    r"(?i)^\s{0,}vs[.]{0,}\W+\b",
    r"(?i)^\s{0,}[x]{0,}\W+\b",
    r"(?i)\s[A-Za-z]{1}\s",
    r"(?i)^[^α-ωΑ-ΩοόΟοά-ώa-zA-Z0-9\W]+",
    r"(?i)\s[.!$%(^$_+~=/}{`]{1,}\s",
    r"(?i)^\s{0,}[&]{1,}\W+\b",
    r"(?i)^\s{0,}[a]{1,}[n]{1,}[d]{1,}\W+\b"
]

CLEAR_VIDEO_TITLE = [
    r"\.(avi|wmv|mpg|mpeg|flv|mp3|flac)$", # Remove the file extensions from title
    r"((with)?\s*lyrics?( video)?\s*)", # Remove Lyrics, video with etc.
    r"\(\s*(HD|HQ|ᴴᴰ)\s*\)$",  # HD (HQ)
    r"(HD|HQ|ᴴᴰ)\s*$",  # HD (HQ)
    r"(?i)\"{0,}[(]{1,}(?=^|\b)Audio\b\"{0,}[)]{1,}",
    r"(vid[\u00E9e]o)?\s?clip\sofficiel",  # video clip officiel
    r"of+iziel+es\s*",  # offizielles
    r"vid[\u00E9e]o\s?clip",  # video clip
    r"\sclip",  # clip
    r"\s*$", #  remove multiple spaces
    r"((PREMIERE|INCOMING)\s*:)?", # Remove "PREMIERE: " or "INCOMING: " - https://regex101.com/r/nG16TF/3
    r"^[^α-ωΑ-ΩοόΟοά-ώa-zA-Z0-9\W]+", # Remove special characters before the start of the string
    r"(?i)\blive\b", #  Word Live case insensitive
    r"(?i)\bhd\b", # Word HD case insensitive
    r"(?i)\bvideo\b", # Word Video case insensitive
    r"(?i)\bvod\b", # Word VOD case insenstivie
    r"(?i)(?=^|\b)official\b", # Word Official Case Insensitive
    r"(?i)\blyrics\b", # Word Lyrics Case Insensitive
    r"[.!$%(^$_+~=/}{`\-]{1,}\s{0,}$",
    r"\s{1,}[.!$%(^$_+~=/}{`\-]{1,}\s{0,}$"
]

CLEAR_TRACK = [
    r"\.(avi|wmv|mpg|mpeg|flv|mp3|flac)$", # Remove the file extensions from title
    r"((with)?\s*lyrics?( video)?\s*)", # Remove Lyrics, video with etc.
    r"\(\s*(HD|HQ|ᴴᴰ)\s*\)$",  # HD (HQ)
    r"((with)?\s*lyrics?( video)?\s*)", # Remove Lyrics, video with etc.
    r"(HD|HQ|ᴴᴰ)\s*$",  # HD (HQ)
    r"(vid[\u00E9e]o)?\s?clip\sofficiel",  # video clip officiel
    r"of+iziel+es\s*",  # offizielles
    r"vid[\u00E9e]o\s?clip",  # video clip
    r"\sclip",  # clip
    r"^\W*",
    r"^[^\w.]*",
    r"^\W+", # Remove special characters from the beginning of strings
    r"\s*$", #  remove multiple spaces
    r"((PREMIERE|INCOMING)\s*:)?", # Remove "PREMIERE: " or "INCOMING: " - https://regex101.com/r/nG16TF/3
    r"^[^α-ωΑ-ΩοόΟοά-ώa-zA-Z0-9\W]+", # Remove special characters before the start of the string
    r"(?i)\blive\b", #  Word Live case insensitive
    r"(?i)\bhd\b", # Word HD case insensitive
    r"(?i)\bvideo\b", # Word Video case insensitive
    r"(?i)\bvod\b", # Word VOD case insenstivie
    r"(?i)(?=^|\b)official\b", # Word Official Case Insensitive
    r"(?i)\blyrics\b", # Word Lyrics Case Insensitive
    r"[.!$%(^$_+~=/}{`\-]{1,}\s{0,}$",
    r"^[^α-ωΑ-ΩοόΟοά-ώa-zA-Z0-9\W]+", # Remove special characters before the start of the string
    r"(Official Track Stream*)", #  Official Track Stream
    r"(of+icial\s*)?(music\s*)?video",  # (official)? (music)? video
    r"(of+icial\s*)?(music\s*)?audio",  # (official)? (music)? audio
    r"(ALBUM TRACK\s*)?(album track\s*)",  # (ALBUM TRACK)
    r"(COVER ART\s*)?(Cover Art\s*)",  # (Cover Art)
    r"(?i)\"{0,}(?=^|\b)Audio\b\"{0,}" #  Audio Case Insensitive
    r"[.!$%(^$_+~=/}{`\-]{1,}\s{0,}$", # Special Characters at the end of string
    r"\s{1,}[.!$%(^$_+~=/}{`\-]{1,}\s{0,}$" # Spaces + special character at the end of string
    r"\s{1,}%" # Spaces at the end of string
]

GENRES_DICTIONARY = {
    "edm" : "Electronic Dance Music",
    "dnb" : "Drum and Bass",
    "alternative rock" : "Alternative Rock", 
    "hip hop" : "Hip-Hop",
    "dance" : "Electronic Dance Music",
    "eurodance" : "Electronic Dance Music",
    "rap" : "Hip-Hop",
    "speedrun" : "Chill Electronic",
    "mpb" : "Latin America Music",
    "r-n-b" : "Rhythm & Blues",
    "r&b"  : "Rhythm & Blues",
    "rock-n-roll" : "Rock & Roll",
    "indie pop rap" : "Rap",
    "ska" : "Jamaican Ska",
    "dub" : "Electronic Reggae",
    "electronic" : "Electronic",
    "jump up" : "Drum and Bass",
    "popwave" : "Pop & Dance",
    "sky room" : "Electronic Dance Music",
    "melbourne bounce international" : "Melbourne Bounce",
    "funk" : "Jazz",
    "scorecore" : "Soundtracks",
    "epicore" : "Metal",
    "funk metal" : "Heavy Metal",
    "neo mellow" : "",
    "bossanova" : "Samba",
    "house" : "Electro House",
    "k-pop" : "Pop & Dance",
    "j-dance" : "Pop & Dance",
    "j-idol" : "Pop & Dance",
    "j-pop" : "Pop & Dance",
    "j-rock" : "Rock",
    "stomp and holler" : "Chill Synthwave",
    "malay" : "Traditional Malay Music",
    "mandopop" : "Pop & Dance",
    "road-trip" : "Soundtrack",
    "classic" : "Classical Music",
    "philippines-opm" : "Pop & Dance",
    "pagode" : "Brazilian Country-Folk",
    "happy" : "Indie Jazz",
    "future bass" : "Electonic Dance Music",
    "dubstep" : "Dubstep",
    "complextro" : "Electro house",
    "trap" : "Trap",
    "country" : "Country",
    "traprun" : "Trap",
    "alt z" : "Electronic",
    "europop" : "Pop & Dance",
    "urban contemporary" : "Hip-Hop",
    "dark clubbing" : "Electronic",
    "big room" : "Electro House",
    "techno" :  "Techno",
    "g funk" : "Rap",
    "metal" : "Metal",
    "folk-pop" : "Pop & Dance",
    "nightrun" : "Melodic Rock",
    "idm" : "Ambient Electronica",
    "indie-pop" : "Indie Electronic",
    "alt-rock" : "Alternative Rock",
    "black-metal" : "Black Metal",
    "chicago-house" : "Electro House",
    "death-metal" : "Death Metal",
    "deep-house" : "Electro House",
    "detroit-techno" : "Detroit Techno Music",
    "drum-and-bass" : "Drum & Bass",
    "hard-rock" : "Accoustic Hard Rock",
    "heavy-metal" : "Heavy Metal",
    "hip-hop" : "Hip-Hop",
    "honky-tonk" : "Country Music",
    "metal-misc" : "Industrial Metal",
    "minimal-techno" : "Minimal Techno",
    "new-age" : "Artistic New Age",
    "new-release" : "Modern Pop",
    "chiptune" : "8-Bit",
    "pop-film" : "Art Pop",
    "video game music" : "Chill Electronic",
    "nu metal" : "Metal",
    "post-dubstep" : "Post Dubstep",
    "power-pop" : "Pop Rock",
    "progressive-house" : "Electro House",
    "tropical house" : "Electro House",
    "electropop" : "Electronic Pop",
    "psych-rock" : "Psychedelic Rock",
    "punk-rock" : "Punk Rock",
    "pop punk" : "Pop-Punk",
    "rainy-day" : "Alternative Rock",
    "show-tunes" : "Traditional Pop",
    "singer-songwriter" : "Folk Accoustic",
    "synth-pop" : "Post Techno Pop",
    "trip-hop" : "Trip Hop",
    "post-grung" : "Rock",
    "work-out" : "Garage Hip Hop",
    "world-music" : "Contemporary Folk Music",
    "pop" : "Modern Pop",
    "gaming" : "Electronic Pop",
    "vapor twitch" : "Electonic Dance Music",
    "rockabilly" : "Rock & Roll",
    "sad" : "Indie Rock",
    "native american" : "Country",
    "sleep" : "Ambient",
    "brostep" : "Dubstep",
    "mellow" : "Drum & Bass",
    "study" : "Classical Music",
    "tropical" : "Tropical House",
    "summer" : "Vibe Pop"
}

SEPARATORS = [
    ' -- ', '--', ' ~ ', ' - ', ' – ', ' — ',
    ' // ', '-', '–', '—', ':', '|', '///', '/', '&','►'
]

ARTIST_SEPERATORS = ["&",",","x","ft","ft.","featuring","feat.","feat"]

CLEAN_ALBUM_DICTIONARY = [
     r"(?i)\s{1,}(?<!^)[(]{1,}original[)]{1,}\s{0,}$",
     r"(?i)(?<!^)\s{1,}[|]{1,}.*$",
     r"(?i)\s{1,}(?<!^)[(]{1,}Mixed by.*[)]{1,}\s{0,}$",
     r"(?i)\s{1,}(?<!^)[(]{1,}Presented by.*[)]{1,}\s{0,}$",
     r"(?i)\s{1,}(?<!^)[(]{1,}Dj Mix.*[)]{1,}\s{0,}$",
     r"(?i)\s{1,}(?<!^)[(]{1,}Live at.*[)]{1,}\s{0,}$",
     r"(?i)(?<!^)(Live at.*)$",
     r"(?i)(?<!^)\[[^()]*\]$",
     r"(?i)(?<!^)(Mixed by.*)$",
     r"(?i)(?<!^)(Live In.*)$",
     r"(?i)\s{1,}(?<!^)[(]{1,}Continuous Dj Mix.*[)]{1,}\s{0,}$",
     r"(?i)\s{1,}(?<!^)[(]{1,}Live*[)]{1,}\s{0,}$",
     r"\,(?=\s{1,}\bPt\b)",
     r"\,(?=\s{1,}\bVol\b)",
     r"\,(?=\s{1,}\bVolume\b)",
     r"\,(?=\s{1,}\bPts\b)",
     r"[\\.,;:\-_]+$",
     r"(?i)\:\s{1,}the$",
     r"[\\.,;:\()-_]+$"
]

Escape_Words = ["the","and","are","is","was","were","by","of","no","so"]

def clean_track_for_extraction(my_str):
    for regex in CLEAR_TRACK:
        my_str = re.sub(regex, "", my_str, flags=re.IGNORECASE)
    
    find_paren = set(find(my_str,"("))

    if find_paren is not None:
        if len(find_paren) != 0:
            start = list(set(find(my_str,"(")))[0]
            replacement = re.sub(r"[^\w.\s]",'', my_str[start:], flags=re.IGNORECASE)
            my_str = my_str[:start] + "- " + convert_string(replacement)

    return my_str

def find(str, ch):
    for i, ltr in enumerate(str):
        if ltr == ch:
            yield i

def clear_title(title):
    for regex in CLEAR_VIDEO_TITLE:
        title = re.sub(regex, "", title, flags=re.IGNORECASE)
    
    return title

def find_correct_seperator_index(seperator_object):
    temporary_list = []
    if (len(seperator_object.keys())) > 1:
        for key,value in seperator_object.items():
            for i in value:
                temporary_list.append(i)
        return sorted(temporary_list)[len(temporary_list)-1]
    else:
        for key,value in seperator_object.items():
            return list(value)[len(value)-1]

# Given the fulltitle of a youtube video, termine where's the last seperator object
# between artist and track title is
def find_separator(title):
    seperator_object = {}
    if title is None or len(title) == 0:
        return
    for sep in SEPARATORS:
        try:
            if sep not in ARTIST_SEPERATORS:
                indexes = set((find(title,sep)))
            if indexes:
                seperator_object[sep] = sorted(indexes)
        except:
            continue
    return seperator_object

def clean_artist(artist):

    for regex in ARTIST_FILTER_RULES:
        artist = re.sub(regex, "", artist, flags=re.IGNORECASE)

    while True:
        # Track (Artist remix) (Remove this) (And this)  https://regex101.com/r/0meJko/2
        groups = re.findall(r"\(.*\)\s*(\((.*)\))", artist)
        if len(groups) > 0:
            artist = artist.replace(groups[0][0], "")
        else:
            break
    
    return artist

def capitalize_parenthesis(my_str):
    for match in re.finditer(r"\(([^()]+)\)", my_str):
        parenthesis = my_str[match.start()+1:match.end()-1].split()
        new_parenthesis = []
        for w in parenthesis:
            new_parenthesis.append(w.capitalize())
        new_substring = ' '.join(new_parenthesis)

        my_str = my_str[:match.start()+1] + new_substring + my_str[match.end()-1:]
    return my_str

def convert_string(my_str):
    capitalize_parenthesis(my_str)
    word_list = []
    for word in my_str.split():
        if word.lower() in Escape_Words:
            word_list.append(word.lower())
        else:
            if word.isupper() is False:
                if int((len(word))) > 3:
                    word_list.append(word.capitalize())
                else:
                    word_list.append(word)
            elif word.isupper() is True:
                word_list.append(word.capitalize())
            else:
                word_list.append(word)
    cleansed_word = ' '.join(word_list)
    cleansed_word = capitalize_parenthesis(cleansed_word)
    return cleansed_word

# Remove Emoji's From track
def deEmojify(track):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',track)

def filter_with_filter_rules(text):
    for regex in YOUTUBE_TRACK_FILTER_RULES:
        text = re.sub(regex, "", text, flags=re.IGNORECASE)

    while True:
        # Track (Artist remix) (Remove this) (And this)  https://regex101.com/r/0meJko/2
        groups = re.findall(r"\(.*\)\s*(\((.*)\))", text)
        if len(groups) > 0:
            text = text.replace(groups[0][0], "")
        else:
            break

    return text

# Clean the Title of a Song
def clean_track(track):

    track = filter_with_filter_rules(track)

    # Apply External Track Filters for Title
    track = functions.remove_remastered(track)
    track = functions.remove_version(track)
    track = functions.youtube(track)
    track = functions.fix_track_suffix(track)
    track = functions.remove_live(track)
    track = functions.remove_zero_width(track)
    track = functions.remove_clean_explicit(track)
    track = functions.remove_reissue(track)
    track = functions.remove_parody(track)
    track = functions.remove_feature(track)
    track = functions.remove_zero_width(track)
    track = functions.replace_nbsp(track)
    track = functions.remove_clean_explicit(track)
    track = functions.remove_live(track)
    track = functions.remove_reissue(track)
    track = functions.remove_remastered(track)
    track = functions.remove_parody(track)
    track = functions.remove_version(track)
    
    # Remove special characters from end and start of words
    track_words = track.split()
    for word in track_words:
        word.strip(")(!~/\_+.* ")

    # Join back the string from the list
    track = ' '.join(track_words)

    # Remove all leading and trailing whitespaces
    track = track.strip()

    # Remove special characters from end and start of words
    if track.find("-"):
        track = re.sub(r"\s{1,}[-]\s{1,}.*","",track)
    
    # Remove Non-English Characters - Mainly chinese
    track = ''.join(filter(lambda character:ord(character) < 0x3000,track))

    # Remove Parenthesis
    track = re.sub("([\(\[]).*?([\)\]])", "\g<1>\g<2>",track)

    # Remove Non-English Characters - Mainly chinese
    track = ''.join(filter(lambda character:ord(character) < 0x3000,track))

    # Remove anything within double quotes  - requires fixing
    track = re.sub('".*?"', '', track)

    track = track.replace("~", "")

    # Remove Emojies
    track = deEmojify(track)

    # Remove multiple spaces in artist and title
    track = " ".join(track.split())
    track = convert_string(track)

    return track

def clean_album_names(album_name):
    for regex in CLEAN_ALBUM_DICTIONARY:
        album_name = re.sub(regex, "", album_name, flags=re.IGNORECASE)
    return album_name

def output_track_info(artist,track):
    if artist is not None:
        if track:
            print("Track seems to be {0} by {1}".format(track,artist))

def get_username():
    return pwd.getpwuid(os.getuid())[0]

def find_values(id, json_repr):
    results = []

    def _decode_dict(a_dict):
        try:
            results.append(a_dict[id])
        except KeyError:
            pass
        return a_dict

    json.loads(json_repr, object_hook=_decode_dict) # Return value ignored.
    return results

def search_dict(search_parameter,dict):
    for key in dict.keys():
        if key == search_parameter:
            return key, dict[key]

def find_key_for(input_dict, value):    
    result = []
    for k, v in input_dict.items():
        if k in value:
            result.append(k)
    return result

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()*100

def remove_dupls(x):
  return list(dict.fromkeys(x))

def remove_all_on_predicate(predicate, list_):
    deserving_removal = [elem for elem in list_ if predicate(elem)]
    for elem in deserving_removal:
        list_.remove(elem)
    return None

def select_randomly(x):
    secure_random = random.SystemRandom()
    return secure_random.choice(x)

def clean_up_genres(genres_list):
    cleaned_genres = []
    print(genres_list)
    for genre in genres_list:
        search_genres = search_dict(genre, GENRES_DICTIONARY)
        search_string = genre.split()
        if search_genres:
            cleaned_genres.append(search_genres[1])

        for word in search_string:
            if word in GENRES_DICTIONARY:
                if search_dict(word, GENRES_DICTIONARY)[1] not in cleaned_genres:
                    cleaned_genres.append(search_dict(word,GENRES_DICTIONARY)[1])

            for key,value in GENRES_DICTIONARY.items():
                check_artist = math.trunc(similar(str(word).lower().strip(),str(key).lower().strip()))
                if int(check_artist) >= int(80):
                    if value not in cleaned_genres:
                        cleaned_genres.append(value)
   
    if cleaned_genres:
        # Count the values in the dictionary and return max value
        a = dict(Counter(cleaned_genres))

        print(a)

        if int(max(a.values())) is int(min(a.values())):
            # Remove Duplicates if still exist 
            mylist = remove_dupls(cleaned_genres) 
            
            # if multiple genres show once and no max value, select one randomly
            if len(mylist) > 1:
                genre = str(select_randomly(mylist)).strip()
                print("Can't determine a dominant genre...Choosing {} from list of artist genres.".format(genre))
                return genre
            else:
                # Return first item of list
                genre = str(mylist[0]).strip()
                print("Processed genre as {}.".format(genre).strip())
                return genre.strip()
        else:
            # Find the largest value in the dictionary 
            new_ma_val = max(a.items(), key=operator.itemgetter(1))[0]
        
            # Remove everything that's not max value
            remove_all_on_predicate(lambda x: new_ma_val not in x, cleaned_genres)
        
            # Remove Duplicates if still exist 
            mylist = remove_dupls(cleaned_genres) 
            
            # if multiple genres show once and no max value, select one randomly
            if len(mylist) > 1:
                genre = str(select_randomly(mylist)).strip()
                print("Can't determine a dominant genre...Choosing {} from list of artist genres.".format(genre))
                return genre
            else:
                # Return first item of list
                genre = str(mylist[0]).strip()
                print("Processed genre as {}.".format(str(genre)).strip())
                return genre.strip()
    return 

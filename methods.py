from __future__ import print_function
from ast import pattern
from calendar import c
from curses.ascii import islower
import re
from sys import flags
from turtle import title
import music_metadata_filter.functions as functions
import pwd
import os 
import json
from difflib import SequenceMatcher
import math
from collections import Counter
import operator
import random
import emoji
import enchant

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
    r"[“]\s{0,}[”]",
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
    r"\s{1,}$",
    r"(?i)\bft\b\s*.\s*(.*)",
    r"(?i)\s&{1}\s\s*.\s*(.*)",
    r"(?i)\s{0,1},{1}\s\s*.\s*(.*)",
    r"(?:\[[^][]*])",
    r"(?i)\bft[u]{0,}[r]{0,}[i]{0,}[n]{0,}[g]{0,}\b\s*.\s*(.*)",
    r"\([^()]*\)",
    r"[{}()!@#$]",
    r"\([^()]*\)",
    r"[“]\s{0,}[”]",
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
    r"[“]\s{0,}[”]",
    r"(?i)^[^α-ωΑ-ΩοόΟοά-ώa-zA-Z0-9\W]+",
    r"(?i)\s[.!$%(^$_+~=/}{`]{1,}\s",
    r"(?i)^\s{0,}[&]{1,}\W+\b",
    r"(?i)^\s{0,}[a]{1,}[n]{1,}[d]{1,}\W+\b"
]

FIRST_LEVEL = [
    r"\.(avi|wmv|mpg|mpeg|flv|mp3|flac)$", # Remove the file extensions from title
    r"((with)?\s*lyrics?( video)?\s*)", # Remove Lyrics, video with etc.
    r"\(\s*(HD|HQ|ᴴᴰ)\s*\)$",  # HD (HQ)
    r"(HD|HQ|ᴴᴰ)\s*$",  # HD (HQ)
    r"(?i)\"{0,}[(]{1,}(?=^|\b)Audio\b\"{0,}[)]{1,}",
    r"(vid[\u00E9e]o)?\s?clip\sofficiel",  # video clip officiel
    r"of+iziel+es\s*",  # offizielles
    r"vid[\u00E9e]o\s?clip",  # video clip
    r"\sclip",  # clip
    r"[“]\s{0,}[”]",
    r"[(]\s{0,}[)]", # Remove Empty Parenthesis with spaces or without
    r"\s{0,}[“”]\s{0,}",
    r"\s*$", #  remove multiple spaces from end of string
    r"((PREMIERE|INCOMING)\s*:)?", # Remove "PREMIERE: " or "INCOMING: " - https://regex101.com/r/nG16TF/3
    r"^[^α-ωΑ-ΩοόΟοά-ώa-zA-Z0-9\W]+", # Remove special characters before the start of the string
    r"(?i)\blive\b", #  Word Live case insensitive
    r"(?i)\bhd\b", # Word HD case insensitive
    r"(?i)\bvideo\b", # Word Video case insensitive
    r"(?i)\bvod\b", # Word VOD case insenstivie
    r"(?i)(?=^|\b)official\b", # Word Official Case Insensitive
    r"(?i)\blyrics\b", # Word Lyrics Case Insensitive
    r"[.!$%(^$_+~=/}{`\-]{1,}\s{0,}$",
    r"[(]\s{0,}[)]", #  parenthesis
    r"\s{1,}[.!$%(^$_+~=/}{`\-]{1,}\s{0,}$"
]

SECOND_LEVEL = [
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
    "synthwave" : "Synthwave",
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
    ' -- ', '--', ' ~ ', ' - ', ' – ', ' — ', ' ／ ', ' | ', ' // ', '-', '–', '—', ':', '|', '///', '/', '&','►'
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

CLEAN_BRACKETS = [
    r"(?i)\[{1,}\s{0,}Official\s{0,}(?:Music)?\s{0,}Video\]{1,}",
    r"(?i)\[{1,}\s{0,}Official\s{0,}(?:Music)?\s{0,}Visualizer\]{1,}",
    r"(?i)\[{1,}\s{0,}(?:Music)?\s{0,}Visualizer\]{1,}",
    r"(?i)\[{1,}\s{0,}(?:Audio)?\s{0,}?\s{0,}(?:With)?\s{0,}?\s{0,}Lyrics\s{0,}?\s{0,}(?:Included)?\s{0,}?\s{0,}\]{1,}",    # Lyrics   # Audio with Lyrics     # Lyrics included  # With Lyrics
    r"(?i)\[{1,}\s{0,}(?:Official)?\s{0,}?\s{0,}(?:)?\s{0,}?\s{0,}Lyrics\s{0,}?\s{0,}(?:Video)?\s{0,}?\s{0,}\]{1,}",  # Official Lyrics Video
    r"(?i)\[{1,}\s{0,}(?:Official)?\s{0,}?\s{0,}(?:)?\s{0,}?\s{0,}Lyric\s{0,}?\s{0,}(?:Video)?\s{0,}?\s{0,}\]{1,}",   # Official Lyric Video
    r"(?i)\[{1,}\s{0,}(?:Official)?\s{0,}?\s{0,}(?:)?\s{0,}?\s{0,}Audio\s{0,}?\s{0,}(?:\d{4})?\s{0,}?\s{0,}\]{1,}",   # Audio # Official Audio # Official Audio [date]
    r"(?i)\[{1,\s{0,}}(?:Official)?\s{0,}?\s{0,}(?:)?\s{0,}?\s{0,}Visualizer\s{0,}?\s{0,}\]{1,}",  # Official Visualizer # Visualizer
    r"(?i)\[{1,}\s{0,}(?:Version)?\s{0,}?\s{0,}(?:Release)?\s{0,}?\s{0,}\d{4}\s{0,}?\s{0,}(?:Version)?\s{0,}?\s{0,}\]{1,}",  # Just a Year
    r"(?i)\[{1,}\s{0,}(?:Cover)?\s{0,}\s{0,}(?:Album)?\s{0,}\s{0,}Art\s{0,}\]{1,}", # Cover or Cover Art or Cover Album Art
    r"(?i)\[{1,}\s{0,}(?:Album)?\s{0,}\s{0,}(?:Cover)?\s{0,}\s{0,}Art\s{0,}\]{1,}", # Album Cover Art
    r"(?i)\[{1,}\s{0,}(?:Album)?\s{0,}\s{0,}(?:Art)?\s{0,}\s{0,}Cover\s{0,}\]{1,}", # Album Art Cover
    r"(?i)\[{1,}\s{0,}(?:Official)?\s{0,}\s{0,}(?:HD)?\s{0,}\s{0,}(?:HQ)?\s{0,}\s{0,}(?:High Definition)?\s{0,}\s{0,}Video\s{0,}\]{1,}", # Official HD Video # Official Video HD # HD Video  # HQ
    r"(?i)\[{1,}\s{0,}(?:360°)?\s{0,}\s{0,}(?:360)?\s{0,}\s{0,}(?:Official)?\s{0,}\s{0,}Visualizer\s{0,}\]{1,}", # Official Visualizer  # (360° Visualizer)
    r"(?i)\[{1,}\s{0,}(?:Official)?\s{0,}\s{0,}(?:Lyric)?\s{0,}\s{0,}(?:Music)?\s{0,}\s{0,}Video\s{0,}\]{1,}",  # Lyric Video # Our Lyric Video # Music Video
    r"(?i)\[{1,}\s{0,}Bass\s{0,}\s{0,}Boosted\s{0,}\]{1,}", # Bass Boosted
    r"(?i)\[{1,}\s{0,}Official.*Version\s{0,}\]{1,}", # Official Whatever Version
    r"(?i)\[{1,}\s{0,}Official\s{1,}Explicit.*\s{0,}\]{1,}", # Official Explicit Whatever
    r"(?i)\[{1,}\s{0,}Video\s{0,}\]{1,}", # Video  
    r"(?i)\[{1,}\s{0,}Live\s{1,}(?:from)?\s{0,}\s{0,}(?:at)?\s{0,}\s{0,}.*\s{0,}\]{1,}",  # Live from or at 
    r"(?i)\[{1,}(?:Explicit)?\s{0,}?\s{0,}(?:Static)?\s{0,}?\s{0,}Video\s{0,}?\s{0,}(?:Static)?\s{0,}?\s{0,}\]{1,}",     # Static Video
    r"(?i)\[{1,}\s{0,}Explicit\s{0,}\]{1,}", # Explicit
    r"(?i)\[{1,}\s{0,}ID\s{0,}\]{1,}", # ID 
    r"(?i)\[{1,}DJ[-\s]{1,}Set.*\s{0,}\]{1,}", # Dj-Set
    r"(?i)\[{1,}\s{0,}\s{0,}\s{0,}(?:High)?\s{0,}\s{0,}(?:Best)?\s{0,}\s{0,}Quality\s{0,}\]{1,}",  # Best Quality - High Quality
    r"(?i)\[{1,}\s{0,}\s{0,}\s{0,}From\s{0,}.*\]{1,}",  # From ...
    r"(?i)\[{1,}(?:Official)?\s{0,}?\s{0,}(?:4K)?\s{0,}?\s{0,}Video\s{0,}\]{1,}",  # Official 4K Video
    r"(?i)\[{1,}Official\s{0,}(?:Song)?\s{0,}?\s{0,}\]{1,}", # Official Song
    r"(?i)\[{1,}Oficial\s{0,}\]{1,}", # Official misworded 
    r"(?i)\[{1,}\s{0,}Directed\s{1,}by\s{0,}.*\]{1,}",  # Directed by 
    r"(?i)\[{1,}\s{0,}Mix[e]{0,}[d]{0,}\s{1,}by\s{0,}.*\]{1,}",  # Mixed by 
    r"(?i)\[{1,}\s{0,}(?:360°)?\s{0,}\s{0,}(?:360)?\s{0,}\s{0,}(?:Official)?\s{0,}\s{0,}Video\s{0,}\]{1,}",   # 360 Video
    r"(?i)\[{1,}\s{0,}Dir[.]{1,}\s{1,}by\s{0,}.*\]{1,}", # Dir. by
    r"(?i)\[{1,}\s{0,}Dir[.]{1,}\s{0,}.*\]{1,}", # Dir.
    r"(?i)\[{1,}\s{0,}(?:\b\w+){0,1}\s+Translation\s{0,}\]{1,}", # any word + Translation
    r"(?i)\[{1,}\s{0,}4K\s{0,}\]{1,}", # 4K
    r"(?i)\[{1,}\s{0,}Presents\s{1,}.*\s{0,}\]{1,}", # Presents
    r"(?i)\[{1,}\s{0,}(?:Vevo\s{1,})?\s{0,}\s{0,}Presents\s{1,}.*\s{0,}\]{1,}",  # Vevo Presents
    r"(?i)\[{1,}(?:Video)?\s{0,}?\s{0,}Time[-]{0,1}lapse\s{0,}?\s{0,}(?:Video)?\s{0,}?\s{0,}(?:Vid[.]{0,1})?\s{0,}?\s{0,}\]{1,}",  # Timelapse or Time-lapse + optional Video
    r"(?i)\[{1,}(?:Animated)?\s{0,}?\s{0,}Video\s{0,}?\s{0,}(?:Animated)?\s{0,}?\s{0,}\]{1,}", # Animated Video
    r"(?i)\[{1,}(?:Animated)?\s{0,}?\s{0,}Vid[.]{0,1}\s{0,}?\s{0,}(?:Animated)?\s{0,}?\s{0,}\]{1,}", # Animated Vid
    r"(?i)\[{1,}(?:Lip)?\s{0,}?\s{0,}(?:Lip-)?\s{0,}?\s{0,}Sync\s{0,}\]{1,}",  # Lip Sync
    r"(?i)\[{1,}(?:Short)?\s{0,}?\s{0,}Film\s{0,}\]{1,}",  # Short Film 
    r"(?i)\[{1,}\s{0,}(?:Late)?\s{0,}?\s{0,}(?:Night)?\s{0,}?\s{0,}Session\s{0,}\]{1,}", # Late Night Session
    r"(?i)\[{1,}\s{0,}(?:360°)?\s{0,}\s{0,}(?:360)?\s{0,}\s{0,}(?:Official)?\s{0,}\s{0,}Visualiser\s{0,}\]{1,}", # (Visualiser)
    r"(?i)\[{1,}\s{0,}(?:Royalty)?\s{0,}\s{0,}(?:Free)?\s{0,}\s{0,}Music\s{0,}\]{1,}", # (Royalty Free Music)
    r"(?i)\[{1,}\s{0,}(?:Fan)?\s{0,}\s{0,}(?:Made)?\s{0,}\s{0,}(?:Memories)?\s{0,}\s{0,}Video\s{0,}\]{1,}", # (Fan Memories Video)
    r"(?i)\[{1,}\s{0,}(?:Fan[-]{0,}Made)?\s{0,}\s{0,}Video\s{0,}\]{1,}", #Fan-Made Video
    r"(?i)\[{1,}\s{0,}\s{0,}(?:Lyrics)?\s{0,}\s{0,}(?:Lyrics\s{1,}[+]{1,}\s{0,})?\s{0,}\s{0,}(?:\b\w+){0,1}\s+Translation\s{0,}\]{1,}", # (Lyrics + English Translation)
    r"(?i)\[{1,}(?:Unreleased)?\s{0,}?\s{0,}(?:4K)?\s{0,}?\s{0,}Video\s{0,}\]{1,}",  # Unreleased
    r"(?i)\[{1,}(?:Unreleased)?\s{0,}?\s{0,}(?:Fan)?\s{0,}?\s{0,}(?:Made)?\s{0,}?\s{0,}(?:Fan-Made)?\s{0,}?\s{0,}Video\s{0,}\]{1,}", # Unreleased
    r"(?i)\[{1,}\d{4}\s{0,}?\s{0,}\s{0,}(?:Mashup)?\s{0,}\]{1,}",  # (2018 Mashup)
    r"(?i)\[{1,}\s{0,}(?:ID)?\s{0,}\s{0,}HQ\s{0,}\s{0,}\]{1,}",  # (HQ)
    r"(?i)\[{1,}\s{0,}(?:ID)?\s{0,}\s{0,}HQ\s{0,}\s{0,}\]{1,}", # (ID HQ) - start of string
    r"(?i)\[{1,}(?:Video)?\s{0,}?\s{0,}(?:Original)?\s{0,}?\s{0,}Version\s{0,}\]{1,}", # (Video Original Version)
    r"(?i)\[{1,}\s{0,}HQ\s{0,}\]{1,}", # (HQ)
    r"(?i)\[{1,}(?:Video)?\s{0,}?\s{0,}(?:Original)?\s{0,}?\s{0,}Ufficiale\s{0,}\]{1,}", # Video Ufficiale
    r"(?i)\[{1,}(?:[^A-Za-z0-9]+Official)?\s{0,}?\s{0,}Video\s{0,}\]{1,}", # ~Official Video
    r"(?i)\[{1,}\s{0,}HD\s{0,}\]{1,}", # (HD)
    r"(?i)\[{1,}\s{0,}(?:On Screen)?\s{0,}?\s{0,}(?:Screen On)?\s{0,}?\s{0,}Lyrics\s{0,}?\s{0,}(?:On Screen)?\s{0,}?\s{0,}\]{1,}",  # (ON SCREEN LYRICS)
    r"(?i)\[{1,}\s{0,}\s{0,}(?:\b\w+){0,1}\s+Ver[.]{1}\s{0,}\]{1,}",  # (DE Ver.)
    r"(?i)\[{1,}\s{0,}(?:Official)?\s{0,}?\s{0,}Video\s{0,}(?:HD)?\s{0,}?\]{1,}", # (Official Video HD)
    r"(?i)\[{1,}\s{0,}(?:No)?\s{0,}?\s{0,}Copyright\s{0,}(?:Music)?\s{0,}?\]{1,}", # (No Copyright Music)
    r"(?i)\[{1,}\s{0,}(?:Our)?\s{0,}?\s{0,}Lyric\s{0,}(?:Video)?\s{0,}?\]{1,}", # (Our Lyric Video)
    r"(?i)\[{1,}\s{0,}(?:Album[^A-Za-z0-9]+[s]{0,1})?\s{0,}?\s{0,}Version\s{0,}?\]{1,}", # (Album Version)
    r"(?i)\[{1,}\s{0,}(?:O[f]{0,2}icial)?\s{0,}?\s{0,}Video\s{0,}(?:HD)?\s{0,}?\]{1,}", # Official 
    r"(?i)\[{1,}\s{0,}Video\s{0,}(?:O[f]{1,2}icial)?\s{0,}?\]{1,}",  # (Video Oficial)
    r"(?i)\[{1,}\s{0,}(?:O[f]{0,2}icial)?\s{0,}?(?:HD)?\s{0,}?\s{0,}Clip\s{0,}(?:HD)?\s{0,}?\]{1,}", # Official Clip
    r"(?i)\[{1,}\s{0,}(?:Video)?\s{0,}?(?:HD)?\s{0,}?\s{0,}Officiel\s{0,}(?:Video)?\s{0,}?(?:HD)?\s{0,}?(?:Clip)?\s{0,}?(?:Video)?\s{0,}?\]{1,}",    # (Clip Officiel)
    r"(?i)\[{1,}\s{0,}(?:Unreleased)?\s{0,}?\s{0,}(?:Tribute)?\s{0,}?\s{0,}(?:Music)?\s{0,}?\s{0,}Video\s{0,}\]{1,}", # (Unreleased Tribute Music Video)
    r"(?i)\[{1,}\s{0,}(?:Unreleased)?\s{0,}?\s{0,}(?:Exclusive)?\s{0,}?\s{0,}(?:4K)?\s{0,}?\s{0,}Audio\s{0,}\]{1,}", # (Unreleased Tribute Music Audio)
    r"(?i)\[{1,}\s{0,}(?:Exclusive)?\s{0,}?\s{0,}(?:Music)?\s{0,}?\s{0,}(?:HQ)?\s{0,}?\s{0,}Audio\s{0,}\]{1,}", # (Exclusive Music Audio)     # (Unreleased Audio)
    r"(?i)\[{1,}\s{0,}(?:(?:\b\w+){0,2})\s{0,}(?:Exclusive)?\s{0,}?\s{0,}(?:- Official)?\s{0,}?\s{0,}(?:Music)?\s{0,}?\s{0,}Video\s{0,}\]{1,}",  # ( 2 Words - Official Music Video)
    r"(?i)\[{1,}\s{0,}Remix\s{0,}\]{1,}",  # (Remix)
    r"(?i)\[{1,}\s{0,}Dirty\s{0,}\]{1,}",  # (Dirty)
    r"(?i)\[{1,}\s{0,}Unreleased\s{0,}\]{1,}", # (Unreleased)
    r"(?i)\[{1,}\s{0,}New\s{0,}\]{1,}",   # (New)
    r"(?i)\[{1,}\s{0,}Remake\s{0,}\]{1,}",  # (Remake)
    r"(?i)\[{1,}\s{0,}\s{0,}\s{0,}Shot\s{1,}by\s{1,}.*\]{1,}", # Shot By.....
    r"\[{1,}\s{0,}\]", # Removing Empty Parenthesis
    r"(?i)\[{1,}\s{0,}(?:O[f]{0,2}icial)?\s{0,}?(?:HD)?\s{0,}?(?:Video)?\s{0,}?\s{0,}Release\s{0,}\]{1,}",  # (Official Video Release)
    r"(?i)\[{1,}\s{0,}(?:Exclusive -)?\s{0,}?(?:O[f]{0,2}icial)?\s{0,}?\s{0,}(?:Exclusive)?\s{0,}?\s{0,}(?:Music)?\s{0,}?\s{0,}Video\s{0,}\]{1,}",  # (Exclusive - Official Music Video)
    r"(?i)\[{1,}\s{0,}\s{0,}\s{0,}Edit[e]{0,1}[d]{0,1}\s{1,}by[.]{0,1}\s{1,}.*\]{1,}",  # Edit(ed) By.
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){1,5}\s{0,}Production[s]{0,1}\s{0,}\]{1,}$", # 1-5 words + Production(s)
    r"(?i)\[{1,}(?:Mash)?\s{0,}?\s{0,}(?:\d{1}[k]{1}\d{2}\s{0,}?\s{0,})?\s{0,}Mashup\s{0,}\s{0,}(?:\d{1}[k]{1}\d{2})?\s{0,}?\]{1,}",  # (2k15 MashUp) or (2k19 Mashup)
    r"(?i)\[{1,}\s{0,}(?:Visual)?\s{0,}\s{0,}(?:Meme)?\s{0,}\s{0,}(?:Intro)?\s{0,}\s{0,}Audio\s{0,}\]{1,}",   # (Visual Audio)
    r"(?i)\[{1,}\s{0,}(?:Exclusive)?\s{0,}\s{0,}(?:Meme)?\s{0,}\s{0,}(?:Slowed)?\s{0,}\s{0,}Video\s{0,}\]{1,}",
    r"(?i)\[{1,}\s{0,}(?:Slowed [+]{0,1})?\s{0,}\s{0,}Reverb\s{0,}\]{1,}", # (Slowed + Reverb)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){1}\s{0,}Exclusive\s{0,}\]{1,}",  # (WSHH Exclusive)
    r"(?i)\[{1,}\s{0,}\s{0,}Part\s{1,}\d{1,2}\s{0,}\]{1,}",  # (Part 3)
    r"(?i)\[{1,}\s{0,}\s{0,}\s{0,}Shot\s{1,}on\s{1,}.*\]{1,}", # (Shot on iPhone by Cole Bennett)
    r"(?i)\[{1,}(?:Mash)?\s{0,}?\s{0,}(?:\d{1}[k]{1}\d{2}\s{0,}?\s{0,})?\s{0,}Mash\s{0,}\s{0,}(?:\d{1}[k]{1}\d{2})?\s{0,}?\]{1,}", # (MASH 2K21)
    r"(?i)\[{1,}(?:Mash)?\s{0,}?\s{0,}(?:\d{4}\s{0,}?\s{0,})?\s{0,}Mash\s{0,}\s{0,}(?:\d{4})?\s{0,}?\]{1,}", # (MASH 2021)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){1,5}\s{0,}Movie\s{0,}\]{1,}", # (Hood Movie)
    r"(?i)\[{1,}\s{0,}(?:Video)?\s{0,}?(?:HD)?\s{0,}?\s{0,}Aftermovie\s{0,}(?:Video)?\s{0,}?(?:HD)?\s{0,}?(?:Video)?\s{0,}?\]{1,}",  #  Aftermovie
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){0,1}Aftermovie\s{0,}\]{1,}", # (Aftermovie)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){1}Aftermovie\s{0,}\]{1,}", # (Italy Aftermovie)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){1,4}\s{0,}Bootleg\s{0,}\]{1,}",  # (DJ KARSKY BOOTLEG)
    r"(?i)\[{1,}\s{0,}O[f]{0,2}icial\s{1,}(?:\w+\W+){1,5}\s{0,}\]{1,}", # (Official Music Video - WSHH Exclusive)
    r"(?i)\[{1,}\s{0,}O[f]{0,2}icial\s{1,}(?:VideoClip)\s{0,}\]{1,}", # (Official Videoclip)
    r"(?i)\[{1,}(?:Intro)?\s{0,}\d{4}\s{0,}?\s{0,}\s{0,}(?:Intro)?\s{0,}\]{1,}", # (Intro 2017)
    r"(?i)\[{1,}\s{0,}HQ\s{1,}O[f]{0,2}icial\s{0,}\]{1,}", # (HQ Official)
    r"(?i)\[{1,}\s{0,}(?:Official)?\s{0,}?\s{0,}Video\s{0,}(?:Clip)?\s{0,}?\]{1,}", # (Official Video Clip)
    r"(?i)\[{1,}\s{0,}(?:Official)?\s{0,}?(?:Free)?\s{0,}?\s{0,}Download\s{0,}(?:Free)?\s{0,}?\]{1,}", # (FREE DOWNLOAD)
    r"(?i)\[{1,}\s{0,}(?:New)?\s{0,}?(?:Free)?\s{0,}?\s{0,}Music\s{0,}(?:Stream)?\s{0,}?\]{1,}",   # (NEW MUSIC)
    r"(?i)\[{1,}\s{0,}(?:Official)?\s{0,}?(?:HD)?\s{0,}?(?:Full)?\s{0,}?\s{0,}Stream\s{0,}(?:Full)?\s{0,}?\]{1,}",  # (Official Full Stream)
    r"(?i)\[{1,}\s{0,}(?:Official)?\s{0,}?(?:Preview)?\s{0,}?(?:PREMIER)?\s{0,}?(?:PREMIERA)?\s{0,}?\s{0,}\d{4}\s{0,}\]{1,}",     # PREMIERA 2021) or PREMIER or Preview
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){1,1}\s{0,}Bootleg\s{0,}?\s{0,}(?:\d{4})\s{0,}?\s{0,}\]{1,}",     # (ENDRIU BOOTLEG 2021)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){1,5}\s{0,}Recap\s{0,}\]{1,}", # (Summer Tour 2017 Recap)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){1,5}\s{0,}HQ\s{0,}\]{1,}",  # (Extended Snippet HQ)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){1,5}\s{0,}\W+Lyrics\W+\s{0,}\]{1,}", # (Whatever Lyrics)
    r"(?i)\[{1,}\s{0,}Meme\s{1,}(?:\w+\W+){0,3}Song\s{0,}\]{1,}", # (Meme Words Song)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){0,3}Meme\s{1,}(?:\w+\W+){0,3}Remix\s{0,}\]{1,}", # (Coffin Dance Meme Song Remix)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){0,3}Intro\s{1,}(?:\w+\W+){0,3}Song\s{0,}\]{1,}", # (Ali-A Fortnite Intro Song)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){0,3}Style\s{0,}\]{1,}",  # ( Dance Club Style )
    r"(?i)\[{1,}\s{0,}Billboard\s{0,}?(?:\w+\W+){1}\s{0,}?\s{0,}\s{0,}\d{1,4}\s{0,}\]{1,}", # (Billboard Hot 100)
    r"(?i)\[{1,}\s{0,}Rated\s{1}\w+\s{0,1}\]{1,}", # (Rated PG)
    r"(?i)\[{1,}\s{0,}HD\s{1}\w+\s{0,1}\]{1,}",  # (HD Version)
    r"(?i)\[{1,}\s{0,}(?:Music)?\s{0,}?(?:Remastered)?\s{0,}?(?:Music)?\s{0,}?O[f]{0,2}icial\s{1,}\s{0,}(?:Music)?\s{0,}?(?:Video)?\s{0,}?(?:Remastered)?\s{0,}?\]{1,}",     # (Official Music Video Remastered)
    r"(?i)\[{1,}\s{0,}(?:Officially)?\s{0,}?(?:Out)?\s{0,}?Now\s{0,}\]{1,}",  # (OUT NOW)
    r"(?i)\[{1,}\s{0,}(?:Your)?\s{0,}?(?:Choice)?\s{0,}?(?:Top)?\s{0,}?\d{1,4}\s{0,}\]{1,}",     # (Your Choice Top 10)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){0,3}\s{0,}Chart[s]{0,1}\s{0,}\]{1,}", # (UK BBC CHART)
    r"(?i)\[{1,}(?:New)?\s{0,}?\s{0,}(?:HD)?\s{0,}?\s{0,}Version\s{0,}\]{1,}",  # (New Version)
    r"(?i)\[{1,}\s{0,}O[f]{0,2}icial\s{1,}(?:Video)?\s{0,}?\s{0,1}[-]{1,}\s{0,1}\d{4}\s{0,}\]{1,}",   # (Official Video - 1996)
    r"(?i)\[{1,}\s{0,}Set\s{0,1}(?:Rip)?\s{0,}?\]{1,}", # (Set rip)
    r"(?i)\[{1,}\d{4}\s{0,}?(?:Remaster)?\s{0,}\]{1,}", # (2018 Remaster)
    r"(?i)\[{1,}\s{0,}Stereo\s{0,1}?(?:Version)?\s{0,}\]{1,}", #(Stereo Version)
    r"(?i)\[{1,}\s{0,}((\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?)(\d{1,2}(st|nd|rd|th)?)?((\s*[,.\-\/]\s*)\D?)?\s*((19[0-9]\d|20\d{2})|\d{2})*\s{0,}\]{1,}", # (July 2019)
    r"(?i)\[{1,}\s{0,}(?:Best)?\s{0,}?\s{0,}\s{0,}(?:Songs)?\s{0,}?((\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?)(\d{1,2}(st|nd|rd|th)?)?((\s*[,.\-\/]\s*)\D?)?\s*((19[0-9]\d|20\d{2})|\d{2})*\s{0,}\]{1,}", # (BEST SONGS Month 2019)
    r"(?i)\[{1,}\s{0,}(?:Best)?\s{0,}?\s{0,}\s{0,}(?:Songs)?\s{0,}?\d{4}\s{0,}\]{1,}", # Best Songs 2020
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){1}\s{0,}\]{1,}", # (IMPOSSIBLE!!!)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){1}\s{0,}\s{0,1}Remixes\s{0,1}\]{1,}", # (The Remixes)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){1,6}\s{0,}\s{0,1}Lip[-]{0,1}\s{0,1}Sync\s{0,1}\]{1,}", # (The Victoria’s Secret Angels Lip Sync)
    r"^\s{0,}\(([^\)]+)\)",  # (Patti) LaBelle - Lady Marmalade HD 0815007
    r"(?i)\[{1,}\s{0,}(?:Officially)?\s{0,}?(?:Out\W+)?\s{0,}?Now\W+\s{0,}\]{1,}", #  (OUT NOW!) 
    r"(?i)\[{1,}\s{0,}Sub[s]{0,1}[.]{0,1}\s{0,}\w+\W{0,1}\s{0,}\]{1,}", # (Sub. Español)
    r"(?i)\[{1,}\s{0,}\w+\W{0,1}\s{0,}Subtitles{0,1}\s{0,}\w+\W{0,1}\s{0,}\]{1,}",   # (English Subtitles) - (Subtitles Spanish)
    r"(?i)\[{1,}\s{0,}(?:4K)?\s{0,}?\s{0,}(?:Official)?\s{0,}?\s{0,}(?:4K)?\s{0,}?\s{0,}Video[c]{0,1}[l]{0,1}[i]{0,1}[p]{0,1}\s{0,}(?:Clip)?\s{0,}?\]{1,}", #  ( 4K Official Videoclip )
    r"(?i)\[{1,}\s{0,}(?:Audio)?\s{0,}?\s{0,}(?:Official)?\s{0,}?\s{0,}(?:Video)?\s{0,}?\s{0,}Clip\s{0,}?\]{1,}",     # (Audio Clip)
    r"(?i)\[{1,}\s{0,}(?:Animated)?\s{0,}?\s{0,}(?:Cover)?\s{0,}?\s{0,}Art\s{0,}(?:[-]{0,}Cover)?\s{0,}?\s{0,}\s{0,}?\]{1,}", # (Animated Cover Art)
    r"(?i)\[{1,}\s{0,}Taken{0,}\s{1,}From\s{0,}.*\]{1,}", # (Taken from ASOT 2016)
    r"\[{1,}\W+\]{1,}", # (◕,,,◕)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){0,3}\s{0,}Film\s{0,}\]{1,}", # (The Short Film)
    r"(?i)\[{1,}\s{0,}(?:\w+\W+){0,3}\s{0,}Remode\s{0,}\]{1,}", # (KAAZE Remode)
    r"(?i)\[{1,}\s{0,}(?:OUT)?\s{0,}?\s{0,}\s{0,}(?:NOW)?\s{0,}?((\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?)(\d{1,2}(st|nd|rd|th)?)?((\s*[,.\-\/]\s*)\D?)?\s*((19[0-9]\d|20\d{2})|\d{2})*\s{0,}\]{1,}", # (OUT AUGUST 28)
    r"(?i)\[{1,}\s{0,}(?:OUT)?\s{0,}?\s{0,}\s{0,}(?:ON)?\s{0,}?((\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?)(\d{1,2}(st|nd|rd|th)?)?((\s*[,.\-\/]\s*)\D?)?\s*((19[0-9]\d|20\d{2})|\d{2})*\s{0,}\]{1,}",   # (OUT ON AUGUST 28) 
    r"(?i)\[{1,}\s{0,}((\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?)(\d{1,2}(st|nd|rd|th)?)?((\s*[,.\-\/]\s*)\D?)?\s*((19[0-9]\d|20\d{2})|\d{2})*(?:OUT)?\s{0,}?\s{0,}\s{0,}(?:NOW)?\s{0,}?\s{0,}\]{1,}",     # (AUGUST 28 OUT NOW) 
    r"(?i)\[{1,}\s{0,1}Out\s{1}on\s{1,}\s{0,}(\s{0,1}\b\w+){1,3}\s{0,}\]",  # (Out on Ophelia Records)
    r"(?i)\[{1,}\s{0,}O[f]{0,2}icial\s{1,}\s{0,}(?:Movie)?\s{0,}(?:Trailer)?\s{0,}?\s{0,}(?:Teaser)?\s{0,}?\s{0,}?\]{1,}",    # (Official Teaser)    # (Official Movie Trailer)
    r"(?i)\[{1,}\s{0,}\s{0,}(?:O[f]{1,2}icial)?\s{0,}?Movie\s{0,}\s{0,}(?:Teaser)?\s{0,}?\s{0,}(?:Trailer)?\s{0,}?\]{1,}", # (Official Movie Trailer) # (Movie Teaser )
    r"(?i)\[{1,}\s{0,}\s{0,}(?:Free)?\s{0,}?Release\s{0,}\s{0,}\]{1,}",  # ( Free Release )
    r"(?i)\[{1,}\s{0,}\s{0,}(?:Audio)?\s{0,}?Only\s{0,}(?:Audio)?\s{0,}?\s{0,}\]{1,}", # (audio only) 
    r"(?i)\[{1,}\s{0,}\s{0,}Audio\s{0,}(?:Snippet)?\s{0,}?\s{0,}\]{1,}",  # (audio snippet)
    r"(?i)\[{1,}\s{0,}\s{0,}Full\s{0,}(?:EP)?\s{0,}?\s{0,}(?:Track)?\s{0,}?\s{0,}\]{1,}",    # (Full EP)     # (FULL TRACK)
    r"(?i)\[{1,}\s{0,}\s{0,}Full\s{1,}Track\s{0,}[-]{0,1}\s{0,}?\s{0,}\s{0,}(?:\W+OUT NOW\W+)\s{0,}\]{1,}", # (FULL TRACK - *OUT NOW*)
    r"(?i)\[{1,}\s{0,}\s{0,}\s{0,}(?:4K)?\s(?:Official)?\s{0,}Videoclip\s{0,}\]{1,}",  # ( 4K Official Videoclip )
    r"(?i)\[{1,}\s{0,}\s{0,}\s{0,}(?:Music)?\s(?:Video)?\s{0,}HD\s{0,}\]{1,}", # (Music Video HD)
    r"(?i)\[{1,}\s{0,}\s{0,}(?:\w+\W+){1,2}Boot\s{0,}\]{1,}", # (Smookie Illson Boot)
    r"(?i)\[{1,}\s{0,}\s{0,}(?:\w+\W+){1,2}\s{0,}Boot\s{0,}\]{1,}",  # (Smookie Illson Boot)
    r"(?i)\[{1,}\s{0,}Committed\s{1,}To\s{1,}.*\s{0,}\]{1,}", # (Committed To Sparkle Motion) 
    r"(?i)\[{1,}\s{0,}Full\s{1,}Album\s{0,}\]{1,}", # (full album)
    r"(?i)\[{1,}\s{0,}O[f]{0,2}icial\s{1,}\s{0,}(?:Movie)?\s{0,}(?:Trailer)?\s{0,}?\s{0,}(?:Preview)?\s{0,}?\s{0,}?\]{1,}",   # (Official Preview )
    r"(?i)\[{1,}\s{0,}O[f]{0,2}icial\s{1,}\s{0,}(?:Movie)?\s{0,}(?:Trailer)?\s{0,}?\s{0,}(?:HD)?\s{0,}?\s{0,}\s{0,}(?:HQ)?\s{0,}?\s{0,}(?:Preview)?\s{0,}?\s{0,}?\]{1,}",     # (Official HQ Preview)
    r"(?i)\[{1,}\s{0,}Original(?:Movie)?\s{0,}(?:Trailer)?\s{0,}?\s{1,}(?:Song)\s{0,}?\s{0,}\s{0,}(?:HQ)?\s{0,}?\s{0,}(?:Preview)?\s{0,}?\s{0,}?\]{1,}",     # (Original Song)
    r"(?i)\[{1,}\s{0,}O[f]{0,2}icial\s{1,}\s{0,}(?:Movie)?\s{0,}(?:Lyric)?\s{0,}?\s{0,}(?:HD)?\s{0,}?\s{0,}\s{0,}(?:Video)?\s{0,}?\s{0,}(?:HD)?\s{0,}?\s{0,}?\]{1,}",     # (Official Lyric Video HD)
    r"(?i)\[{1,}\s{0,}Making\s{1,}of\s{0,}\]{1,}", # (Making Of)
    r"(?i)\[{1,}\s{0,}O[f]{0,2}icial\s{1,}\s{0,}(?:Visual)?\s{0,}?\]{1,}",  # (Official Visual) 
    r"(?i)\[{1,}\s{0,}Uncensored\s{1,}\s{0,}(?:HD)?\s{0,}?\s{0,}(?:Official)?\s{0,}?\s{0,}(?:HD)?\s{0,}?\s{0,}(?:\w+\W+){1}\s{0,}(?:Version)?\s{0,}?\]{1,}", # (Uncensored HD Official UK Version)
    r"(?i)\[{1,}\s{0,}Out\s{1,}on\s{0,}(?:\w+\W+){1,3}\s{0,}(?:\d{4}\s{0,}?\s{0,})?\s{0,}\s{0,}?((\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?)(\d{1,2}(st|nd|rd|th)?)?((\s*[,.\-\/]\s*)\D?)?\s*((19[0-9]\d|20\d{2})|\d{2})*\s{0,}\]{1,}", # (Out On OZ Records 19 April ) # (Out On OZ Records on March 19th)
    r"(?i)\[{1,}\s{0,1}Part\s{0,}(\s{0,1}\b\w+){1,3}\s{0,}\]{1,}", # (Part One)
    r"(?i)\[{1,}\s{0,1}(\s{0,1}\b\w+){0,3}\s{0,}Out\s{0,}\W+Now\W+(\s{0,1}\b\w+){0,3}\s{0,}\]{1,}", # (Monsters 8 out now!)
    r"(?i)\[{1,}\s{0,1}Free\s{1,}DL\s{0,}\]{1,}", # (Free DL) 
    r"(?i)\[{1,}\s{0,}O[f]{0,2}icial\s{1,}(\s{0,1}\b\w+){0,3}\s{0,}Compilation{0,}\s{0,}\]{1,}", # (Official Music Video Compilation)
    r"(?i)\[{1,}\s{0,}Clip\s{1,}Of{1,2}icial\s{0,}\]{1,}", # (clip official)
    r"(?i)\[{1,}\s{0,}Director's\s{1,}Cut\s{0,}\]{1,}", # (Director's Cut)
    r"(?i)\[{1,}\s{0,}Tour\s{1,}Trailer\s{0,}\]{1,}", # (Tour Trailer)
    r"(?i)\[{1,}\s{0,}English\s{1,}Version\s{0,}\]{1,}", # (English Version)
    r"(?i)\[{1,}\s{0,}Tour\s{1,}Trailer\s{0,}(\s{0,1}\b\w+){0,3}\s{0,}\]{1,}", # (Tour Trailer)
    r"(?i)\[{1,}\s{0,}Of{1,2}ficial\s{1,}Video\s{0,}(\s{0,1}\b\w+){0,3}\s{0,}\]{1,}", # (Official Video Live at Freshtival)
    r"(?i)\[{1,}\s{0,}Of{1,2}ficial\s{1,}(\s{0,1}\b\w+){0,3}\s{0,}Video\s{0,}(\s{0,1}\b\w+){0,3}\s{0,}\]{1,}", # (Official Short Video Version HD)
    r"(?i)\[{1,}\s{0,}Full\s{1,}Version\s{0,}\]{1,}", # (Full Version)
    r"(?i)\[{1,}\s{0,}Demo\s{1,}Clip\s{0,}\]{1,}", # (demo clip)
    r"(?i)\[{1,}\s{0,}Clip\s{1,}Of{1,2}iciel\s{0,}\]{1,}", # (Clip Officiel)
    r"(?i)\[{1,}\s{0,}#(\s{0,1}\b\w+){1}\s{0,}\]{1,}", # (#360RA)
    r"(?i)\[{1,}\s{0,}Video\s{0,}(\s{0,1}\b\w+){0,3}\s{0,}Version{0,}\s{0,}\]{1,}", # Bomfunk MC's - Freestyler (Video Original Version)
    r"\s{1,}OUT\s{1,}NOW", # (The Asylum OUT NOW)
    r"(?i)\[{1,}\s{0,}OUT\s{1,}\d{2}[.]{1}\d{2,4}\s{0,}\]{1,}",  # (OUT 10.24)
    r"(?i)\bAudio\b", # Word Audio
    r"\s{0,}\/\s{0,}(?=\])", # Okay (Blush Remix / )
    r"(?i)\[{1,}\s{0,}(?:The)?\s{0,}?Best\s{1,}of\s{1,}.*\s{0,}\]{1,}", # Armin van Buuren Feat. Ray Wilson - Yet Another Day (Ucast Remix) [the Best of Armin Only]
    r"(?i)\[{1,}\s{0,}(?:HD)?\s{0,}?(?:HQ)?\s{0,}?Edit\s{0,}\]{1,}", # [hq Edit]
    r"(?i)\[{1,}\s{0,}O[f]{1,2}icial\s{1,}\s{0,}(?:360°)?\s{0,}?\s{0,}(?:VR)?\s{0,}?\s{0,}(?:Music)?\s{0,}?Video\s{0,}\]{1,}",
    r"(?i)\[{1,}\s{0,}Exclusive\s{1,}by.*\]{1,}", # [exclusive by Brian Ferreyra]
    r"(?i)\[{1,}\s{0,}O[f]{1,2}icial\s{1,}(?:Music)?\s{0,}?(?:Video)?\s{0,}?Re-cut\s{0,}\]{1,}", # [Official Music Video Re-cut]
    r"(?i)\[{1,}\s{0,}Busted\s{1,}by\s{1,}(?:\b\w+\s{0,}){1,2}\]{1,}", # [Busted By Herobust Workings ]
    r"(?i)\[{1,}\s{0,}Downtempo\s{0,}(?:Version)?\s{0,}\]{1,}", # Downtempo Version
    r"(?i)\[{1,}\s{0,}Halloween\s{0,}(?:Version)?\s{0,}(?:Edition)?\s{0,}(?:Edit)?\s{0,}\]{1,}", # Halloween Edit
    r"(?i)//\s{1,}(?:\b\w+\s{0,}){1,2}Music\s{0,}$", # // Hybrid Music
    r"(?i)\[{1,}\s{0,}Billboard\s{0,}(?:\b\w+\s{0,}){1,3}\s{0,}\]{1,}", # [Billboard Top Songs 2021]
    r"(?i)\[{1,}\s{0,}(?:\b\w+\s{0,}){1}\s{0,}O[f]{1,2}icial\]{1,}", # Word + Official
    r"(?i)\[{1,}\s{0,}(?:\b\w+\s{0,}){1,2}\s{0,}Music\]{1,}", # Words + Music
    r"(?i)\[{1,}\s{0,}O[f]{1,2}icial\s{1,}\s{0,}(?:Movie)?\s{0,}?\s{0,}(?:MV)?\s{0,}?\s{0,}\]{1,}", # Official MV
    r"(?i)\[{1,}s{0,}(?:\b\w+\s{0,}){1,2}Release\s{0,}\]{1,}", # [monstercat Release] [Monstercat EP Release] [ncs Release]
    r"(?i)\[{1,}\s{0,}Clean\s{1,}\W+Lyrics\s{0,}\]{1,}", # [Clean - Lyrics]
    r"(?i)\[{1,}\s{0,}Copyright\s{1,}Free\s{0,}\]{1,}", # [copyright Free]
    r"(?i)\[{1,}\s{0,}Coachella(\s{0,1}\b\w+){1,2}\s{0,}\]{1,}", # [coachella Weekend 2]
    r"(?i)\[{1,}\s{0,}Unreleased(\s{0,1}\b\w+){0,2}\s{0,}\]{1,}", # [Unreleased]
    r"(?i)\{{1,}\s{0,}(?:HD)?\s{0,}?(?:HQ)?\s{0,}?Edit\s{0,}\}{1,}", # {HD Edit} 
    r"(?i)\[{1,}\s{0,}\s{0,}(?:\b\w+\s{0,}){1,2}\s{0,}Stream\s{0,}\]{1,}", # [official Full Stream]
    r"(?i)\[{1,}\s{0,}Monstercat\s{0,}\]{1,}", # Monstercat
    r"(?i)\[{1,}s{0,}The\s{1,}Best\s{1,}of\s{1,}(?:\b\w+\s{0,}){1,5}\s{0,}\]{1,}", #  [The Best Of Armin Only Anthem]
    r"(?i)\[{1,}s{0,}Theme\s{1,}Song\s{0,}(?:\b\w+\s{0,}){1,5}\s{0,}\]{1,}", #[Theme Song From Kill Switch]
    r"(?i)\[{1,}\s{0,}\W+\s{0,}tune\s{1,}(?:\b\w+\s{0,}){1,5}\s{0,}\]{1,}", # **tune of the Week
    r"(?i)\[{1,}\s{0,}(?:\b\w+\s{0,}){1,3}Anthem\]{1,}", # Anthem
    r"(?i)\[{1,}\s{0,}Synthwave\s{0,}\]{1,}", # Synthwave
    r"(?i)\[{1,}\s{0,}Remastered\s{1,}(?:\b\w+\s{0,}){1,2}\s{0,}\]{1,}", #[Remastered in 4K]
    r"(?i)\[{1,}\s{0,}.*/\s{0,1}O[f]{1,2}icial\s{1,}Video\s{0,}\]{1,}", # Words + Official Version
    r"(?i)\[{1,}\s{0,}O[f]{1,2}icial\s{1,}\s{0,}?(?:Video)?\s{0,}\]{1,}", # Official Video
    r"(?i)\[{1,}\s{0,}English\s{0,}?(?:Version)?\s{0,}\]{1,}", # English Version
    r"(?i)\[{1,}A[c]{1,2}oustic\s{1,}Performance\s{0,}\]{1,}", # Accoustic Performance
    r"(?i)\[{1,}\s{0,}(?:\b\w+\s{0,}){1}\s{0,}Exclusive\s{1,}-\s{1,}O[f]{1,}icial\s{0,}\]{1,}", # Exclusive Official
    r"(?i)\[{1,}\s{0,}Vevo\s{1,}Presents\s{0,}\]{1,}",
    r"(?i)\[{1,}\s{0,}Premiere\s{0,}\]{1,}",
    r"(?i)\[{1,}\s{0,}Exclusive\s{0,}\]{1,}",
    r"(?i)\[{1,}\s{0,}Electro\s{1,}Swing\s{1,}Cover\s{0,}\]{1,}",
    r"(?i)\[{1,}\s{0,}Hip\s{1,}Hop\s{1,}Remix\s{0,}\]{1,}",
    r"(?i)\[{1,}\s{0,}(?:\b\w+\s{0,}){1,3}[-]{1}\s{1,}Ten\s{1,}Year\s{1,}Tribute\s{0,}\]{1,}",
    r"(?i)\[{1,}\s{0,}(?:\b\w+\s{0,}){1,3}\s{0,}Year\s{1,}Tribute\s{0,}\]{1,}",
    r"(?i)\[{1,}\s{0,}by\s{1,}(?:\b\w+\s{0,}){1,4}\s{1,}Studios\s{0,}\]{1,}",
    r"(?i)\[{1,}\s{0,}Vocaloid\s{0,}\]{1,}",
    r"(?i)\[{1,}\s{0,}trap\s{0,}\]{1,}",
    r"(?i)^\s{0,}\[{1,}\s{0,}.*\s{0,}\]{1,}",
    r"(?i)\[{1,}\s{0,}(?:\b\w+\s{0,}){1,5}\s{1,}[-]{1}\s{0,}YTMAs\s{0,}\]{1,}",
    r"(?i)\[{1,}\s{0,}\d{1,2}\/\d{1,}\s{0,}\]{1,}",
]   

def clean_brackets(track):
    for regex in CLEAN_BRACKETS:
        track = re.sub(regex, "", track, flags=re.IGNORECASE)
    
    if (track.find(')') != -1):
        track = re.sub(r"(?i)\[{1,}\s{0,}O[f]{0,2}icial\s{0,}\]{1,}","", track, flags=re.IGNORECASE)
        
    return track

special_seperators = [r"[|]"]
multiple_seperators = [r"\s{1,}-\s{1,}"]

def replace_special_seperators(track):
    matches = [] 
    
    for x in special_seperators:
            pattern = re.compile(x)
            for match in re.finditer(pattern, track):
                matches.append(match.start())
    
    if matches:
        matches = sorted(matches)

    if len(matches) > 1:
        track = track.replace(track[matches[0]],"-", 1)

    return track

def clean_second_dash(track):
    matches = []

    for x in multiple_seperators:
        pattern = re.compile(x)
        for match in re.finditer(pattern,track):
            matches.append(match.start())
       
    if matches:
        if len(matches) > 1:
           temporary_check_string = track[matches[-1]:]
           count_words = len(re.findall(r'\w+', temporary_check_string.strip()))
           if count_words < 3:
            track = track[:matches[-1]]
        
    return track

CLEAN_EXTRAS = [
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
    r"\.(avi|wmv|mpg|mpeg|flv|mp3|flac)$", # Remove the file extensions from title
    r"((with)?\s*lyrics?( video)?\s*)", # Remove Lyrics, video with etc.
    r"\(\s*(HD|HQ|ᴴᴰ)\s*\)$",  # HD (HQ)
    r"((with)?\s*lyrics?( video)?\s*)", # Remove Lyrics, video with etc.
    r"(HD|HQ|ᴴᴰ)\s*$",  # HD (HQ)
    r"(vid[\u00E9e]o)?\s?clip\sofficiel",  # video clip officiel
    r"of+iziel+es\s*",  # offizielles
    r"vid[\u00E9e]o\s?clip",  # video clip
    r"\sclip",  # clip
    r"((PREMIERE|INCOMING)\s*:)?", # Remove "PREMIERE: " or "INCOMING: " - https://regex101.com/r/nG16TF/3
    r"(Official Track Stream*)", #  Official Track Stream
    r"(of+icial\s*)?(music\s*)?video",  # (official)? (music)? video
    r"(of+icial\s*)?(music\s*)?audio",  # (official)? (music)? audio
    r"(ALBUM TRACK\s*)?(album track\s*)",  # (ALBUM TRACK)
    r"(COVER ART\s*)?(Cover Art\s*)",  # (Cover Art)
    r"(?i)\"{0,}(?=^|\b)Audio\b\"{0,}" #  Audio Case Insensitive
]

def clean_extra_from_title(track):
    for regex in CLEAN_EXTRAS:
        track = re.sub(regex, "", track, flags=re.IGNORECASE)
    
    return track

CLEAN_PARENTHESIS = [
    r"(?i)[(]{1,}Official\s{0,}(?:Music)?\s{0,}Video\s{0,}[)]{1,}",
    r"(?i)[(]{1,}Official\s{0,}(?:Music)?\s{0,}Visualizer\s{0,}[)]{1,}",
    r"(?i)[(]{1,}(?:Music)?\s{0,}Visualizer\s{0,}[)]{1,}",
    r"(?i)[(]{1,}(?:Audio)?\s{0,}?\s{0,}(?:With)?\s{0,}?\s{0,}Lyrics\s{0,}?\s{0,}(?:Included)?\s{0,}?\s{0,}[)]{1,}",    # Lyrics   # Audio with Lyrics     # Lyrics included  # With Lyrics
    r"(?i)[(]{1,}(?:Official)?\s{0,}?\s{0,}(?:)?\s{0,}?\s{0,}Lyrics\s{0,}?\s{0,}(?:Video)?\s{0,}?\s{0,}[)]{1,}",  # Official Lyrics Video
    r"(?i)[(]{1,}(?:Official)?\s{0,}?\s{0,}(?:)?\s{0,}?\s{0,}Lyric\s{0,}?\s{0,}(?:Video)?\s{0,}?\s{0,}[)]{1,}",   # Official Lyric Video
    r"(?i)[(]{1,}(?:Official)?\s{0,}?\s{0,}(?:)?\s{0,}?\s{0,}Audio\s{0,}?\s{0,}(?:\d{4})?\s{0,}?\s{0,}[)]{1,}",   # Audio # Official Audio # Official Audio [date]
    r"(?i)[(]{1,}(?:Official)?\s{0,}?\s{0,}(?:)?\s{0,}?\s{0,}Visualizer\s{0,}?\s{0,}[)]{1,}",  # Official Visualizer # Visualizer
    r"(?i)[(]{1,}(?:Version)?\s{0,}?\s{0,}(?:Release)?\s{0,}?\s{0,}\d{4}\s{0,}?\s{0,}(?:Version)?\s{0,}?\s{0,}[)]{1,}",  # Just a Year
    r"(?i)[(]{1,}\s{0,}(?:Cover)?\s{0,}\s{0,}(?:Album)?\s{0,}\s{0,}Art\s{0,}[)]{1,}", # Cover or Cover Art or Cover Album Art
    r"(?i)[(]{1,}\s{0,}(?:Album)?\s{0,}\s{0,}(?:Cover)?\s{0,}\s{0,}Art\s{0,}[)]{1,}", # Album Cover Art
    r"(?i)[(]{1,}\s{0,}(?:Album)?\s{0,}\s{0,}(?:Art)?\s{0,}\s{0,}Cover\s{0,}[)]{1,}", # Album Art Cover
    r"(?i)[(]{1,}\s{0,}(?:Official)?\s{0,}\s{0,}(?:HD)?\s{0,}\s{0,}(?:HQ)?\s{0,}\s{0,}(?:High Definition)?\s{0,}\s{0,}Video\s{0,}[)]{1,}", # Official HD Video # Official Video HD # HD Video  # HQ
    r"(?i)[(]{1,}\s{0,}(?:360°)?\s{0,}\s{0,}(?:360)?\s{0,}\s{0,}(?:Official)?\s{0,}\s{0,}Visualizer\s{0,}[)]{1,}", # Official Visualizer  # (360° Visualizer)
    r"(?i)[(]{1,}\s{0,}(?:Official)?\s{0,}\s{0,}(?:Lyric)?\s{0,}\s{0,}(?:Music)?\s{0,}\s{0,}Video\s{0,}[)]{1,}",  # Lyric Video # Our Lyric Video # Music Video
    r"(?i)[(]{1,}\s{0,}Bass\s{0,}\s{0,}Boosted\s{0,}[)]{1,}", # Bass Boosted
    r"(?i)[(]{1,}\s{0,}Official.*Version\s{0,}[)]{1,}", # Official Whatever Version
    r"(?i)[(]{1,}\s{0,}Official\s{1,}Explicit.*\s{0,}[)]{1,}", # Official Explicit Whatever
    r"(?i)[(]{1,}\s{0,}Video\s{0,}[)]{1,}", # Video  
    r"(?i)[(]{1,}\s{0,}Live\s{1,}(?:from)?\s{0,}\s{0,}(?:at)?\s{0,}\s{0,}.*\s{0,}[)]{1,}",  # Live from or at 
    r"(?i)[(]{1,}(?:Explicit)?\s{0,}?\s{0,}(?:Static)?\s{0,}?\s{0,}Video\s{0,}?\s{0,}(?:Static)?\s{0,}?\s{0,}[)]{1,}",     # Static Video
    r"(?i)[(]{1,}\s{0,}Explicit\s{0,}[)]{1,}", # Explicit
    r"(?i)[(]{1,}\s{0,}ID\s{0,}[)]{1,}", # ID 
    r"(?i)[(]{1,}DJ[-\s]{1,}Set.*\s{0,}[)]{1,}", # Dj-Set
    r"(?i)[(]{1,}\s{0,}\s{0,}\s{0,}(?:High)?\s{0,}\s{0,}(?:Best)?\s{0,}\s{0,}Quality\s{0,}[)]{1,}",  # Best Quality - High Quality
    r"(?i)[(]{1,}\s{0,}\s{0,}\s{0,}From\s{0,}.*[)]{1,}",  # From ...
    r"(?i)[(]{1,}(?:Official)?\s{0,}?\s{0,}(?:4K)?\s{0,}?\s{0,}Video\s{0,}[)]{1,}",  # Official 4K Video
    r"(?i)[(]{1,}Official\s{0,}(?:Song)?\s{0,}?\s{0,}[)]{1,}", # Official Song
    r"(?i)[(]{1,}Oficial\s{0,}[)]{1,}", # Official misworded 
    r"(?i)[(]{1,}\s{0,}Directed\s{1,}by\s{0,}.*[)]{1,}",  # Directed by 
    r"(?i)[(]{1,}\s{0,}Mix[e]{0,}[d]{0,}\s{1,}by\s{0,}.*[)]{1,}",  # Mixed by 
    r"(?i)[(]{1,}\s{0,}(?:360°)?\s{0,}\s{0,}(?:360)?\s{0,}\s{0,}(?:Official)?\s{0,}\s{0,}Video\s{0,}[)]{1,}",   # 360 Video
    r"(?i)[(]{1,}\s{0,}Dir[.]{1,}\s{1,}by\s{0,}.*[)]{1,}", # Dir. by
    r"(?i)[(]{1,}\s{0,}Dir[.]{1,}\s{0,}.*[)]{1,}", # Dir.
    r"(?i)[(]{1,}\s{0,}(?:\b\w+){0,1}\s+Translation\s{0,}[)]{1,}", # any word + Translation
    r"(?i)[(]{1,}\s{0,}4K\s{0,}[)]{1,}", # 4K
    r"(?i)[(]{1,}\s{0,}Presents\s{1,}.*\s{0,}[)]{1,}", # Presents
    r"(?i)[(]{1,}\s{0,}(?:Vevo\s{1,})?\s{0,}\s{0,}Presents\s{1,}.*\s{0,}[)]{1,}",  # Vevo Presents
    r"(?i)[(]{1,}(?:Video)?\s{0,}?\s{0,}Time[-]{0,1}lapse\s{0,}?\s{0,}(?:Video)?\s{0,}?\s{0,}(?:Vid[.]{0,1})?\s{0,}?\s{0,}[)]{1,}",  # Timelapse or Time-lapse + optional Video
    r"(?i)[(]{1,}(?:Animated)?\s{0,}?\s{0,}Video\s{0,}?\s{0,}(?:Animated)?\s{0,}?\s{0,}[)]{1,}", # Animated Video
    r"(?i)[(]{1,}(?:Animated)?\s{0,}?\s{0,}Vid[.]{0,1}\s{0,}?\s{0,}(?:Animated)?\s{0,}?\s{0,}[)]{1,}", # Animated Vid
    r"(?i)[(]{1,}(?:Lip)?\s{0,}?\s{0,}(?:Lip-)?\s{0,}?\s{0,}Sync\s{0,}[)]{1,}",  # Lip Sync
    r"(?i)[(]{1,}(?:Short)?\s{0,}?\s{0,}Film\s{0,}[)]{1,}",  # Short Film 
    r"(?i)[(]{1,}\s{0,}(?:Late)?\s{0,}?\s{0,}(?:Night)?\s{0,}?\s{0,}Session\s{0,}[)]{1,}", # Late Night Session
    r"(?i)[(]{1,}\s{0,}(?:360°)?\s{0,}\s{0,}(?:360)?\s{0,}\s{0,}(?:Official)?\s{0,}\s{0,}Visualiser\s{0,}[)]{1,}", # (Visualiser)
    r"(?i)[(]{1,}\s{0,}(?:Royalty)?\s{0,}\s{0,}(?:Free)?\s{0,}\s{0,}Music\s{0,}[)]{1,}", # (Royalty Free Music)
    r"(?i)[(]{1,}\s{0,}(?:Fan)?\s{0,}\s{0,}(?:Made)?\s{0,}\s{0,}(?:Memories)?\s{0,}\s{0,}Video\s{0,}[)]{1,}", # (Fan Memories Video)
    r"(?i)[(]{1,}\s{0,}(?:Fan[-]{0,}Made)?\s{0,}\s{0,}Video\s{0,}[)]{1,}", #Fan-Made Video
    r"(?i)[(]{1,}\s{0,}\s{0,}(?:Lyrics)?\s{0,}\s{0,}(?:Lyrics\s{1,}[+]{1,}\s{0,})?\s{0,}\s{0,}(?:\b\w+){0,1}\s+Translation\s{0,}[)]{1,}", # (Lyrics + English Translation)
    r"(?i)[(]{1,}(?:Unreleased)?\s{0,}?\s{0,}(?:4K)?\s{0,}?\s{0,}Video\s{0,}[)]{1,}",  # Unreleased
    r"(?i)[(]{1,}(?:Unreleased)?\s{0,}?\s{0,}(?:Fan)?\s{0,}?\s{0,}(?:Made)?\s{0,}?\s{0,}(?:Fan-Made)?\s{0,}?\s{0,}Video\s{0,}[)]{1,}", # Unreleased
    r"(?i)[(]{1,}\d{4}\s{0,}?\s{0,}\s{0,}(?:Mashup)?\s{0,}[)]{1,}",  # (2018 Mashup)
    r"(?i)[(]{1,}\s{0,}(?:ID)?\s{0,}\s{0,}HQ\s{0,}\s{0,}[)]{1,}",  # (HQ)
    r"(?i)[(]{1,}\s{0,}(?:ID)?\s{0,}\s{0,}HQ\s{0,}\s{0,}[)]{1,}", # (ID HQ) - start of string
    r"(?i)[(]{1,}(?:Video)?\s{0,}?\s{0,}(?:Original)?\s{0,}?\s{0,}Version\s{0,}[)]{1,}", # (Video Original Version)
    r"(?i)[(]{1,}\s{0,}HQ\s{0,}[)]{1,}", # (HQ)
    r"(?i)[(]{1,}(?:Video)?\s{0,}?\s{0,}(?:Original)?\s{0,}?\s{0,}Ufficiale\s{0,}[)]{1,}", # Video Ufficiale
    r"(?i)[(]{1,}(?:[^A-Za-z0-9]+Official)?\s{0,}?\s{0,}Video\s{0,}[)]{1,}", # ~Official Video
    r"(?i)[(]{1,}\s{0,}HD\s{0,}[)]{1,}", # (HD)
    r"(?i)[(]{1,}\s{0,}(?:On Screen)?\s{0,}?\s{0,}(?:Screen On)?\s{0,}?\s{0,}Lyrics\s{0,}?\s{0,}(?:On Screen)?\s{0,}?\s{0,}[)]{1,}",  # (ON SCREEN LYRICS)
    r"(?i)[(]{1,}\s{0,}\s{0,}(?:\b\w+){0,1}\s+Ver[.]{1}\s{0,}[)]{1,}",  # (DE Ver.)
    r"(?i)[(]{1,}\s{0,}(?:Official)?\s{0,}?\s{0,}Video\s{0,}(?:HD)?\s{0,}?[)]{1,}", # (Official Video HD)
    r"(?i)[(]{1,}\s{0,}(?:No)?\s{0,}?\s{0,}Copyright\s{0,}(?:Music)?\s{0,}?[)]{1,}", # (No Copyright Music)
    r"(?i)[(]{1,}\s{0,}(?:Our)?\s{0,}?\s{0,}Lyric\s{0,}(?:Video)?\s{0,}?[)]{1,}", # (Our Lyric Video)
    r"(?i)[(]{1,}\s{0,}(?:Album[^A-Za-z0-9]+[s]{0,1})?\s{0,}?\s{0,}Version\s{0,}?[)]{1,}", # (Album Version)
    r"(?i)[(]{1,}\s{0,}(?:O[f]{0,2}icial)?\s{0,}?\s{0,}Video\s{0,}(?:HD)?\s{0,}?[)]{1,}", # Official 
    r"(?i)[(]{1,}\s{0,}Video\s{0,}(?:O[f]{1,2}icial)?\s{0,}?[)]{1,}",  # (Video Oficial)
    r"(?i)[(]{1,}\s{0,}(?:O[f]{0,2}icial)?\s{0,}?(?:HD)?\s{0,}?\s{0,}Clip\s{0,}(?:HD)?\s{0,}?[)]{1,}", # Official Clip
    r"(?i)[(]{1,}\s{0,}(?:Video)?\s{0,}?(?:HD)?\s{0,}?\s{0,}Officiel\s{0,}(?:Video)?\s{0,}?(?:HD)?\s{0,}?(?:Clip)?\s{0,}?(?:Video)?\s{0,}?[)]{1,}",    # (Clip Officiel)
    r"(?i)[(]{1,}\s{0,}(?:Unreleased)?\s{0,}?\s{0,}(?:Tribute)?\s{0,}?\s{0,}(?:Music)?\s{0,}?\s{0,}Video\s{0,}[)]{1,}", # (Unreleased Tribute Music Video)
    r"(?i)[(]{1,}\s{0,}(?:Unreleased)?\s{0,}?\s{0,}(?:Exclusive)?\s{0,}?\s{0,}(?:4K)?\s{0,}?\s{0,}Audio\s{0,}[)]{1,}", # (Unreleased Tribute Music Audio)
    r"(?i)[(]{1,}\s{0,}(?:Exclusive)?\s{0,}?\s{0,}(?:Music)?\s{0,}?\s{0,}(?:HQ)?\s{0,}?\s{0,}Audio\s{0,}[)]{1,}", # (Exclusive Music Audio)     # (Unreleased Audio)
    r"(?i)[(]{1,}\s{0,}(?:(?:\b\w+){0,2})\s{0,}(?:Exclusive)?\s{0,}?\s{0,}(?:- Official)?\s{0,}?\s{0,}(?:Music)?\s{0,}?\s{0,}Video\s{0,}[)]{1,}",  # ( 2 Words - Official Music Video)
    r"(?i)[(]{1,}\s{0,}Remix\s{0,}[)]{1,}",  # (Remix)
    r"(?i)[(]{1,}\s{0,}Dirty\s{0,}[)]{1,}",  # (Dirty)
    r"(?i)[(]{1,}\s{0,}Unreleased\s{0,}[)]{1,}", # (Unreleased)
    r"(?i)[(]{1,}\s{0,}New\s{0,}[)]{1,}",   # (New)
    r"(?i)[(]{1,}\s{0,}Remake\s{0,}[)]{1,}",  # (Remake)
    r"(?i)[(]{1,}\s{0,}\s{0,}\s{0,}Shot\s{1,}by\s{1,}.*[)]{1,}", # Shot By.....
    r"[(]\s{0,}[)]", # Removing Empty Parenthesis
    r"(?i)[(]{1,}\s{0,}(?:O[f]{0,2}icial)?\s{0,}?(?:HD)?\s{0,}?(?:Video)?\s{0,}?\s{0,}Release\s{0,}[)]{1,}",  # (Official Video Release)
    r"(?i)[(]{1,}\s{0,}(?:Exclusive -)?\s{0,}?(?:O[f]{0,2}icial)?\s{0,}?\s{0,}(?:Exclusive)?\s{0,}?\s{0,}(?:Music)?\s{0,}?\s{0,}Video\s{0,}[)]{1,}",  # (Exclusive - Official Music Video)
    r"(?i)[(]{1,}\s{0,}\s{0,}\s{0,}Edit[e]{0,1}[d]{0,1}\s{1,}by[.]{0,1}\s{1,}.*[)]{1,}",  # Edit(ed) By.
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){1,5}\s{0,}Production[s]{0,1}\s{0,}[)]{1,}$", # 1-5 words + Production(s)
    r"(?i)[(]{1,}(?:Mash)?\s{0,}?\s{0,}(?:\d{1}[k]{1}\d{2}\s{0,}?\s{0,})?\s{0,}Mashup\s{0,}\s{0,}(?:\d{1}[k]{1}\d{2})?\s{0,}?[)]{1,}",  # (2k15 MashUp) or (2k19 Mashup)
    r"(?i)[(]{1,}\s{0,}(?:Visual)?\s{0,}\s{0,}(?:Meme)?\s{0,}\s{0,}(?:Intro)?\s{0,}\s{0,}Audio\s{0,}[)]{1,}",   # (Visual Audio)
    r"(?i)[(]{1,}\s{0,}(?:Exclusive)?\s{0,}\s{0,}(?:Meme)?\s{0,}\s{0,}(?:Slowed)?\s{0,}\s{0,}Video\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}(?:Slowed [+]{0,1})?\s{0,}\s{0,}Reverb\s{0,}[)]{1,}", # (Slowed + Reverb)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){1}\s{0,}Exclusive\s{0,}[)]{1,}",  # (WSHH Exclusive)
    r"(?i)[(]{1,}\s{0,}\s{0,}Part\s{1,}\d{1,2}\s{0,}[)]{1,}",  # (Part 3)
    r"(?i)[(]{1,}\s{0,}\s{0,}\s{0,}Shot\s{1,}on\s{1,}.*[)]{1,}", # (Shot on iPhone by Cole Bennett)
    r"(?i)[(]{1,}(?:Mash)?\s{0,}?\s{0,}(?:\d{1}[k]{1}\d{2}\s{0,}?\s{0,})?\s{0,}Mash\s{0,}\s{0,}(?:\d{1}[k]{1}\d{2})?\s{0,}?[)]{1,}", # (MASH 2K21)
    r"(?i)[(]{1,}(?:Mash)?\s{0,}?\s{0,}(?:\d{4}\s{0,}?\s{0,})?\s{0,}Mash\s{0,}\s{0,}(?:\d{4})?\s{0,}?[)]{1,}", # (MASH 2021)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){1,5}\s{0,}Movie\s{0,}[)]{1,}", # (Hood Movie)
    r"(?i)[(]{1,}\s{0,}(?:Video)?\s{0,}?(?:HD)?\s{0,}?\s{0,}Aftermovie\s{0,}(?:Video)?\s{0,}?(?:HD)?\s{0,}?(?:Video)?\s{0,}?[)]{1,}",  #  Aftermovie
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){0,1}Aftermovie\s{0,}[)]{1,}", # (Aftermovie)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){1}Aftermovie\s{0,}[)]{1,}", # (Italy Aftermovie)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){1,4}\s{0,}Bootleg\s{0,}[)]{1,}",  # (DJ KARSKY BOOTLEG)
    r"(?i)[(]{1,}\s{0,}O[f]{0,2}icial\s{1,}(?:\w+\W+){1,5}\s{0,}[)]{1,}", # (Official Music Video - WSHH Exclusive)
    r"(?i)[(]{1,}\s{0,}O[f]{0,2}icial\s{1,}(?:VideoClip)\s{0,}[)]{1,}", # (Official Videoclip)
    r"(?i)[(]{1,}(?:Intro)?\s{0,}\d{4}\s{0,}?\s{0,}\s{0,}(?:Intro)?\s{0,}[)]{1,}", # (Intro 2017)
    r"(?i)[(]{1,}\s{0,}HQ\s{1,}O[f]{0,2}icial\s{0,}[)]{1,}", # (HQ Official)
    r"(?i)[(]{1,}\s{0,}(?:Official)?\s{0,}?\s{0,}Video\s{0,}(?:Clip)?\s{0,}?[)]{1,}", # (Official Video Clip)
    r"(?i)[(]{1,}\s{0,}(?:Official)?\s{0,}?(?:Free)?\s{0,}?\s{0,}Download\s{0,}(?:Free)?\s{0,}?[)]{1,}", # (FREE DOWNLOAD)
    r"(?i)[(]{1,}\s{0,}(?:New)?\s{0,}?(?:Free)?\s{0,}?\s{0,}Music\s{0,}(?:Stream)?\s{0,}?[)]{1,}",   # (NEW MUSIC)
    r"(?i)[(]{1,}\s{0,}(?:Official)?\s{0,}?(?:HD)?\s{0,}?(?:Full)?\s{0,}?\s{0,}Stream\s{0,}(?:Full)?\s{0,}?[)]{1,}",  # (Official Full Stream)
    r"(?i)[(]{1,}\s{0,}(?:Official)?\s{0,}?(?:Preview)?\s{0,}?(?:PREMIER)?\s{0,}?(?:PREMIERA)?\s{0,}?\s{0,}\d{4}\s{0,}[)]{1,}",     # PREMIERA 2021) or PREMIER or Preview
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){1,1}\s{0,}Bootleg\s{0,}?\s{0,}(?:\d{4})\s{0,}?\s{0,}[)]{1,}",     # (ENDRIU BOOTLEG 2021)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){1,5}\s{0,}Recap\s{0,}[)]{1,}", # (Summer Tour 2017 Recap)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){1,5}\s{0,}HQ\s{0,}[)]{1,}",  # (Extended Snippet HQ)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){1,5}\s{0,}\W+Lyrics\W+\s{0,}[)]{1,}", # (Whatever Lyrics)
    r"(?i)[(]{1,}\s{0,}Meme\s{1,}(?:\w+\W+){0,3}Song\s{0,}[)]{1,}", # (Meme Words Song)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){0,3}Meme\s{1,}(?:\w+\W+){0,3}Remix\s{0,}[)]{1,}", # (Coffin Dance Meme Song Remix)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){0,3}Intro\s{1,}(?:\w+\W+){0,3}Song\s{0,}[)]{1,}", # (Ali-A Fortnite Intro Song)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){0,3}Style\s{0,}[)]{1,}",  # ( Dance Club Style )
    r"(?i)[(]{1,}\s{0,}Billboard\s{0,}?(?:\w+\W+){1}\s{0,}?\s{0,}\s{0,}\d{1,4}\s{0,}[)]{1,}", # (Billboard Hot 100)
    r"(?i)[(]{1,}\s{0,}Rated\s{1}\w+\s{0,1}[)]{1,}", # (Rated PG)
    r"(?i)[(]{1,}\s{0,}HD\s{1}\w+\s{0,1}[)]{1,}",  # (HD Version)
    r"(?i)[(]{1,}\s{0,}(?:Music)?\s{0,}?(?:Remastered)?\s{0,}?(?:Music)?\s{0,}?O[f]{0,2}icial\s{1,}\s{0,}(?:Music)?\s{0,}?(?:Video)?\s{0,}?(?:Remastered)?\s{0,}?[)]{1,}",     # (Official Music Video Remastered)
    r"(?i)[(]{1,}\s{0,}(?:Officially)?\s{0,}?(?:Out)?\s{0,}?Now\s{0,}[)]{1,}",  # (OUT NOW)
    r"(?i)[(]{1,}\s{0,}(?:Your)?\s{0,}?(?:Choice)?\s{0,}?(?:Top)?\s{0,}?\d{1,4}\s{0,}[)]{1,}",     # (Your Choice Top 10)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){0,3}\s{0,}Chart[s]{0,1}\s{0,}[)]{1,}", # (UK BBC CHART)
    r"(?i)[(]{1,}(?:New)?\s{0,}?\s{0,}(?:HD)?\s{0,}?\s{0,}Version\s{0,}[)]{1,}",  # (New Version)
    r"(?i)[(]{1,}\s{0,}O[f]{0,2}icial\s{1,}(?:Video)?\s{0,}?\s{0,1}[-]{1,}\s{0,1}\d{4}\s{0,}[)]{1,}",   # (Official Video - 1996)
    r"(?i)[(]{1,}\s{0,}Set\s{0,1}(?:Rip)?\s{0,}?[)]{1,}", # (Set rip)
    r"(?i)[(]{1,}\d{4}\s{0,}?(?:Remaster)?\s{0,}[)]{1,}", # (2018 Remaster)
    r"(?i)[(]{1,}\s{0,}Stereo\s{0,1}?(?:Version)?\s{0,}[)]{1,}", #(Stereo Version)
    r"(?i)[(]{1,}\s{0,}((\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?)(\d{1,2}(st|nd|rd|th)?)?((\s*[,.\-\/]\s*)\D?)?\s*((19[0-9]\d|20\d{2})|\d{2})*\s{0,}[)]{1,}", # (July 2019)
    r"(?i)[(]{1,}\s{0,}(?:Best)?\s{0,}?\s{0,}\s{0,}(?:Songs)?\s{0,}?((\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?)(\d{1,2}(st|nd|rd|th)?)?((\s*[,.\-\/]\s*)\D?)?\s*((19[0-9]\d|20\d{2})|\d{2})*\s{0,}[)]{1,}", # (BEST SONGS Month 2019)
    r"(?i)[(]{1,}\s{0,}(?:Best)?\s{0,}?\s{0,}\s{0,}(?:Songs)?\s{0,}?\d{4}\s{0,}[)]{1,}", # Best Songs 2020
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){1}\s{0,}[)]{1,}", # (IMPOSSIBLE!!!)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){1}\s{0,}\s{0,1}Remixes\s{0,1}[)]{1,}", # (The Remixes)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){1,6}\s{0,}\s{0,1}Lip[-]{0,1}\s{0,1}Sync\s{0,1}[)]{1,}", # (The Victoria’s Secret Angels Lip Sync)
    r"^\s{0,}\(([^\)]+)\)",  # (Patti) LaBelle - Lady Marmalade HD 0815007
    r"(?i)[(]{1,}\s{0,}(?:Officially)?\s{0,}?(?:Out\W+)?\s{0,}?Now\W+\s{0,}[)]{1,}", #  (OUT NOW!) 
    r"(?i)[(]{1,}\s{0,}Sub[s]{0,1}[.]{0,1}\s{0,}\w+\W{0,1}\s{0,}[)]{1,}", # (Sub. Español)
    r"(?i)[(]{1,}\s{0,}\w+\W{0,1}\s{0,}Subtitles{0,1}\s{0,}\w+\W{0,1}\s{0,}[)]{1,}",   # (English Subtitles) - (Subtitles Spanish)
    r"(?i)[(]{1,}\s{0,}(?:4K)?\s{0,}?\s{0,}(?:Official)?\s{0,}?\s{0,}(?:4K)?\s{0,}?\s{0,}Video[c]{0,1}[l]{0,1}[i]{0,1}[p]{0,1}\s{0,}(?:Clip)?\s{0,}?[)]{1,}", #  ( 4K Official Videoclip )
    r"(?i)[(]{1,}\s{0,}(?:Audio)?\s{0,}?\s{0,}(?:Official)?\s{0,}?\s{0,}(?:Video)?\s{0,}?\s{0,}Clip\s{0,}?[)]{1,}",     # (Audio Clip)
    r"(?i)[(]{1,}\s{0,}(?:Animated)?\s{0,}?\s{0,}(?:Cover)?\s{0,}?\s{0,}Art\s{0,}(?:[-]{0,}Cover)?\s{0,}?\s{0,}\s{0,}?[)]{1,}", # (Animated Cover Art)
    r"(?i)[(]{1,}\s{0,}Taken{0,}\s{1,}From\s{0,}.*[)]{1,}", # (Taken from ASOT 2016)
    r"[(]{1,}\W+[)]{1,}", # (◕,,,◕)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){0,3}\s{0,}Film\s{0,}[)]{1,}", # (The Short Film)
    r"(?i)[(]{1,}\s{0,}(?:\w+\W+){0,3}\s{0,}Remode\s{0,}[)]{1,}", # (KAAZE Remode)
    r"(?i)[(]{1,}\s{0,}(?:OUT)?\s{0,}?\s{0,}\s{0,}(?:NOW)?\s{0,}?((\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?)(\d{1,2}(st|nd|rd|th)?)?((\s*[,.\-\/]\s*)\D?)?\s*((19[0-9]\d|20\d{2})|\d{2})*\s{0,}[)]{1,}", # (OUT AUGUST 28)
    r"(?i)[(]{1,}\s{0,}(?:OUT)?\s{0,}?\s{0,}\s{0,}(?:ON)?\s{0,}?((\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?)(\d{1,2}(st|nd|rd|th)?)?((\s*[,.\-\/]\s*)\D?)?\s*((19[0-9]\d|20\d{2})|\d{2})*\s{0,}[)]{1,}",   # (OUT ON AUGUST 28) 
    r"(?i)[(]{1,}\s{0,}((\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?)(\d{1,2}(st|nd|rd|th)?)?((\s*[,.\-\/]\s*)\D?)?\s*((19[0-9]\d|20\d{2})|\d{2})*(?:OUT)?\s{0,}?\s{0,}\s{0,}(?:NOW)?\s{0,}?\s{0,}[)]{1,}",     # (AUGUST 28 OUT NOW) 
    r"(?i)[(]{1,}\s{0,1}Out\s{1}on\s{1,}\s{0,}(\s{0,1}\b\w+){1,3}\s{0,}[)]",  # (Out on Ophelia Records)
    r"(?i)[(]{1,}\s{0,}O[f]{0,2}icial\s{1,}\s{0,}(?:Movie)?\s{0,}(?:Trailer)?\s{0,}?\s{0,}(?:Teaser)?\s{0,}?\s{0,}?[)]{1,}",    # (Official Teaser)    # (Official Movie Trailer)
    r"(?i)[(]{1,}\s{0,}\s{0,}(?:O[f]{1,2}icial)?\s{0,}?Movie\s{0,}\s{0,}(?:Teaser)?\s{0,}?\s{0,}(?:Trailer)?\s{0,}?[)]{1,}", # (Official Movie Trailer) # (Movie Teaser )
    r"(?i)[(]{1,}\s{0,}\s{0,}(?:Free)?\s{0,}?Release\s{0,}\s{0,}[)]{1,}",  # ( Free Release )
    r"(?i)[(]{1,}\s{0,}\s{0,}(?:Audio)?\s{0,}?Only\s{0,}(?:Audio)?\s{0,}?\s{0,}[)]{1,}", # (audio only) 
    r"(?i)[(]{1,}\s{0,}\s{0,}Audio\s{0,}(?:Snippet)?\s{0,}?\s{0,}[)]{1,}",  # (audio snippet)
    r"(?i)[(]{1,}\s{0,}\s{0,}Full\s{0,}(?:EP)?\s{0,}?\s{0,}(?:Track)?\s{0,}?\s{0,}[)]{1,}",    # (Full EP)     # (FULL TRACK)
    r"(?i)[(]{1,}\s{0,}\s{0,}Full\s{1,}Track\s{0,}[-]{0,1}\s{0,}?\s{0,}\s{0,}(?:\W+OUT NOW\W+)\s{0,}[)]{1,}", # (FULL TRACK - *OUT NOW*)
    r"(?i)[(]{1,}\s{0,}\s{0,}\s{0,}(?:4K)?\s(?:Official)?\s{0,}Videoclip\s{0,}[)]{1,}",  # ( 4K Official Videoclip )
    r"(?i)[(]{1,}\s{0,}\s{0,}\s{0,}(?:Music)?\s(?:Video)?\s{0,}HD\s{0,}[)]{1,}", # (Music Video HD)
    r"(?i)[(]{1,}\s{0,}\s{0,}(?:\w+\W+){1,2}Boot\s{0,}[)]{1,}", # (Smookie Illson Boot)
    r"(?i)[(]{1,}\s{0,}\s{0,}(?:\w+\W+){1,2}\s{0,}Boot\s{0,}[)]{1,}",  # (Smookie Illson Boot)
    r"(?i)[(]{1,}\s{0,}Committed\s{1,}To\s{1,}.*\s{0,}[)]{1,}", # (Committed To Sparkle Motion) 
    r"(?i)[(]{1,}\s{0,}Full\s{1,}Album\s{0,}[)]{1,}", # (full album)
    r"(?i)[(]{1,}\s{0,}O[f]{0,2}icial\s{1,}\s{0,}(?:Movie)?\s{0,}(?:Trailer)?\s{0,}?\s{0,}(?:Preview)?\s{0,}?\s{0,}?[)]{1,}",   # (Official Preview )
    r"(?i)[(]{1,}\s{0,}O[f]{0,2}icial\s{1,}\s{0,}(?:Movie)?\s{0,}(?:Trailer)?\s{0,}?\s{0,}(?:HD)?\s{0,}?\s{0,}\s{0,}(?:HQ)?\s{0,}?\s{0,}(?:Preview)?\s{0,}?\s{0,}?[)]{1,}",     # (Official HQ Preview)
    r"(?i)[(]{1,}\s{0,}Original(?:Movie)?\s{0,}(?:Trailer)?\s{0,}?\s{1,}(?:Song)\s{0,}?\s{0,}\s{0,}(?:HQ)?\s{0,}?\s{0,}(?:Preview)?\s{0,}?\s{0,}?[)]{1,}",     # (Original Song)
    r"(?i)[(]{1,}\s{0,}O[f]{0,2}icial\s{1,}\s{0,}(?:Movie)?\s{0,}(?:Lyric)?\s{0,}?\s{0,}(?:HD)?\s{0,}?\s{0,}\s{0,}(?:Video)?\s{0,}?\s{0,}(?:HD)?\s{0,}?\s{0,}?[)]{1,}",     # (Official Lyric Video HD)
    r"(?i)[(]{1,}\s{0,}Making\s{1,}of\s{0,}[)]{1,}", # (Making Of)
    r"(?i)[(]{1,}\s{0,}O[f]{0,2}icial\s{1,}\s{0,}(?:Visual)?\s{0,}?[)]{1,}",  # (Official Visual) 
    r"(?i)[(]{1,}\s{0,}Uncensored\s{1,}\s{0,}(?:HD)?\s{0,}?\s{0,}(?:Official)?\s{0,}?\s{0,}(?:HD)?\s{0,}?\s{0,}(?:\w+\W+){1}\s{0,}(?:Version)?\s{0,}?[)]{1,}", # (Uncensored HD Official UK Version)
    r"(?i)[(]{1,}\s{0,}Out\s{1,}on\s{0,}(?:\w+\W+){1,3}\s{0,}(?:\d{4}\s{0,}?\s{0,})?\s{0,}\s{0,}?((\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?)(\d{1,2}(st|nd|rd|th)?)?((\s*[,.\-\/]\s*)\D?)?\s*((19[0-9]\d|20\d{2})|\d{2})*\s{0,}[)]{1,}", # (Out On OZ Records 19 April ) # (Out On OZ Records on March 19th)
    r"(?i)[(]{1,}\s{0,1}Part\s{0,}(\s{0,1}\b\w+){1,3}\s{0,}[)]{1,}", # (Part One)
    r"(?i)[(]{1,}\s{0,1}(\s{0,1}\b\w+){0,3}\s{0,}Out\s{0,}\W+Now\W+(\s{0,1}\b\w+){0,3}\s{0,}[)]{1,}", # (Monsters 8 out now!)
    r"(?i)[(]{1,}\s{0,1}Free\s{1,}DL\s{0,}[)]{1,}", # (Free DL) 
    r"(?i)[(]{1,}\s{0,}O[f]{0,2}icial\s{1,}(\s{0,1}\b\w+){0,3}\s{0,}Compilation{0,}\s{0,}[)]{1,}", # (Official Music Video Compilation)
    r"(?i)[(]{1,}\s{0,}Clip\s{1,}Of{1,2}icial\s{0,}[)]{1,}", # (clip official)
    r"(?i)[(]{1,}\s{0,}Director's\s{1,}Cut\s{0,}[)]{1,}", # (Director's Cut)
    r"(?i)[(]{1,}\s{0,}Tour\s{1,}Trailer\s{0,}[)]{1,}", # (Tour Trailer)
    r"(?i)[(]{1,}\s{0,}English\s{1,}Version\s{0,}[)]{1,}", # (English Version)
    r"(?i)[(]{1,}\s{0,}Tour\s{1,}Trailer\s{0,}(\s{0,1}\b\w+){0,3}\s{0,}[)]{1,}", # (Tour Trailer)
    r"(?i)[(]{1,}\s{0,}Of{1,2}ficial\s{1,}Video\s{0,}(\s{0,1}\b\w+){0,3}\s{0,}[)]{1,}", # (Official Video Live at Freshtival)
    r"(?i)[(]{1,}\s{0,}Of{1,2}ficial\s{1,}(\s{0,1}\b\w+){0,3}\s{0,}Video\s{0,}(\s{0,1}\b\w+){0,3}\s{0,}[)]{1,}", # (Official Short Video Version HD)
    r"(?i)[(]{1,}\s{0,}Full\s{1,}Version\s{0,}[)]{1,}", # (Full Version)
    r"(?i)[(]{1,}\s{0,}Demo\s{1,}Clip\s{0,}[)]{1,}", # (demo clip)
    r"(?i)[(]{1,}\s{0,}Clip\s{1,}Of{1,2}iciel\s{0,}[)]{1,}", # (Clip Officiel)
    r"(?i)[(]{1,}\s{0,}#(\s{0,1}\b\w+){1}\s{0,}[)]{1,}", # (#360RA)
    r"(?i)[(]{1,}\s{0,}Video\s{0,}(\s{0,1}\b\w+){0,3}\s{0,}Version{0,}\s{0,}[)]{1,}", # Bomfunk MC's - Freestyler (Video Original Version)
    r"\s{1,}OUT\s{1,}NOW", # (The Asylum OUT NOW)
    r"(?i)[(]{1,}\s{0,}OUT\s{1,}\d{2}[.]{1}\d{2,4}\s{0,}[)]{1,}",  # (OUT 10.24)
    r"(?i)\bAudio\b", # Word Audio
    r"\s{0,}\/\s{0,}(?=[)])", # Okay (Blush Remix / )
    r"\s{0,}\-\s{0,}(?=[)])", # Clean up after dash
    r"(?i)[(]{1,}\s{0,}Starring\s{1,}(?:\b\w+\s{0,}){1,2}\s{0,}[)]{1,}", #3lau - On My Mind ft. Yeah Boy (Starring Gronk) 
    r"(?i)[(]{1,}\s{0,}(?:HD)?\s{0,}?(?:HQ)?\s{0,}?Edit\s{0,}[)]{1,}", # (hq Edit)
    r"(?i)[(]{1,}\s{0,}O[f]{1,2}icial\s{1,}\s{0,}(?:360°)?\s{0,}?\s{0,}(?:VR)?\s{0,}?\s{0,}(?:Music)?\s{0,}?Video\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Exclusive\s{1,}by.*[)]{1,}", # Exclusive by...
    r"(?i)[(]{1,}\s{0,}O[f]{1,2}icial\s{1,}(?:Music)?\s{0,}?(?:Video)?\s{0,}?Re-cut\s{0,}[)]{1,}", # Official Music Video Re-cut    
    r"\s{0,}[*]{1,}(\s{0,1}\b\w+){1}[*]{1,}\s{0,}", # **totw**
    r"(?i)[(]{1,}\s{0,}Downtempo\s{0,}(?:Version)?\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Halloween\s{0,}(?:Version)?\s{0,}(?:Edition)?\s{0,}(?:Edit)?\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Billboard\s{0,}(?:\b\w+\s{0,}){1,3}\s{0,}[)]{1,}", # (Billboard Top Songs 2021)
    r"(?i)[(]{1,}\s{0,}(?:\b\w+\s{0,}){1,2}\s{0,}Music[)]{1,}", # (Ultra Music)
    r"(?i)[(]{1,}\s{0,}(?:\b\w+\s{0,}){1}\s{0,}O[f]{1,2}icial[)]{1,}", #(Videoclip Oficial)
    r"(?i)[(]{1,}\s{0,}O[f]{1,2}icial\s{1,}\s{0,}(?:Movie)?\s{0,}?\s{0,}(?:MV)?\s{0,}?\s{0,}[)]{1,}", # (Official Mv)
    r"(?i)[(]{1,}\s{0,}(?:\b\w+\s{0,}){1,2}Release\s{0,}[)]{1,}", # (monstercat  Release)
    r"(?i)[(]{1,}\s{0,}Clean\s{1,}\W+Lyrics\s{0,}[)]{1,}", # (Clean - Lyrics)
    r"(?i)[(]{1,}\s{0,}Copyright\s{1,}Free\s{0,}[)]{1,}",  # (copyright Free)
    r"(?i)[(]{1,}\s{0,}Coachella(\s{0,1}\b\w+){1,2}\s{0,}[)]{1,}", # [coachella Weekend 2]
    r"(?i)[(]{1,}\s{0,}Unreleased\s{0,}[)]{1,}", # Unreleased
    r"(?i)[(]{1,}\s{0,}\s{0,}(?:\b\w+\s{0,}){1,2}\s{0,}Stream\s{0,}[)]{1,}", # 2 Words + Stream
    r"(?i)[(]{1,}\s{0,}Monstercat\s{0,}[)]{1,}", # Monstercat
    r"(?i)[(]{1,}\s{0,}The\s{1,}Best\s{1,}of\s{1,}(?:\b\w+\s{0,}){1,5}\s{0,}[)]{1,}", # (The Best Of Armin Only Anthem)
    r"(?i)[(]{1,}s{0,}Theme\s{1,}Song\s{0,}(?:\b\w+\s{0,}){1,5}\s{0,}[)]{1,}",  # Theme Song ...
    r"(?i)[(]{1,}\s{0,}\W+\s{0,}tune\s{1,}(?:\b\w+\s{0,}){1,5}\s{0,}[)]{1,}", # (**tune of the Week)
    r"(?i)[(]{1,}\s{0,}(?:\b\w+\s{0,}){1,3}Anthem[)]{1,}", #  (DLDK Amsterdam 2016 Anthem)
    r"(?i)[(]{1,}\s{0,}Synthwave\s{0,}[)]{1,}", # Synthwave
    r"(?i)[(]{1,}\s{0,}Remastered\s{1,}(?:\b\w+\s{0,}){1,2}\s{0,}[)]{1,}", # Remastered...
    r"(?i)[(]{1,}\s{0,}.*/\s{0,1}O[f]{1,2}icial\s{1,}Video\s{0,}[)]{1,}", # /official video
    r"(?i)[(]{1,}\s{0,}(?:\b\w+\s{0,}){1,3}\s{0,1}O[f]{1,2}icial\s{1,}Song\s{0,}[)]{1,}", # Official Song
    r"(?i)[(]{1,}\s{0,}O[f]{1,2}icial\s{1,}\s{0,}?(?:Video)?\s{0,}[)]{1,}", # Official Video
    r"(?i)[(]{1,}\s{0,}English\s{0,}?(?:Version)?\s{0,}[)]{1,}",
    r"(?i)[(]{1,}Video\s{1,}O[f]{1,2}icial\s{0,}\[{1,}\s{0,}English\s{0,}?(?:Version)?\s{0,}\]{1,}\s{0,}[)]{1,}",  # Official English Version
    r"(?i)[(]{1,}\s{0,}A[c]{1,2}oustic\s{1,}Performance\s{0,}[)]{1,}",  # Accoutstic Performance
    r"(?i)[(]{1,}\s{0,}(?:\b\w+\s{0,}){1}\s{0,}Exclusive\s{1,}-\s{1,}O[f]{1,}icial\s{0,}[)]{1,}",  # Exclusive
    r"(?i)[(]{1,}\s{0,}Vevo\s{1,}Presents\s{0,}[)]{1,}",  # Vevo Presents
    r"(?i)[(]{1,}\s{0,}Live\W+\s{1,}1 Mic\s{1,}1 Take\s{0,}[)]{1,}",  # Live, 1 Mic 1 Take
    r"(?i)[(]{1,}\s{0,}Exclusive\s{0,}[)]{1,}",  # Exclusive
    r"(?i)[(]{1,}\s{0,}Premiere\s{0,}[)]{1,}"  # Premiere
    r"(?i)[(]{1,}\s{0,}Electro\s{1,}Swing\s{1,}Cover\s{0,}[)]{1,}", # Electro Swing Cover
    r"(?i)[(]{1,}\s{0,}Hip\s{1,}Hop\s{1,}Remix\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}(?:\b\w+\s{0,}){1,3}\s{0,}Year\s{1,}Tribute\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}by\s{1,}(?:\b\w+\s{0,}){1,4}\s{1,}Studios\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Vocaloid\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Stripped\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Beyond\s{1,}the\s{1,}lights\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Edm\s{1,}Remix\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Slowed\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Spotify\s{1,}Edit\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}New\s{1,}Song\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Trap\s{1,}Remix\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Mass\s{1,}(?:\b\w+\s{0,}){1,3}Anthem\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Lofi\s{1,}(?:\b\w+\s{0,}){1,3}Beats\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}(?:\b\w+\s{0,}){1,3}\s{0,}Records\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}NCS\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Parental\s{1,}Advisory\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}(?:\b\w+\s{0,}){1,2}Compilation\s{1,}Video\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Starring.*\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}.*sub[+]Lyrics\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}(?:\b\w+\s{0,}){1}Cut\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Free\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Deep\s{1,}House\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Inspired\s{1,}by\s{0,}(?:\b\w+\s{0,}){1,3}\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}trap\s{0,}[)]{1,}",
    r"(?i)\s{0,}[(]{1,}Acoustic\s{1,}Version\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Guest\s{1,}Mix[)]{1,}",
    r"(?i)\s{0,}[(]{1,}Lyrics\s{1,}[-\/\]]{1,}\s{1,}Lyric\s{1,}Video\s{0,}[)]{1,}",
    r"(?i)\s{0,}[(]{1,}Meme\s{1,}Song\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}(?:\b\w+\s{0,}){1,5}[:]{0,1}\s{0,}The\s{1,}Album\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}(?:\b\w+\s{0,}){1,5}\s{1,}[-]{1}\s{0,}YTMAs\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Online\s{1,}Version\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}\d{1,2}\/\d{1,}\s{0,}[)]{1,}",
    r"(?i)[(]{1,}\s{0,}Remix\s{0,}[-]{1}\s{0,}O[f]{1,}icial\s{1,}Visualizer\s{0,}[)]{1,}"

    # MOONBOY - ALIEN INVAZION (RIDDIM/DUBSTEP)

    # Shotgun Feat. (MagMag) - DJ BL3ND, Rettchit [Firepower Records - Dubstep]
   
    # GRAViiTY - ELEVATiON (#Chillstep)
    # Razihel Feat. TeamMate - Legend (ZATOX RMX) - Turn RMX to Remix - Some chords (Jauz ReRemix)
] 

def clean_unrequired_from_parenthesis(track):
    for regex in CLEAN_PARENTHESIS:
        track = re.sub(regex, "", track, flags=re.IGNORECASE)
        
    # Remove Multiple Spaces
    track = ' '.join(track.split())
    
    return track

BRACKET_LIST = [
    r"(?i)\s{0,}[{]{1,}Official\s{1,}Full\s{1,}Stream\s{0,}[}]{1,}"
]

def clean_unrequired_from_bracket(track):
    for regex in BRACKET_LIST:
        track = re.sub(regex, "", track, flags=re.IGNORECASE)
        
    # Remove Multiple Spaces
    track = ' '.join(track.split())
    
    # hashtags and tags

    # Tik-Tok or TikTok
    # Chinese Characters    

    return track

STRIP_SPECIFIC_WORDS = [
    r"(?i)\btik[-]{0,1}tok\b",
    r"(?i)\btik[-]{0,1}\s{1,}tok\b",
    r"(?i)\bO[f]{1,2}icial\b\s{1,}\bMusic\b\s{1,}\bVideo\b\s{0,}",
    r"(?i)\s{1,}O[f]{1,2}icial\s{1,}Movie\s{0,}",
    r"(?i)\s{1,}O[f]{1,2}icial\s{1,}MV\s{0,}",
    r"(?i)\s{1,}O[f]{1,2}icial\s{1,}Video\s{0,}",
    r"(?i)\s{1,}with\s{1,}lyrics\W+(\s{1,}|$)",
    r"(?i)\s{1,}Lyrics(\s{1,}|$)",
    r"(?i)\s{1,}AfterMovie(\s{1,}|$)",
    r"(?i)\s{1,}Official\s{1,}Music\s{1,}Video(\s{1,}|$)",
    r"(?i)\s{1,}Video\s{1,}Ufficiale(\s{1,}|$)",
    r"(?i)\s{1,}Official\s{1,}Video(\s{1,}|$)",
    r"(?i)\s{1,}Spinnin[']{0,1}\s{1,}Records\s{1,}Anniversary(\s{1,}|$)",
    r"(?i)\s{1,}Lyrics[.]{1,}(\s{1,}|$)",
    r"(?i)\s{1,}Live\s{1,}at\s{1,}(?:\b\w+\s{0,}){1}\s{1,}\d{4}(\s{1,}|$)",
    r"(?i)(^|\s{1,})Free\s{1,}Download($|\s)",
    r"(?i)(^|\s{1,})Lyrics\W+($|\s)",
    r"(?i)(^|\s{1,})Lyrics($|\s)",
    r"(?i)(^|\s{1,})MV($|\s)",
    r"(?i)(^|\s{1,})M/V($|\s)",
    r"(?i)(^|\s{1,})O[f]{1,}icial\s{1,}Soundtrack($|\s)",
    r"(?i)(^|\s{1,})\W+Spanish\s{1,}Version($|\s)",
    r"(?i)(^|\s{1,})O[f]{1,2}icial\s{1,}Soundtrack($|\s)",
    r"(?i)(^|\s{1,})Lyric\s{1,}Video($|\s)",
    r"(?i)(^|\s{1,})on\s{1,}Spotify($|\s{1,})",
    r"(?i)(^|\s{1,})on\s{1,}Spotify\s{1,}&\s{1,}Apple($|\s{1,})",
    r"(?i)(^|\s{1,})HD($|\s{1,})",
    r"(?i)(?=\s{1,}|^)by\s{1,}(?:\b\w+\s{0,}){1,4}\s{1,}Studios(?=\s{1,}|$)"

]

artist_track_seperators = [
    r"(?<=[a-zA-Z])-(?=[a-zA-Z]{2,})",
]

track_seperators = [
    r"(?<=[a-zA-Z])-(?=[\s]{1,})",
    r"(?<=[\s])-(?=[a-zA-Z]{2,})"
]

replace_the_seperators = [
    r"(?<=[\s])[|]{1}(?=[\s])",
    r"(?<=[\s])[/]{1}(?=[\s])"
]

word_seperators = [
    r"(?<=[a-zA-Z])\\(?=[a-zA-Z]{2,})",
    r"(?<=[a-zA-Z])[|]{1}(?=[a-zA-Z]{2,})",
    r"(?<=[a-zA-Z])//(?=[a-zA-Z]{2,})",
    r"(?<=[a-zA-Z])/(?=[a-zA-Z]{2,})",  
]

def spaces_for_seperator(string):
    dashes = string.count("-")
    matches = get_all_integers_between_square_brackets(string,artist_track_seperators)

    if dashes == 1 and matches:
         string = string[0:int(matches[-1])] + " - " + string[int(matches[-1])+1:]

    # Remove Multiple Spaces
    string = ' '.join(string.split())

    return string

def replace_seperators(string,list_check):
    matches = get_all_integers_between_square_brackets(string,list_check)
    quotes = string.count("-")
    if quotes == 0 and matches:
       string = string[0:int(matches[-1])] + " - " + string[int(matches[-1])+1:]
    
    pattern = re.compile(r"(?i)(^|\s{1,})--($|\s{1,})")
    string = re.sub(pattern," - ", string)

    # Remove Multiple Spaces
    string = ' '.join(string.split())

    return string

def get_all_integers_between_square_brackets(string,list_to_check):
    matches = []
    for x in list_to_check:
        pattern = re.compile(x)
        for match in re.finditer(pattern, string):
            matches.append(int(match.start()))
    
    return matches

def seperate_backslash_words(track):  
    matches = get_all_integers_between_square_brackets(track,word_seperators)

    if len(matches) > 0:
        for index in matches:
            track = track.replace(track[index]," ", 1)

    return track

def ade_seperate_track_artist(full_title):
    matches = get_all_integers_between_square_brackets(full_title,artist_track_seperators)
    quotes = full_title.count("-")
    p = re.compile(r'(?<=[\s])-(?=[\s])')
    seperator = bool(re.search(p,full_title))
    matches_v2 = get_all_integers_between_square_brackets(full_title,track_seperators)
   
    if len(matches) > 0 and quotes > 1 and seperator is False:
        full_title = full_title[0:int(matches[-1])] + " - " + full_title[int(matches[-1])+1:]
    
    if matches_v2:
        for item in matches_v2:
            full_title = full_title[0:int(item)] + " - " + full_title[int(item)+1:]
    
    full_title = convert_string(full_title)            
    return full_title

def strip_specific_words(track):
    for regex in STRIP_SPECIFIC_WORDS:
        track = re.sub(regex, "", track, flags=re.IGNORECASE)

    # Remove Multiple Spaces
    track = ' '.join(track.split())

    return track 

MISC_LIST = [
    r"(?i)\.(mp4|mkv|wmv|mp3|m4v|mov|avi|flv|webm|flac|mka|m4a|aac|oggswf|avi|flv|mpg|rm|mov|wav|asf|3gp|mkv|rmvb|mp4)(\s{1,}|$)",

]

def remove_miscellaneous(track):

    if track.find("-") != -1:
        track = re.sub(r"(?i)[|]{1,}\s{0,}(\s{0,1}\b\w+){0,3}\s{0,}$","",track, flags=re.IGNORECASE)
        track = re.sub(r"[|]{1,2}\s{1,}.*$","",track, flags=re.IGNORECASE)

    for regex in MISC_LIST:
        track = re.sub(regex,"",track, flags=re.IGNORECASE)
    return track

Escape_Words = ["the","and","are","is","was","were","by","of","no","so","with","be","to","a","be","ft.","n","v","vs","us","me","my","up"]

def clean_track_for_extraction(my_str):
    my_str = re.sub("(?=[a-zA-Z])Audio(?=[a-zA-Z])", " ",my_str, flags=re.IGNORECASE)
    
    for regex in SECOND_LEVEL:
        my_str = re.sub(regex, "", my_str, flags=re.IGNORECASE)
    
    my_str = re.sub(r"\s\s+" , " ", my_str)
 
    find_paren = set(find(my_str,"("))

    if find_paren is not None:
        if len(find_paren) != 0:
            start = list(set(find(my_str,"(")))[0]
            replacement = re.sub(r"[^\w.\s]",'', my_str[start:], flags=re.IGNORECASE)
            my_str = my_str[:start] + "- " + convert_string(replacement)

    my_str = re.sub(r"\s{2,}", " ", my_str)

    return my_str

def clean_track_for_extraction_vol2(my_str):
    my_str = re.sub("(?=[a-zA-Z])Audio(?=[a-zA-Z])", " ",my_str, flags=re.IGNORECASE)
    
    for regex in SECOND_LEVEL:
        my_str = re.sub(regex, "", my_str, flags=re.IGNORECASE)
    
    my_str = re.sub(r"\s\s+" , " ", my_str)
    my_str = re.sub(r"\s{2,}", " ", my_str)

    return my_str

def find(str, ch):
    for i, ltr in enumerate(str):
        if ltr == ch:
            yield i

def clear_title(title):
    for regex in FIRST_LEVEL:
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

def matching_parentheses(string):
    op= [] 
    dc = { 
        op.pop() if op else -1:i for i,c in enumerate(string) if 
        (c=='(' and op.append(i) and False) or (c==')' and op)
    }
    return False if dc.get(-1) or op else dc

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
    regrex_pattern =  re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'',track)

def remove_emoji(track):
    emoji_rx = r"[#*0-9]\uFE0F?\u20E3|©\uFE0F?|[®\u203C\u2049\u2122\u2139\u2194-\u2199\u21A9\u21AA]\uFE0F?|[\u231A\u231B]|[\u2328\u23CF]\uFE0F?|[\u23E9-\u23EC]|[\u23ED-\u23EF]\uFE0F?|\u23F0|[\u23F1\u23F2]\uFE0F?|\u23F3|[\u23F8-\u23FA\u24C2\u25AA\u25AB\u25B6\u25C0\u25FB\u25FC]\uFE0F?|[\u25FD\u25FE]|[\u2600-\u2604\u260E\u2611]\uFE0F?|[\u2614\u2615]|\u2618\uFE0F?|\u261D[\uFE0F\U0001F3FB-\U0001F3FF]?|[\u2620\u2622\u2623\u2626\u262A\u262E\u262F\u2638-\u263A\u2640\u2642]\uFE0F?|[\u2648-\u2653]|[\u265F\u2660\u2663\u2665\u2666\u2668\u267B\u267E]\uFE0F?|\u267F|\u2692\uFE0F?|\u2693|[\u2694-\u2697\u2699\u269B\u269C\u26A0]\uFE0F?|\u26A1|\u26A7\uFE0F?|[\u26AA\u26AB]|[\u26B0\u26B1]\uFE0F?|[\u26BD\u26BE\u26C4\u26C5]|\u26C8\uFE0F?|\u26CE|[\u26CF\u26D1\u26D3]\uFE0F?|\u26D4|\u26E9\uFE0F?|\u26EA|[\u26F0\u26F1]\uFE0F?|[\u26F2\u26F3]|\u26F4\uFE0F?|\u26F5|[\u26F7\u26F8]\uFE0F?|\u26F9(?:\u200D[\u2640\u2642]\uFE0F?|[\uFE0F\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|[\u26FA\u26FD]|\u2702\uFE0F?|\u2705|[\u2708\u2709]\uFE0F?|[\u270A\u270B][\U0001F3FB-\U0001F3FF]?|[\u270C\u270D][\uFE0F\U0001F3FB-\U0001F3FF]?|\u270F\uFE0F?|[\u2712\u2714\u2716\u271D\u2721]\uFE0F?|\u2728|[\u2733\u2734\u2744\u2747]\uFE0F?|[\u274C\u274E\u2753-\u2755\u2757]|\u2763\uFE0F?|\u2764(?:\u200D[\U0001F525\U0001FA79]|\uFE0F(?:\u200D[\U0001F525\U0001FA79])?)?|[\u2795-\u2797]|\u27A1\uFE0F?|[\u27B0\u27BF]|[\u2934\u2935\u2B05-\u2B07]\uFE0F?|[\u2B1B\u2B1C\u2B50\u2B55]|[\u3030\u303D\u3297\u3299]\uFE0F?|[\U0001F004\U0001F0CF]|[\U0001F170\U0001F171\U0001F17E\U0001F17F]\uFE0F?|[\U0001F18E\U0001F191-\U0001F19A]|\U0001F1E6[\U0001F1E8-\U0001F1EC\U0001F1EE\U0001F1F1\U0001F1F2\U0001F1F4\U0001F1F6-\U0001F1FA\U0001F1FC\U0001F1FD\U0001F1FF]|\U0001F1E7[\U0001F1E6\U0001F1E7\U0001F1E9-\U0001F1EF\U0001F1F1-\U0001F1F4\U0001F1F6-\U0001F1F9\U0001F1FB\U0001F1FC\U0001F1FE\U0001F1FF]|\U0001F1E8[\U0001F1E6\U0001F1E8\U0001F1E9\U0001F1EB-\U0001F1EE\U0001F1F0-\U0001F1F5\U0001F1F7\U0001F1FA-\U0001F1FF]|\U0001F1E9[\U0001F1EA\U0001F1EC\U0001F1EF\U0001F1F0\U0001F1F2\U0001F1F4\U0001F1FF]|\U0001F1EA[\U0001F1E6\U0001F1E8\U0001F1EA\U0001F1EC\U0001F1ED\U0001F1F7-\U0001F1FA]|\U0001F1EB[\U0001F1EE-\U0001F1F0\U0001F1F2\U0001F1F4\U0001F1F7]|\U0001F1EC[\U0001F1E6\U0001F1E7\U0001F1E9-\U0001F1EE\U0001F1F1-\U0001F1F3\U0001F1F5-\U0001F1FA\U0001F1FC\U0001F1FE]|\U0001F1ED[\U0001F1F0\U0001F1F2\U0001F1F3\U0001F1F7\U0001F1F9\U0001F1FA]|\U0001F1EE[\U0001F1E8-\U0001F1EA\U0001F1F1-\U0001F1F4\U0001F1F6-\U0001F1F9]|\U0001F1EF[\U0001F1EA\U0001F1F2\U0001F1F4\U0001F1F5]|\U0001F1F0[\U0001F1EA\U0001F1EC-\U0001F1EE\U0001F1F2\U0001F1F3\U0001F1F5\U0001F1F7\U0001F1FC\U0001F1FE\U0001F1FF]|\U0001F1F1[\U0001F1E6-\U0001F1E8\U0001F1EE\U0001F1F0\U0001F1F7-\U0001F1FB\U0001F1FE]|\U0001F1F2[\U0001F1E6\U0001F1E8-\U0001F1ED\U0001F1F0-\U0001F1FF]|\U0001F1F3[\U0001F1E6\U0001F1E8\U0001F1EA-\U0001F1EC\U0001F1EE\U0001F1F1\U0001F1F4\U0001F1F5\U0001F1F7\U0001F1FA\U0001F1FF]|\U0001F1F4\U0001F1F2|\U0001F1F5[\U0001F1E6\U0001F1EA-\U0001F1ED\U0001F1F0-\U0001F1F3\U0001F1F7-\U0001F1F9\U0001F1FC\U0001F1FE]|\U0001F1F6\U0001F1E6|\U0001F1F7[\U0001F1EA\U0001F1F4\U0001F1F8\U0001F1FA\U0001F1FC]|\U0001F1F8[\U0001F1E6-\U0001F1EA\U0001F1EC-\U0001F1F4\U0001F1F7-\U0001F1F9\U0001F1FB\U0001F1FD-\U0001F1FF]|\U0001F1F9[\U0001F1E6\U0001F1E8\U0001F1E9\U0001F1EB-\U0001F1ED\U0001F1EF-\U0001F1F4\U0001F1F7\U0001F1F9\U0001F1FB\U0001F1FC\U0001F1FF]|\U0001F1FA[\U0001F1E6\U0001F1EC\U0001F1F2\U0001F1F3\U0001F1F8\U0001F1FE\U0001F1FF]|\U0001F1FB[\U0001F1E6\U0001F1E8\U0001F1EA\U0001F1EC\U0001F1EE\U0001F1F3\U0001F1FA]|\U0001F1FC[\U0001F1EB\U0001F1F8]|\U0001F1FD\U0001F1F0|\U0001F1FE[\U0001F1EA\U0001F1F9]|\U0001F1FF[\U0001F1E6\U0001F1F2\U0001F1FC]|\U0001F201|\U0001F202\uFE0F?|[\U0001F21A\U0001F22F\U0001F232-\U0001F236]|\U0001F237\uFE0F?|[\U0001F238-\U0001F23A\U0001F250\U0001F251\U0001F300-\U0001F320]|[\U0001F321\U0001F324-\U0001F32C]\uFE0F?|[\U0001F32D-\U0001F335]|\U0001F336\uFE0F?|[\U0001F337-\U0001F37C]|\U0001F37D\uFE0F?|[\U0001F37E-\U0001F384]|\U0001F385[\U0001F3FB-\U0001F3FF]?|[\U0001F386-\U0001F393]|[\U0001F396\U0001F397\U0001F399-\U0001F39B\U0001F39E\U0001F39F]\uFE0F?|[\U0001F3A0-\U0001F3C1]|\U0001F3C2[\U0001F3FB-\U0001F3FF]?|[\U0001F3C3\U0001F3C4](?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|[\U0001F3C5\U0001F3C6]|\U0001F3C7[\U0001F3FB-\U0001F3FF]?|[\U0001F3C8\U0001F3C9]|\U0001F3CA(?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|[\U0001F3CB\U0001F3CC](?:\u200D[\u2640\u2642]\uFE0F?|[\uFE0F\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|[\U0001F3CD\U0001F3CE]\uFE0F?|[\U0001F3CF-\U0001F3D3]|[\U0001F3D4-\U0001F3DF]\uFE0F?|[\U0001F3E0-\U0001F3F0]|\U0001F3F3(?:\u200D(?:\u26A7\uFE0F?|\U0001F308)|\uFE0F(?:\u200D(?:\u26A7\uFE0F?|\U0001F308))?)?|\U0001F3F4(?:\u200D\u2620\uFE0F?|\U000E0067\U000E0062(?:\U000E0065\U000E006E\U000E0067|\U000E0073\U000E0063\U000E0074|\U000E0077\U000E006C\U000E0073)\U000E007F)?|[\U0001F3F5\U0001F3F7]\uFE0F?|[\U0001F3F8-\U0001F407]|\U0001F408(?:\u200D\u2B1B)?|[\U0001F409-\U0001F414]|\U0001F415(?:\u200D\U0001F9BA)?|[\U0001F416-\U0001F43A]|\U0001F43B(?:\u200D\u2744\uFE0F?)?|[\U0001F43C-\U0001F43E]|\U0001F43F\uFE0F?|\U0001F440|\U0001F441(?:\u200D\U0001F5E8\uFE0F?|\uFE0F(?:\u200D\U0001F5E8\uFE0F?)?)?|[\U0001F442\U0001F443][\U0001F3FB-\U0001F3FF]?|[\U0001F444\U0001F445]|[\U0001F446-\U0001F450][\U0001F3FB-\U0001F3FF]?|[\U0001F451-\U0001F465]|[\U0001F466\U0001F467][\U0001F3FB-\U0001F3FF]?|\U0001F468(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:\U0001F48B\u200D)?\U0001F468|[\U0001F33E\U0001F373\U0001F37C\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED]|\U0001F466(?:\u200D\U0001F466)?|\U0001F467(?:\u200D[\U0001F466\U0001F467])?|[\U0001F468\U0001F469]\u200D(?:\U0001F466(?:\u200D\U0001F466)?|\U0001F467(?:\u200D[\U0001F466\U0001F467])?)|[\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD])|\U0001F3FB(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:\U0001F48B\u200D)?\U0001F468[\U0001F3FB-\U0001F3FF]|[\U0001F33E\U0001F373\U0001F37C\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D\U0001F468[\U0001F3FC-\U0001F3FF]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?|\U0001F3FC(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:\U0001F48B\u200D)?\U0001F468[\U0001F3FB-\U0001F3FF]|[\U0001F33E\U0001F373\U0001F37C\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D\U0001F468[\U0001F3FB\U0001F3FD-\U0001F3FF]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?|\U0001F3FD(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:\U0001F48B\u200D)?\U0001F468[\U0001F3FB-\U0001F3FF]|[\U0001F33E\U0001F373\U0001F37C\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D\U0001F468[\U0001F3FB\U0001F3FC\U0001F3FE\U0001F3FF]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?|\U0001F3FE(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:\U0001F48B\u200D)?\U0001F468[\U0001F3FB-\U0001F3FF]|[\U0001F33E\U0001F373\U0001F37C\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D\U0001F468[\U0001F3FB-\U0001F3FD\U0001F3FF]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?|\U0001F3FF(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:\U0001F48B\u200D)?\U0001F468[\U0001F3FB-\U0001F3FF]|[\U0001F33E\U0001F373\U0001F37C\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D\U0001F468[\U0001F3FB-\U0001F3FE]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?)?|\U0001F469(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:\U0001F48B\u200D)?[\U0001F468\U0001F469]|[\U0001F33E\U0001F373\U0001F37C\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED]|\U0001F466(?:\u200D\U0001F466)?|\U0001F467(?:\u200D[\U0001F466\U0001F467])?|\U0001F469\u200D(?:\U0001F466(?:\u200D\U0001F466)?|\U0001F467(?:\u200D[\U0001F466\U0001F467])?)|[\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD])|\U0001F3FB(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:[\U0001F468\U0001F469][\U0001F3FB-\U0001F3FF]|\U0001F48B\u200D[\U0001F468\U0001F469][\U0001F3FB-\U0001F3FF])|[\U0001F33E\U0001F373\U0001F37C\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D[\U0001F468\U0001F469][\U0001F3FC-\U0001F3FF]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?|\U0001F3FC(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:[\U0001F468\U0001F469][\U0001F3FB-\U0001F3FF]|\U0001F48B\u200D[\U0001F468\U0001F469][\U0001F3FB-\U0001F3FF])|[\U0001F33E\U0001F373\U0001F37C\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D[\U0001F468\U0001F469][\U0001F3FB\U0001F3FD-\U0001F3FF]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?|\U0001F3FD(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:[\U0001F468\U0001F469][\U0001F3FB-\U0001F3FF]|\U0001F48B\u200D[\U0001F468\U0001F469][\U0001F3FB-\U0001F3FF])|[\U0001F33E\U0001F373\U0001F37C\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D[\U0001F468\U0001F469][\U0001F3FB\U0001F3FC\U0001F3FE\U0001F3FF]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?|\U0001F3FE(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:[\U0001F468\U0001F469][\U0001F3FB-\U0001F3FF]|\U0001F48B\u200D[\U0001F468\U0001F469][\U0001F3FB-\U0001F3FF])|[\U0001F33E\U0001F373\U0001F37C\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D[\U0001F468\U0001F469][\U0001F3FB-\U0001F3FD\U0001F3FF]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?|\U0001F3FF(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:[\U0001F468\U0001F469][\U0001F3FB-\U0001F3FF]|\U0001F48B\u200D[\U0001F468\U0001F469][\U0001F3FB-\U0001F3FF])|[\U0001F33E\U0001F373\U0001F37C\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D[\U0001F468\U0001F469][\U0001F3FB-\U0001F3FE]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?)?|\U0001F46A|[\U0001F46B-\U0001F46D][\U0001F3FB-\U0001F3FF]?|\U0001F46E(?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|\U0001F46F(?:\u200D[\u2640\u2642]\uFE0F?)?|[\U0001F470\U0001F471](?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|\U0001F472[\U0001F3FB-\U0001F3FF]?|\U0001F473(?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|[\U0001F474-\U0001F476][\U0001F3FB-\U0001F3FF]?|\U0001F477(?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|\U0001F478[\U0001F3FB-\U0001F3FF]?|[\U0001F479-\U0001F47B]|\U0001F47C[\U0001F3FB-\U0001F3FF]?|[\U0001F47D-\U0001F480]|[\U0001F481\U0001F482](?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|\U0001F483[\U0001F3FB-\U0001F3FF]?|\U0001F484|\U0001F485[\U0001F3FB-\U0001F3FF]?|[\U0001F486\U0001F487](?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|[\U0001F488-\U0001F48E]|\U0001F48F[\U0001F3FB-\U0001F3FF]?|\U0001F490|\U0001F491[\U0001F3FB-\U0001F3FF]?|[\U0001F492-\U0001F4A9]|\U0001F4AA[\U0001F3FB-\U0001F3FF]?|[\U0001F4AB-\U0001F4FC]|\U0001F4FD\uFE0F?|[\U0001F4FF-\U0001F53D]|[\U0001F549\U0001F54A]\uFE0F?|[\U0001F54B-\U0001F54E\U0001F550-\U0001F567]|[\U0001F56F\U0001F570\U0001F573]\uFE0F?|\U0001F574[\uFE0F\U0001F3FB-\U0001F3FF]?|\U0001F575(?:\u200D[\u2640\u2642]\uFE0F?|[\uFE0F\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|[\U0001F576-\U0001F579]\uFE0F?|\U0001F57A[\U0001F3FB-\U0001F3FF]?|[\U0001F587\U0001F58A-\U0001F58D]\uFE0F?|\U0001F590[\uFE0F\U0001F3FB-\U0001F3FF]?|[\U0001F595\U0001F596][\U0001F3FB-\U0001F3FF]?|\U0001F5A4|[\U0001F5A5\U0001F5A8\U0001F5B1\U0001F5B2\U0001F5BC\U0001F5C2-\U0001F5C4\U0001F5D1-\U0001F5D3\U0001F5DC-\U0001F5DE\U0001F5E1\U0001F5E3\U0001F5E8\U0001F5EF\U0001F5F3\U0001F5FA]\uFE0F?|[\U0001F5FB-\U0001F62D]|\U0001F62E(?:\u200D\U0001F4A8)?|[\U0001F62F-\U0001F634]|\U0001F635(?:\u200D\U0001F4AB)?|\U0001F636(?:\u200D\U0001F32B\uFE0F?)?|[\U0001F637-\U0001F644]|[\U0001F645-\U0001F647](?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|[\U0001F648-\U0001F64A]|\U0001F64B(?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|\U0001F64C[\U0001F3FB-\U0001F3FF]?|[\U0001F64D\U0001F64E](?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|\U0001F64F[\U0001F3FB-\U0001F3FF]?|[\U0001F680-\U0001F6A2]|\U0001F6A3(?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|[\U0001F6A4-\U0001F6B3]|[\U0001F6B4-\U0001F6B6](?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|[\U0001F6B7-\U0001F6BF]|\U0001F6C0[\U0001F3FB-\U0001F3FF]?|[\U0001F6C1-\U0001F6C5]|\U0001F6CB\uFE0F?|\U0001F6CC[\U0001F3FB-\U0001F3FF]?|[\U0001F6CD-\U0001F6CF]\uFE0F?|[\U0001F6D0-\U0001F6D2\U0001F6D5-\U0001F6D7\U0001F6DD-\U0001F6DF]|[\U0001F6E0-\U0001F6E5\U0001F6E9]\uFE0F?|[\U0001F6EB\U0001F6EC]|[\U0001F6F0\U0001F6F3]\uFE0F?|[\U0001F6F4-\U0001F6FC\U0001F7E0-\U0001F7EB\U0001F7F0]|\U0001F90C[\U0001F3FB-\U0001F3FF]?|[\U0001F90D\U0001F90E]|\U0001F90F[\U0001F3FB-\U0001F3FF]?|[\U0001F910-\U0001F917]|[\U0001F918-\U0001F91F][\U0001F3FB-\U0001F3FF]?|[\U0001F920-\U0001F925]|\U0001F926(?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|[\U0001F927-\U0001F92F]|[\U0001F930-\U0001F934][\U0001F3FB-\U0001F3FF]?|\U0001F935(?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|\U0001F936[\U0001F3FB-\U0001F3FF]?|[\U0001F937-\U0001F939](?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|\U0001F93A|\U0001F93C(?:\u200D[\u2640\u2642]\uFE0F?)?|[\U0001F93D\U0001F93E](?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|[\U0001F93F-\U0001F945\U0001F947-\U0001F976]|\U0001F977[\U0001F3FB-\U0001F3FF]?|[\U0001F978-\U0001F9B4]|[\U0001F9B5\U0001F9B6][\U0001F3FB-\U0001F3FF]?|\U0001F9B7|[\U0001F9B8\U0001F9B9](?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|\U0001F9BA|\U0001F9BB[\U0001F3FB-\U0001F3FF]?|[\U0001F9BC-\U0001F9CC]|[\U0001F9CD-\U0001F9CF](?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|\U0001F9D0|\U0001F9D1(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|[\U0001F33E\U0001F373\U0001F37C\U0001F384\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D\U0001F9D1|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD])|\U0001F3FB(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:\U0001F48B\u200D|)\U0001F9D1[\U0001F3FC-\U0001F3FF]|[\U0001F33E\U0001F373\U0001F37C\U0001F384\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D\U0001F9D1[\U0001F3FB-\U0001F3FF]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?|\U0001F3FC(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:\U0001F48B\u200D|)\U0001F9D1[\U0001F3FB\U0001F3FD-\U0001F3FF]|[\U0001F33E\U0001F373\U0001F37C\U0001F384\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D\U0001F9D1[\U0001F3FB-\U0001F3FF]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?|\U0001F3FD(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:\U0001F48B\u200D|)\U0001F9D1[\U0001F3FB\U0001F3FC\U0001F3FE\U0001F3FF]|[\U0001F33E\U0001F373\U0001F37C\U0001F384\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D\U0001F9D1[\U0001F3FB-\U0001F3FF]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?|\U0001F3FE(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:\U0001F48B\u200D|)\U0001F9D1[\U0001F3FB-\U0001F3FD\U0001F3FF]|[\U0001F33E\U0001F373\U0001F37C\U0001F384\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D\U0001F9D1[\U0001F3FB-\U0001F3FF]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?|\U0001F3FF(?:\u200D(?:[\u2695\u2696\u2708]\uFE0F?|\u2764\uFE0F?\u200D(?:\U0001F48B\u200D|)\U0001F9D1[\U0001F3FB-\U0001F3FE]|[\U0001F33E\U0001F373\U0001F37C\U0001F384\U0001F393\U0001F3A4\U0001F3A8\U0001F3EB\U0001F3ED\U0001F4BB\U0001F4BC\U0001F527\U0001F52C\U0001F680\U0001F692]|\U0001F91D\u200D\U0001F9D1[\U0001F3FB-\U0001F3FF]|[\U0001F9AF-\U0001F9B3\U0001F9BC\U0001F9BD]))?)?|[\U0001F9D2\U0001F9D3][\U0001F3FB-\U0001F3FF]?|\U0001F9D4(?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|\U0001F9D5[\U0001F3FB-\U0001F3FF]?|[\U0001F9D6-\U0001F9DD](?:\u200D[\u2640\u2642]\uFE0F?|[\U0001F3FB-\U0001F3FF](?:\u200D[\u2640\u2642]\uFE0F?)?)?|[\U0001F9DE\U0001F9DF](?:\u200D[\u2640\u2642]\uFE0F?)?|[\U0001F9E0-\U0001F9FF\U0001FA70-\U0001FA74\U0001FA78-\U0001FA7C\U0001FA80-\U0001FA86\U0001FA90-\U0001FAAC\U0001FAB0-\U0001FABA\U0001FAC0-\U0001FAC2]|[\U0001FAC3-\U0001FAC5][\U0001F3FB-\U0001F3FF]?|[\U0001FAD0-\U0001FAD9\U0001FAE0-\U0001FAE7]|\U0001FAF0[\U0001F3FB-\U0001F3FF]?|\U0001FAF1(?:\U0001F3FB(?:\u200D\U0001FAF2[\U0001F3FC-\U0001F3FF])?|\U0001F3FC(?:\u200D\U0001FAF2[\U0001F3FB\U0001F3FD-\U0001F3FF])?|\U0001F3FD(?:\u200D\U0001FAF2[\U0001F3FB\U0001F3FC\U0001F3FE\U0001F3FF])?|\U0001F3FE(?:\u200D\U0001FAF2[\U0001F3FB-\U0001F3FD\U0001F3FF])?|\U0001F3FF(?:\u200D\U0001FAF2[\U0001F3FB-\U0001F3FE])?)?|[\U0001FAF2-\U0001FAF6][\U0001F3FB-\U0001F3FF]?"
    extract_emoji = re.compile(emoji_rx)                   # Match a single emoji
    extract_emoji_chunks = re.compile(f'(?:{emoji_rx})+')  # Match one or more emojis
    extract_5_emoji_string = re.compile(f'^(?:{emoji_rx}){{5}}$')  # Match string of 5 emojis
    
    track = re.sub(extract_emoji,"",track)
    track = re.sub(extract_emoji_chunks,"",track)
    track = re.sub(extract_5_emoji_string,"",track)
    
    return track 

def remove_chinese(track):
    return ''.join(filter(lambda character:ord(character) < 0x3000,track))

def remove_emojis(text: str) -> str:
    return ''.join(c for c in text if c not in emoji.UNICODE_EMOJI)

def remove_emojis_v2(string):
    return emoji.get_emoji_regexp().sub(u'', string)


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

        # Find item with Max Value in Dictionary
        itemMaxValue = max(a.items(), key=lambda x: x[1])
        listOfKeys = list()
        # Iterate over all the items in dictionary to find keys with max value
        for key, value in a.items():
            if value == itemMaxValue[1]:
                listOfKeys.append(key)

        if len(listOfKeys) == 0:
            print("Can't determine genre...")
            return 

        elif len(listOfKeys) == 1:
            genre = str(listOfKeys[0])
            print("Processed genre as {}.".format(genre).strip())
            return genre

        elif len(listOfKeys) > 1:
            genre = str(select_randomly(listOfKeys)).strip()
            print("Keeping {} from list of artist genres as backup track genre.".format(genre))
            return genre
    else:
        return
        
def return_yt_info(final_info,single_info,spotify_track_dict_info):
    print("Searching Artist Albums for Song....")
    for key in final_info.keys():
        if str(key).strip() in spotify_track_dict_info.keys():
            yt_dlp_info = final_info[key]
            return yt_dlp_info

    print("Song is not part of Artist Albums...")
    print("Searching Artist's EPs....")  
    for key,value in single_info.items():
        if str(key).strip() in spotify_track_dict_info.keys():
            yt_dlp_singles_info = single_info[key]
            return yt_dlp_singles_info

    print("Song was not found in Artist's EPs....")
    return 

def test_album_names(artist_albums,value_to_check):
    for key,value in artist_albums.items():
        check_value = math.trunc(similar(str(value_to_check).lower().strip(),str(value).lower().strip()))
        if int(check_value) == int(100):
            return value_to_check
    return 

def find_tags(string):
    exit_list = []
    tags = [w.split()[0] for w in string.split('@')[1:]]
    hashtags = [w.split()[0] for w in string.split('#')[1:]]
    
    # using list comprehension to concat
    res_list = [y for x in [tags, hashtags] for y in x]
    
    for result in res_list:
        result =  re.sub("\s{0,}([^)\w\s]|_|\s{0,})+(?=\s|$)\s{0,}$", "", result, flags=re.IGNORECASE)
        exit_list.append(result)
    
    if exit_list:
        return exit_list
    else:
        return 


RECORD_LABEL_RULES = [
    r"\s*$",                 #  Remove multiple spaces
    r"(?i)\bLlc\b",          #  Remove capital insensitive LLC
    r"(?i)(?<!^)\b[b]{1,}[y]{1,}\b\s{1,}\w+\s{0,}$" # Remove if one word after "by" then end of string 
]

def format_record_label(record_label):
    print("\n")

    print("Before Regexes : {}".format(str(record_label).strip()))

    for x in RECORD_LABEL_RULES:
        record_label = re.sub(x, "", record_label, flags=re.IGNORECASE)
    
    print("After Regexes : {}".format(record_label.strip()))

    if len(record_label) <= 4:
        record_label = str(record_label).upper()

    print("After Capitalization of Small Label : {}".format(record_label))

    record_label = record_label.split()

    for index, word in enumerate(record_label):
        print(word)
        if len(word) <= int(2):
            if index != 0 and word not in Escape_Words:
                record_label[index] = word.upper()
        else:
            record_label[index] = word.capitalize()

    record_label = ' '.join(record_label)
    
    print("After capitalization {}".format(record_label).strip())

    try:
        for m in re.finditer("\/[a-z]",record_label):
            character_after_slash = int(m.end()-1)
            record_label = record_label[:character_after_slash] + record_label[character_after_slash].upper() + record_label[character_after_slash+1:]
    
        print("Replace character after slash : {}".format(record_label))

    except:
        pass  
    
    print("\n")
    return record_label

REMOVE_QUOTES_LIST =[ 
    r'(?i)\"(.+?)\"',
    r"(?i)\'(?:\b\w+\s{0,}){1}\'",
    r"(?i)\“(?:\b\w+\s{0,}){1}\”",
    r"(?i)\“\”",
    r'(?=\b.*\b)(?=\').(?![^\s$])',
    r'\s{1,}(?=\').(?=\b.*\b)',
    r"(?!\b.*\b)\‘(?!\b.*\b)"
]

def remove_quotes_from_string(youtube_video_full_title):
    youtube_video_full_title = str(youtube_video_full_title).strip()

    for quote_pattern in REMOVE_QUOTES_LIST:
        pattern = re.compile(quote_pattern)
        for match in re.finditer(pattern, youtube_video_full_title):
            youtube_video_full_title = youtube_video_full_title[:match.start()] + " " + youtube_video_full_title[match.start() + 1:match.end()-1] + youtube_video_full_title[match.end():]

    youtube_video_full_title = convert_string(youtube_video_full_title)

    return youtube_video_full_title

def second_parenthesis(youtube_video_full_title):
    if (youtube_video_full_title.find(')') != -1):
        all_string_parenthesis = matching_parentheses(youtube_video_full_title)
    
        if all_string_parenthesis:
            if (len(all_string_parenthesis.keys()) > 1):
                keys=list(sorted(all_string_parenthesis.keys()))  #get list of keys from dictionary
                keys.pop(0)  #Remove first in list of keys
                for key in keys:
                    no_delete =  re.search(r"(?i)^((?!Remix|Mix|feat|featuring|Feat[.]{1}|ft[.]{1}).)*$",youtube_video_full_title, re.IGNORECASE)
                    if no_delete is not None:
                        youtube_video_full_title = youtube_video_full_title[:key-1] + youtube_video_full_title[all_string_parenthesis[key]+1:]
        
    return youtube_video_full_title

FINAL_CLEANUP_LIST = [
    r"\s{0,}\-\s{0,}(?=\])", # Clean up after dash
    r"\s{0,}([^)\']\w\s]|_|\s{0,})+(?=\s|$)\s{0,}$", # Special Characters and Spaces at the end of String
    r"^\W+",
    r"[\[$&+,:;=?@#|'<>.^*(%\"\£_!-]{1,}$",
    r"(?<!\w)'(?!\w+)",
    r"[\%\/\\\&\?\,\'\;\:\!\-\:\)]{2,}"
]

def final_cleanup(youtube_video_full_title):
    
    for x in FINAL_CLEANUP_LIST:
        youtube_video_full_title = re.sub(x, "", youtube_video_full_title, flags=re.IGNORECASE)
    
    return youtube_video_full_title

DOT_REGEXES = [
    r"(([a-zA-Z]\.){3,})",
    r"\b\w{1}[.]{1}\w{1}(?=\s|$)"
]

def capitalize_words_with_dots(youtube_full_title):
    for regex in DOT_REGEXES:
        pattern = re.compile(regex)
        for match in re.finditer(pattern, youtube_full_title):
            youtube_full_title = youtube_full_title[:match.start()] + str(youtube_full_title[match.start():match.end()]).upper() + youtube_full_title[match.end():]

    return youtube_full_title

def capitalize_words_correctly(youtube_full_title):
    d = enchant.Dict("en_US")
    after_keywords=["ft."]
    words = youtube_full_title.lower().split()
    for key in after_keywords:
        if key in words[1:]:
            previous_word = words[words.index(key)-1]
            if (len(previous_word) <= 4):
                for x in words:
                    words[words.index(x)] = convert_string(words[words.index(x)])
                if d.check(previous_word) is False:
                    words[words.index(key)-1] = previous_word.upper()  
        
    youtube_full_title =  ' '.join(words)

    before_keywords=["-"]
    title_seperated = youtube_full_title.lower().split()
    for key in before_keywords:
        if key in title_seperated[1:]:
            after_word = title_seperated[title_seperated.index(key)+1]
            if (len(after_word) <= 4):
                for x in title_seperated:
                    try:
                        if  title_seperated[title_seperated.index(key)+2] in after_keywords:
                            if d.check(after_word) is False:
                                title_seperated[title_seperated.index(key)+1] = after_word.upper()
                    except IndexError:
                        if title_seperated.index(x) == (len(title_seperated)-1):
                            if d.check(after_word) is False:
                                title_seperated[title_seperated.index(key)+1] = after_word.upper()
                        
    youtube_full_title = ' '.join(title_seperated)

    result = all([i.islower() for i in youtube_full_title.split()])

    if result is False:
        list_of_strings = youtube_full_title.split()
        for i in list_of_strings:
            test = re.search("\s{0,}[-]\s{0,}",i)
            if test is None:
                if list_of_strings[list_of_strings.index(i)].islower():
                    if list_of_strings[list_of_strings.index(i)] is not Escape_Words:
                        if d.check(list_of_strings[list_of_strings.index(i)]) is True:
                            list_of_strings[list_of_strings.index(i)] = list_of_strings[list_of_strings.index(i)].capitalize()

        youtube_full_title = ' '.join(list_of_strings)

    return youtube_full_title

def smiley_cleaner(youtube_full_title):
    # approach 1: pattern for "generic smiley"
    pattern1 = re.compile(r"(?i)\s{1,}[:;7BX=]{1}[-~'\^]{0,1}[)(\/\|DP]{1}\b(?=\s{1,}|$)")

    # approach 2: disjunction of a list of smileys
    smileys = """:-) :) :o) :] :3 :c) :> =] 8) =) :} :^) 
                :D 8-D 8D x-D xD X-D XD =-D =D =-3 =3 B^D""".split()
    pattern2 = "|".join(map(re.escape, smileys))

    youtube_full_title = re.sub(pattern1,"",youtube_full_title)
    youtube_full_title = re.sub(pattern2,"",youtube_full_title)

    return youtube_full_title
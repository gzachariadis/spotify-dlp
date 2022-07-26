from __future__ import print_function
from ast import pattern
from calendar import c
from curses.ascii import islower
import re
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
    r"(?i)\[{1,}\s{0,}(?!VIP)(?!Original)(?:\w+){1}\s{0,}\]{1,}",  # A Single Word in Parenthesis not VIP    # (freestyle) # (YGK) if not (VIP)   # (Freeway) - A single word? ( KiingRod )
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
    r"(?i)\[{1,}\s{0,}\W+\s{0,}tune\s{1,}(?:\b\w+\s{0,}){1,5}\s{0,}\]{1,}" # **tune of the Week

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
    r"(?i)[(]{1,}Official\s{0,}(?:Music)?\s{0,}Video[)]{1,}",
    r"(?i)[(]{1,}Official\s{0,}(?:Music)?\s{0,}Visualizer[)]{1,}",
    r"(?i)[(]{1,}(?:Music)?\s{0,}Visualizer[)]{1,}",
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
    r"(?i)[(]{1,}\s{0,}(?!VIP)(?!Original)(?:\w+){1}\s{0,}[)]{1,}",  # A Single Word in Parenthesis not VIP    # (freestyle) # (YGK) if not (VIP)   # (Freeway) - A single word? ( KiingRod )
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
    r"(?i)[(]{1,}\s{0,}\W+\s{0,}tune\s{1,}(?:\b\w+\s{0,}){1,5}\s{0,}[)]{1,}" # (**tune of the Week)
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
    r"(?i)\s{1,}Lyrics[.]{1,}(\s{1,}|$)"
]

artist_track_seperators = [
    r"(?<=[a-zA-Z])-(?=[a-zA-Z]{2,})"  
]

word_seperators = [
    r"(?<=[a-zA-Z])\\(?=[a-zA-Z]{2,})",
    r"(?<=[a-zA-Z])[|]{1}(?=[a-zA-Z]{2,})",
    r"(?<=[a-zA-Z])//(?=[a-zA-Z]{2,})",
    r"(?<=[a-zA-Z])/(?=[a-zA-Z]{2,})",  
]

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

    if len(matches) > 0:
        for index in matches:
            full_title = full_title[0:int(index)] + " - " + full_title[int(index)+1:]
    
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

Escape_Words = ["the","and","are","is","was","were","by","of","no","so","with","be","to","a","be","ft.","n","v","vs","us","me"]

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

def remove_quotes_from_string(youtube_video_full_title):
    youtube_video_full_title = str(youtube_video_full_title).strip()

    for match in re.finditer(r'(?i)\"(.+?)\"', youtube_video_full_title):
        youtube_video_full_title = youtube_video_full_title[:match.start()] + " " + youtube_video_full_title[match.start() + 1:match.end()-1] + youtube_video_full_title[match.end():]

    for match in re.finditer(r"(?i)\'(?:\b\w+\s{0,}){1}\'", youtube_video_full_title):
        youtube_video_full_title = youtube_video_full_title[:match.start()] + " " + youtube_video_full_title[match.start() + 1:match.end()-1] + youtube_video_full_title[match.end():]

    for match in re.finditer(r"(?i)\“(?:\b\w+\s{0,}){1}\”", youtube_video_full_title):
        youtube_video_full_title = youtube_video_full_title[:match.start()] + " " + youtube_video_full_title[match.start() + 1:match.end()-1] + youtube_video_full_title[match.end():]

    for match in re.finditer(r"(?i)\“\”", youtube_video_full_title):
        youtube_video_full_title = youtube_video_full_title[:match.start()] + " " + youtube_video_full_title[match.start() + 1:match.end()-1] + youtube_video_full_title[match.end():]

    youtube_video_full_title = convert_string(youtube_video_full_title)

    return youtube_video_full_title

FINAL_CLEANUP_LIST = [
    r"\s{0,}\-\s{0,}(?=\])", # Clean up after dash
    r"\s{0,}([^)\']\w\s]|_|\s{0,})+(?=\s|$)\s{0,}$", # Special Characters and Spaces at the end of String
    r"^\W+"
]

def final_cleanup(youtube_video_full_title):
    
    for x in FINAL_CLEANUP_LIST:
        youtube_video_full_title = re.sub(x, "", youtube_video_full_title, flags=re.IGNORECASE)
    
    return youtube_video_full_title

def capitalize_words_correctly(youtube_full_title):
    after_keywords=["ft."]
    words = youtube_full_title.lower().split()
    for key in after_keywords:
        if key in words[1:]:
            previous_word = words[words.index(key)-1]
            if (len(previous_word) < 4):
                for x in words:
                    words[words.index(x)] = convert_string(words[words.index(x)])
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
                            title_seperated[title_seperated.index(key)+1] = after_word.upper()
                    except IndexError:
                        if title_seperated.index(x) == (len(title_seperated)-1):
                            title_seperated[title_seperated.index(key)+1] = after_word.upper()
                        
          
    youtube_full_title = ' '.join(title_seperated)

    result = all([i.islower() for i in youtube_full_title.split()])

    if result is False:
        list_of_strings = youtube_full_title.split()
        for i in list_of_strings:
            test =re.search("\s{0,}[-]\s{0,}",i)
            if test is None:
                if list_of_strings[list_of_strings.index(i)].islower():
                    if list_of_strings[list_of_strings.index(i)] is not Escape_Words:
                        list_of_strings[list_of_strings.index(i)] = list_of_strings[list_of_strings.index(i)].capitalize()

        youtube_full_title = ' '.join(list_of_strings)

    return youtube_full_title

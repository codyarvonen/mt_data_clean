import re
from difflib import SequenceMatcher

print("Reading input file...")

# Open the file to clean
file = open("raw_data.txt", "r")
file_text = file.read()

print("Finding segments...")

# Find all of the text segments
phrases = re.findall("<seg>.*?</seg>", file_text, re.DOTALL)

# Open result files
result_en = open("result_eng.txt", "w")
result_es = open("result_esp.txt", "w")

dictionary = {}
source_phrase = ""

print("Regex filtering...")

# Clean each text segment
for index, phrase in enumerate(phrases):

    phrase = phrase.strip(". ")

    # Detect and fix technical issues in the content
    phrase = re.sub("\n|\t|\r|\*", " ", phrase)
    phrase = re.sub(r"\\n", "", phrase)
    
    phrase = re.sub(r"\\", "", phrase)

    # Normalize escaped characters/entities
    phrase = re.sub("&lt;", "<", phrase)
    phrase = re.sub("&gt;", ">", phrase)
    phrase = re.sub("&amp;", "&", phrase)
    phrase = re.sub("&mdash;", "--", phrase)
    phrase = re.sub("&ndash;|&#8211;", "-", phrase)
    phrase = re.sub(u"\u00A0", " ", phrase)
    phrase = re.sub(u"\u2026", " ", phrase)
    phrase = re.sub(u"\u2020", " ", phrase)
    phrase = re.sub("&nbsp;|&middot;|•|©|�|&rarr;|&larr;|&hellip;|&copy|&#xd;|&#x202f;", " ", phrase)
    phrase = re.sub("&shy;", "", phrase)
    phrase = re.sub("&atilde;", "ã", phrase)

    # Normalize quotes
    phrase = re.sub("&quot;|&rdquo;|&ldquo;|“|”", "\"", phrase)
    phrase = re.sub("&lsquo;|&rsquo;|&#39;|‘|’|&#x2019;", "\'", phrase)
    
    

    # Removing tags that don’t affect the meaning
    phrase = re.sub("<.*?>|{.*?}|\\($.*?\\)", " ", phrase)

    # Check unbalanced brackets(? – you should probably remove these, too)
    phrase = re.sub("{|}", "", phrase)

    # Normalize certain control characters and normalize whitespaces
    phrase = re.sub(" +", " ", phrase)
    phrase = re.sub("^ ", "", phrase)

    phrase = re.sub("^\.*", "", phrase)
    phrase = re.sub("&amp;", "&", phrase)
    phrase = phrase.strip(". ")
    phrase = re.sub("[0-9]$", "", phrase)

    if index % 2 == 0:
        source_phrase = phrase
    else:
        dictionary[source_phrase] = phrase

print("Deleting entries...")

print("Number of items in dictionary: {0}".format(len(dictionary)))

for source in list(dictionary):
    # Remove empty segments (source or target)
    # Remove segments that are too long (>100 words) (13)
    # Remove segments that are too short(<3 words) (14)
    # Identify and remove duplicates with no context for MT training purposes
    # Check sentence length ratios and remove if the ratio exceeds your threshold (16)
    # Characters that do not match either the expected source or target language(? - only if you have lists of valid characters to use)
    # Do not remove segments where source = target(? – you probably should remove them)
    if isinstance(dictionary[source], list):
        dictionary.pop(source)
    else:
        rm_entry = (dictionary[source].isspace() or source.isspace() or len(dictionary[source].split()) > 100 or 
                    len(dictionary[source].split()) < 3 or len(source.split()) > 100 or 
                    len(source.split()) < 3  or source is None or dictionary[source] is None or 
                    len(dictionary[source].split()) > (2 * len(source.split())) or 
                    len(source.split()) > (2 * len(dictionary[source].split())) or source == dictionary[source] or
                    re.search("á|é|í|ó|ú|ñ", source) is not None or SequenceMatcher(None, source, dictionary[source]).ratio() > 0.9)

        if rm_entry:
            dictionary.pop(source)

print("Still deleting entries...")

print("Number of items in dictionary: {0}".format(len(dictionary)))

# Remove entries consisting of only punctuation, whitespace, or tags (like #8)
# Check if a segment contains mostly non-text content            
for source in list(dictionary):
    num_char_source = len(source)
    num_char_target = len(dictionary[source])
    num_alpha_source = 0
    num_alpha_target = 0
    for char in source:
        if char.isalpha() or char.isspace(): 
            num_alpha_source += 1
    for char in dictionary[source]:
        if char.isalpha() or char.isspace(): 
            num_alpha_target += 1

    if (num_alpha_source/num_char_source) < 0.8 or (num_alpha_target/num_char_target) < 0.8:
        dictionary.pop(source)

print("Printing entries...")

# Print dictionary to text file
for source in dictionary:
    result_en.write(source)        
    result_en.write("\n")
    result_es.write(dictionary[source])        
    result_es.write("\n")
    
print("Number of items in dictionary: {0}".format(len(dictionary)))
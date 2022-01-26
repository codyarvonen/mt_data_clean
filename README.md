# mt_data_clean
This repository contains the `mt_data_clean.py` file that pipelines the machine translation data cleaning process for the English to Spanish data given to me in class. 

First, I downloaded the three .tmx files and concatenated them all into one and save it as a single .txt file. This file containing all of the raw TMX data is not included in this repository because github limits the upload file size to 100 MB and that file is about 1200 MB.

Second, I wrote the `mt_data_clean.py` script to pipeline the cleaning process. The following 16 bullet points are the cleaning steps I took and the associated code snippet from `mt_data_clean.py` that executes task. Note that to implement the desired regular expression functionality, the following imports were used:
```
import re
from difflib import SequenceMatcher
```

1. Detect and fix technical issues in the content. This is done by parsing the TMX data into a python list of strings using the regular expression found on line 13. This allows us to search for and delete any extra newline characters because newline characters are no longer used to determine when a text segment ends, the python list does that now. Removal of newline characters is performed with the regular expressions on lines 30 and 31.
```
13  phrases = re.findall("<seg>.*?</seg>", file_text, re.DOTALL)
30  phrase = re.sub("\n|\t|\r|\*", " ", phrase)
31  phrase = re.sub(r"\\n", "", phrase)
```

2. Remove empty segments (source or target). In order to do this, we simply put the source and target texts into a python dictionary and searched for instances of None. This can be found in a series of or statements on line 91. This dictionary has proved very useful for future steps as well.
```
91  if (source is None or dictionary[source] is None):
```

3. Normalize escaped characters/entities and normalize certain control characters/. This is done using regular expressions on each line of text and replacing the escaped/control character or entity with an acceptable character. This can be found on lines 36-46.
```
36  phrase = re.sub("&lt;", "<", phrase)
37  phrase = re.sub("&gt;", ">", phrase)
38  phrase = re.sub("&amp;", "&", phrase)
39  phrase = re.sub("&mdash;", "--", phrase)
40  phrase = re.sub("&ndash;|&#8211;", "-", phrase)
41  phrase = re.sub(u"\u00A0", " ", phrase)
42  phrase = re.sub(u"\u2026", " ", phrase)
43  phrase = re.sub(u"\u2020", " ", phrase)
44  phrase = re.sub("&nbsp;|&middot;|•|©|�|&rarr;|&larr;|&hellip;|&copy|&#xd;|&#x202f;", " ", phrase)
45  phrase = re.sub("&shy;", "", phrase)
46  phrase = re.sub("&atilde;", "ã", phrase)
```
4. Normalize whitespaces. This is done by finding all instances of one or more spaces in a line of text and replacing it with a single space. I also wrote an extra regular expression to get rid of single spaces at the beginning of lines of text. This can be found in lines 61 and 62.
```
61  phrase = re.sub(" +", " ", phrase)
62  phrase = re.sub("^ ", "", phrase)
```

5. Normalize quotes. This is done by finding all quote character representations and replacing them with their corresponding straight quotes. This can be found on lines 49 and 50.
```
49  phrase = re.sub("&quot;|&rdquo;|&ldquo;|“|”", "\"", phrase)
50  phrase = re.sub("&lsquo;|&rsquo;|&#39;|‘|’|&#x2019;", "\'", phrase)
```

6. Removing tags that don’t affect the meaning. Using regular expressions, I identified the instances of tags using <...>, {...}, and ($...) notation and removed them from the line of text as shown in line 55.
```
55 phrase = re.sub("<.*?>|{.*?}|\\($.*?\\)", " ", phrase)
```

7. Identify and remove duplicates with no context for MT training purposes. The beauty of using the python dictionary data structure is that all duplicates in the source are automatically removed. This is good because we do not want two source phrases mapping to different target phrases. It will confuse the neural model. However, to delete the different target phrases associated with source phrase, I had to check if the dictionary value was an instance of a list. If so, that dictionary element is deleted as seen in lines 86 and 87.
```
86  if isinstance(dictionary[source], list):
87      dictionary.pop(source)
```

8. Check if a segment contains mostly non-text content. To do this, I counted the number of alphabetic characters by the total number of characters in a line of text in order to get a percentace value. Then I determined if the percentage value was high enough to assume the line was mostly non-text and should be deleted. This is shown in the loop on line 104.
```
104 for source in list(dictionary):
117 if (num_alpha_source/num_char_source) < 0.8 or (num_alpha_target/num_char_target) < 0.8:
118     dictionary.pop(source)
```

9. Characters that do not match either the expected source or target language. For this step, I searched for special Spanish characters (e.g. accented vowels) in the Engligh source. If there was an instance, I deleted the entry as shown in line 94.
```
94  if (re.search("á|é|í|ó|ú", source) is not None):
```

10. Remove segments where source = target. This is done by identifying the python dictionary entries where `source == dictionary[source]` as shown on line 93. Note, the following method: `SequenceMatcher(None, source, dictionary[source]).ratio()` is used the determine how similar the strings are and if they are within a certain threshold, they will be removed. This method is great bbut slows down the program a lot and can be removed if desired.

11. Check unbalanced brackets. This is done using regular expressions on each line to identify and replace extraneous brackets as seen on line 58.
```
58  phrase = re.sub("{|}", "", phrase)
```

12. Remove entries consisting of only punctuation, whitespace, or tags. This is done primarily using the method outlined in step 8. This is also done by checking if `dictionary[source].isspace() or source.isspace()` as shown on line 89.

13. Remove segments that are too long (>100 words). This is done by counting the words in a line of text for the source or target and determining if there are more than 100 words as shown in lines 89 and 90.

14. Remove segments that are too short(<3 words). This is done by counting the words in a line of text for the source or target and determining if there are less than 3 words as shown in lines 90 and 91.
```
89  len(dictionary[source].split()) > 100 or 
90  len(dictionary[source].split()) < 3 or len(source.split()) > 100 or 
91  len(source.split()) < 3
```



15. Misalignments (manual check). This is done by verifying that the total number of dictionary elements that are printed at the end of the program is equal to the nnumber of lines in each of the respective result text files.

16. Check sentence length ratios and remove if the ratio exceeds your threshold. This is done by making sure the source is not twice as big as the target and vice-versa, as shown in lines 92 and 93.
```
92  len(dictionary[source].split()) > (2 * len(source.split())) or 
93  len(source.split()) > (2 * len(dictionary[source].split()))
```

After `mt_data_clean.py` is run, the source elements from the python dictionary are placed in the `result_eng.txt` file and the target elements in the `result_esp.txt` file. These files have been uploaded to the link specified in class. 
import requests
import re

# Workaround for broken description fetching in PyTube library. Code taken from comment on this issue at GitHub:
# https://github.com/pytube/pytube/issues/1626
#
# Also implements string formatting code found from Stack Overflow threads here:
# https://stackoverflow.com/questions/4020539/process-escape-sequences-in-a-string-in-python
# https://stackoverflow.com/questions/53955397/issue-in-encode-decode-in-python-3-with-non-ascii-character


def desc_fetcher(url):
    full_html = requests.get(url).text
    y = re.search(r'shortDescription":"', full_html)
    desc = ''
    count = y.start() + 19  # adding the length of the 'shortDescription":"
    while True:
        # get the letter at current index in text
        letter = full_html[count]
        if letter == "\"":
            if full_html[count - 1] == "\\":
                # this is case where the letter before is a backslash, meaning it is not real end of description
                desc += letter
                count += 1
            else:
                break
        else:
            desc += letter
            count += 1

    formatted_output = bytes(desc, 'latin1', errors='backslashreplace').decode('unicode-escape')

    return formatted_output

#!/usr/bin/python

import os
import sys
import codecs
import operator

def usage():
    return '''
This script extracts words and counts from a 2006 wiktionary word frequency study over American
television and movies. To use, first visit the study and download, as .html files, all 26 of the
frequency lists:

https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists#TV_and_movie_scripts

Put those into a single directory and point it to this script:

%s wiktionary_html_dir ../data/spoken_english.txt

output.txt will include one line per word in the study, ordered by rank, of the form:

word1 count1
word2 count2
...
    ''' % sys.argv[0]

def parse_wiki_tokens(html_doc_str):
    '''fragile hax, but checks the result at the end'''
    results = []
    last3 = ['', '', '']
    header = True
    for line in html_doc_str.split('\n'):
        last3.pop(0)
        last3.append(line.strip())
        if all(s.startswith('<td>') and not s == '<td></td>' for s in last3):
            if header:
                header = False
                continue
            last3 = [s.replace('<td>', '').replace('</td>', '').strip() for s in last3]
            rank, token, count = last3
            rank = int(rank.split()[0])
            token = token.replace('</a>', '')
            token = token[token.index('>')+1:].lower()
            count = int(count)
            results.append((rank, token, count))
    assert len(results) in [1000, 2000, 1284] # early docs have 1k entries, later 2k, last 1284
    return results

def main(wiktionary_html_root, output_filename):
    rank_token_count = [] # list of 3-tuples
    for filename in os.listdir(wiktionary_html_root):
        path = os.path.join(wiktionary_html_root, filename)
        with codecs.open(path, 'r', 'utf8') as f:
            rank_token_count.extend(parse_wiki_tokens(f.read()))
    rank_token_count.sort(key=operator.itemgetter(0))
    with codecs.open(output_filename, 'w', 'utf8') as f:
        last_rank = 0
        for rank, token, count in rank_token_count:
            assert rank == last_rank + 1
            last_rank = rank
            f.write('%-18s %d\n' % (token, count))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print usage()
    else:
        main(*sys.argv[1:])
    sys.exit(0)
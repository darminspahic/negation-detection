#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Author: Darmin Spahic <Spahic@stud.uni-heidelberg.de>
Project: Negation Detection

Module name:
extract_cuewords

Short description:
This module extracts negation cue words from xml files
and writes them into a txt file, one word per line.

License: MIT License
Version: 1.0

"""

# Import dependencies
import codecs
import os
import sys

from bs4 import BeautifulSoup
import lxml

XML_TRAIN_FILES_PATH = '../../res/xml/train/'
XML_TRAIN_FILES_OUTPUT_PATH = '../../res/xml/train/output/'

CUEWORDS_DATA_PATH = '../../res/cuewords/'
CUEWORDS_STATS_PATH = '../../res/cuewords/stats/'

CUEWORDS_FILE = 'baskerville_cuewords.txt'
CUEWORDS_FILE_POS_TAGGED = 'baskerville_cuewords_postagged.txt'

NEGATION_FRAME_NAME = 'Negation' #CaseSensitive

def extract_cuewords(cuewords, xml_file_path):
    """ This function extracts negation cuewords from xml files
        and writes them into a txt file, one word per line.

        Args:
            cuewords (str): Path to an empty txt file for output
            xml_file_path (str): Path to input files

        Returns:
            Two written files with negation cues alphabetically sorted
            and without duplicates, one file contains POS tags.

        Example:
            >>> extract_cuewords('../res/cuewords/baskerville_cuewords.txt', '../res/xml/train/')
    """

    try:
        file_output = open(CUEWORDS_DATA_PATH+CUEWORDS_FILE, 'w', encoding='utf8')
        file_output_pos_tagged = open(CUEWORDS_DATA_PATH+CUEWORDS_FILE_POS_TAGGED,
                                      'w', encoding='utf8')

    except FileNotFoundError:
        print('Please set correct filenames')

    # Empty lists for collecting data per file
    cueword_ids = []
    cuewords = []

    # Empty list to collect data for all files
    all_cuewords = []
    all_cuewords_pos_tagged = []

    print('Extracting cuewords from:', xml_file_path, 'to:', CUEWORDS_DATA_PATH+CUEWORDS_FILE)

    # Go through all files in xml_file_path directory
    for file in os.listdir(xml_file_path):

        # For each file, open, parseXML
        file = xml_file_path+file

        # Open files only, ignore subdirectories
        if os.path.isfile(file) and file.lower().endswith('.xml'):

            file_input = open(file, 'r', encoding='utf8')
            file_input = BeautifulSoup(file_input, 'xml')

            # Collect frames, get ids
            for frame in file_input.find_all('frame', {'name' : NEGATION_FRAME_NAME}):
                for target in frame.find_all('target'):
                    for fenode in target.find_all('fenode'):
                        cueword_ids.insert(0, fenode.get('idref'))

            # Find all splitwords
            for splitword in file_input.find_all('splitword'):
                cueword_ids.insert(0, splitword.get('idref'))

            # Find all terminals, check if its ID is in cueword_ids[]
            for terminal in file_input.find_all('t'):
                if terminal.get('id') in cueword_ids:
                    all_cuewords.insert(0, terminal.get('word').lower())
                    all_cuewords_pos_tagged.insert(0, terminal.get('word').lower()+
                                                   '\t'+terminal.get('pos'))

            # clear list for next document
            cueword_ids = []
            cuewords = []

    # Sort final list
    all_cuewords = sorted(set(all_cuewords))
    all_cuewords_pos_tagged = sorted(set(all_cuewords_pos_tagged))

    # Write cuewords without duplicates to file:
    for cueword in all_cuewords:
        file_output.write(cueword+'\n')

    for cueword in all_cuewords_pos_tagged:
        file_output_pos_tagged.write(cueword+'\n')

    file_output.close()
    file_output_pos_tagged.close()

    print('Cuewords extracted to:', file_output.name)
    print('Cuewords extracted and POS tagged to:', file_output_pos_tagged.name)
    print('Done!')

if __name__ == "__main__":
    extract_cuewords(CUEWORDS_FILE, XML_TRAIN_FILES_PATH)

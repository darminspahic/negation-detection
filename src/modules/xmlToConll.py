#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Author: Darmin Spahic <Spahic@stud.uni-heidelberg.de>
Project: Negation Detection

Module name:
xml_to_conll

Short description:
This module transforms corpus xml files into the
CoNLL-2009 format, which is needed for dependency parsing.

License: MIT License
Version: 1.0

"""

# import dependencies
import os, sys
import codecs
from bs4 import BeautifulSoup
import lxml

XML_TRAIN_FILES_PATH = '../../res/xml/train/'
CONLL_PATH = '../../res/conll/'

# get Sentences and Terminals; write CoNLL-2009: http://ufal.mff.cuni.cz/conll2009-st/task-description.html
# Columns overview
# ID FORM LEMMA PLEMMA POS PPOS FEAT PFEAT HEAD PHEAD DEPREL PDEPREL FILLPRED PRED APRED1 APRED2 APRED3 APRED4 APRED5 APRED6

def xml_to_conll(xml_file_path):
        """ This function transforms corpus xml files into the CoNLL-2009 format
            which is needed for dependency parsing.

            Args:
                xml (str): Path to corpus files in tiger xml format

            Returns:
                The written files with .conll extension

            Example:
                >>> xml_to_conll('../res/xml/train/')
        """

        for file in os.listdir(xml_file_path):

            # Set path to file
            file = xml_file_path+file

            # Open files only, ignore subdirectories
            if os.path.isfile(file) and file.lower().endswith('.xml'):

                # Open Files
                chapter_input = open(file, 'r', encoding='utf8')

                # Create Same Filename in Output Folder
                chapter_output = open(CONLL_PATH+os.path.split(file)[-1]+'.conll', 'w', encoding='utf8')

                print('Converting: ' + chapter_input.name + ' to Conll09 file: ' + chapter_output.name)

                chapter_input = BeautifulSoup(chapter_input, 'xml')
                for sentence in chapter_input.find_all('s'):
                    line_id = 0
                    for terminal in sentence.find_all('t'):
                        line_id, terminal_id, form, lemma, plemma = line_id+1, terminal.get('id'), terminal.get('word'), terminal.get('lemma'), terminal.get('lemma')
                        pos, ppos = terminal.get('pos'), terminal.get('pos')
                        feat, pfeat, head, phead, deprel, pdeprel, fillpred, pred, apred1 = "_" * 9 # <3 Python!
                        chapter_output.write("%s" "\t" "%s" "\t" "%s" "\t" "%s" "\t" "%s" "\t" "%s" "\t" "%s" "\t"
                                             "%s" "\t" "%s" "\t" "%s" "\t" "%s" "\t" "%s" "\t" "%s" "\t" "%s" "\t" "%s" "\n"
                                             % (str(line_id)+"-"+terminal_id, form, lemma, plemma, pos, ppos, feat, pfeat, head, phead, deprel, pdeprel, fillpred, pred, apred1))
                    chapter_output.write("\n")

                chapter_output.close()

        print("Done!")

if __name__ == "__main__":

    xml_to_conll(XML_TRAIN_FILES_PATH)

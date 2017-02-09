#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Author: Darmin Spahic <Spahic@stud.uni-heidelberg.de>
Project: Negation Detection

Module name:
NegationDetection

Short description:
This is the main module and it is a collection of all
modules from the project.

License: MIT License
Version: 1.0

"""

import codecs
import os
import sys

from bs4 import BeautifulSoup
import lxml

import numpy as np

from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import jaccard_similarity_score

################
# PATH SETTINGS
################

XML_TRAIN_FILES_PATH = '../res/xml/train/'
XML_TEST_FILES_PATH = '../res/xml/test/'

XML_TRAIN_FILES_OUTPUT_PATH = '../res/xml/train/output/'
XML_TEST_FILES_OUTPUT_PATH = '../res/xml/test/output/'

XML_TRAIN_FILES_TAGGED_PATH = '../res/xml/train/output/tagged/'
XML_TEST_FILES_TAGGED_PATH = '../res/xml/test/output/tagged/'

CUEWORDS_DATA_PATH = '../res/cuewords/'
CUEWORDS_STATS_PATH = '../res/cuewords/stats/'

CUEWORDS_FILE = 'baskerville_cuewords.txt'
CUEWORDS_FILE_POS_TAGGED = 'baskerville_cuewords_postagged.txt'

CONLL_PATH = '../res/conll/'

TRAIN_RESULTS_FILE = '../results/results-train.txt'
TEST_RESULTS_FILE = '../results/results-test.txt'

NEGATION_FRAME_NAME = 'Negation' #CaseSensitive
NEGATED_TAG_NAME = 'Negated' #CaseSensitive
FOCUS_TAG_NAME = 'Focus' #CaseSensitive
SCOPE_TAG_NAME = 'Scope' #CaseSensitive

################
# RULE SETTINGS
################

# POS Tag list for Splitwords
UN_AUS_RULES_POS_TAGS = ['ADJA', 'ADJD', 'NN', 'VVFIN', 'VVPP', 'VVINF']

FOCUS_LEMMA_RULES = ['VMFIN', 'VVFIN', 'VVPP']

# Ruleset for scope starting fenodes
SCOPE_START_FENODE = ['$*LRB*', '$,', 'KON', 'KOUS']

# Ruleset for scope ending fenodes
SCOPE_END_FENODE = ['$.', '$*LRB*']

# Ruleset for lemmas which end scope
SCOPE_END_LEMMA = ['–', 'und']

# Ruleset for scope breaking fenodes
SCOPE_BREAKING_FENODE = ['$,', '$.']

# Ruleset for where the scope should continue
SCOPE_CONTINUE_FENODE = ['KOUS', 'ADV', 'ART', 'KOKOM', 'APPR']

# Focus ruleset for word 'nicht' and pos PTKNEG
NICHT_RULES = ['PIS', 'VVPP', 'ADJD', 'ADV', 'PPER', 'VVINF', 'ADJ', 'ADJA', 'VMFIN', 'PPOSAT']
NICHT_PREV_RULES = ['VAFIN']

# Rulest for word 'nichts'
NICHTS_RULES = ['PIAT', 'PTKANT', 'PIS']

# Where to look for focus for the word 'nichts'
NICHTS_FOCUS_RULES = ['NN', 'PIS', 'PPER']

# Negated ruleset for word 'nicht'
NICHT_NEGATED_RULES = ['VVPP', 'VVIZU', 'VVFIN', 'VMFIN', 'ART']

class NegationDetection:
    """ This is the main module and it is a collection of all
        modules from the project.

        Returns: Results from all modules of this project

        Example: TRAIN = NegationDetection()

    """

    def __init__(self):
        print("Running NegationDetection")

    def extract_cuewords(self, cuewords, xml_file_path):
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

        # Create output files
        if not os.path.exists(CUEWORDS_DATA_PATH):
            self.create_directories(CUEWORDS_DATA_PATH)
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

        if not os.path.exists(xml_file_path):
            self.create_directories(xml_file_path)

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

        return cuewords

    def cueword_statistics(self, xml_file_path):
        """ This function iterates over xml files and writes various statistics
            about the cuewords, scope, focus and negated targets.

            Args:
                xml_file_path (str): Path to input files

            Returns:
                Written txt file for each file in the input path.

            Example:
                >>> cueword_statistics('../res/xml/train/')

        """

        print('Extracting cueword statistics from:', xml_file_path, 'to:', CUEWORDS_STATS_PATH)

        if not os.path.exists(CUEWORDS_STATS_PATH):
            self.create_directories(CUEWORDS_STATS_PATH)

        # Go through all files in xml_file_path directory
        for file in os.listdir(xml_file_path):

            # For each file, open, parseXML
            file = xml_file_path+file

            # Open files only, ignore subdirectories
            if os.path.isfile(file) and file.lower().endswith('.xml'):

                chapter_input = open(file, 'r', encoding='utf8')
                chapter_output = open(CUEWORDS_STATS_PATH+os.path.split(file)[-1]+'_stats.txt',
                                      'w', encoding='utf8')

                # Try html.parser for ignoring lower and UPPER Tag and attr names
                chapter_input = BeautifulSoup(chapter_input, 'xml')

                for sentence in chapter_input.find_all('s'):
                    # Terminals and Semantics
                    #terminals = sentence.find_all('t')
                    semantics = sentence.find('sem')

                    # If splitwords exist
                    if semantics.find('splitwords'):
                        splitwords = semantics.find('splitwords')
                        splitword = splitwords.find_all('splitword')

                        # For each splitword
                        for s_w in splitword:

                            # Get reference id
                            # <splitword idref="x">
                            splitword_idref = s_w.get('idref')

                            # Get corresponding terminal and its POS tag
                            # <t id="x" pos="ADJA" word="unerschütterlichen"/>
                            terminal = sentence.find(id=splitword_idref).get('word')
                            pos = sentence.find(id=splitword_idref).get('pos')

                            #print(splitword_idref,'\t',terminal,'\t',pos)
                            chapter_output.write('\n' '=SPLITWORDS=' '\n')
                            chapter_output.write('%s' '\t' '%s' '\t' '%s' '\n' %
                                                 (splitword_idref, terminal, pos))

                            # Find parts of splitword
                            parts = s_w.find_all('part')
                            part1 = parts[0].get('id')
                            part2 = parts[1].get('id')

                            for part in parts:
                                part_word = part.get('word')
                                part_id = part.get('id')
                                #print(part_id,'\t',part_word)
                                chapter_output.write('%s' '\t' '%s' '\n'
                                                     % (part_id, part_word))

                            # Find corresponding frames
                            frames = semantics.find('frames')
                            frame = frames.find_all('frame')

                            for frame_tag in frame:

                                # skip first letter in case of n|Negation
                                if frame_tag['name'] == NEGATION_FRAME_NAME:

                                    # Find target
                                    target = frame_tag.find('target')
                                    fenode = target.find('fenode')
                                    fenode_id = fenode.get('idref')

                                    # Check part ID if == target ID
                                    if part1 == fenode_id or part2 == fenode_id or splitword_idref == fenode_id:

                                        part_word = sentence.find(id=fenode_id).get('word')
                                        #print(fenode_id,'\t','target')
                                        chapter_output.write('%s' '\t' '%s' '\n'
                                                             % (fenode_id, 'TARGET'))


                                        # try and except blocks because of parser lowerUPPER errors

                                        #Find Negated
                                        try:
                                            negated = frame_tag.find('fe', {'name' : NEGATED_TAG_NAME})
                                            negated_fenode_idref = negated.find('fenode').get('idref')
                                        except AttributeError:
                                            negated = ''
                                            negated_fenode_idref = ''
                                        #print(negated_fenode_idref,'\t',negated['name'].lower())
                                        try:
                                            chapter_output.write('%s' '\t' '%s' '\n'
                                                                 % (negated_fenode_idref, negated['name'].upper()))
                                        except TypeError:
                                            chapter_output.write('')

                                        #Find Scope
                                        try:
                                            scope = frame_tag.find('fe', {'name' : SCOPE_TAG_NAME})
                                            scope_fenode_idref = scope.find('fenode').get('idref')
                                        except AttributeError:
                                            scope = ''
                                            scope_fenode_idref = ''
                                        #print(scope_fenode_idref,'\t',scope['name'].lower())
                                        try:
                                            chapter_output.write('%s' '\t' '%s' '\n'
                                                                 % (scope_fenode_idref, scope['name'].upper()))
                                        except TypeError:
                                            chapter_output.write('')

                                        #Find Focus
                                        try:
                                            focus = frame_tag.find('fe', {'name' : FOCUS_TAG_NAME})
                                            focus_fenode_idref = focus.find('fenode').get('idref')
                                        except AttributeError:
                                            focus = ''
                                            focus_fenode_idref = ''

                                        #print(focus_fenode_idref,'\t',focus['name'].lower())
                                        try:
                                            chapter_output.write('%s' '\t' '%s' '\n'
                                                                 % (focus_fenode_idref, focus['name'].upper()))
                                        except TypeError:
                                            chapter_output.write('')

                    #end if splitwords

                    else:

                        # If Frames exist
                        if semantics.find('frames'):

                            frames = semantics.find('frames')
                            frame = frames.find_all('frame')

                            chapter_output.write('\n' '=SCOPE/FOCUS=' '\n')

                            for frame_tag in frame:

                                # skip first letter in case of n|Negation
                                if frame_tag['name'] == NEGATION_FRAME_NAME:

                                    #scope_list = []

                                    # Find target
                                    target = frame_tag.find('target')
                                    fenode = target.find('fenode')
                                    fenode_id = fenode.get('idref')

                                    word = sentence.find(id=fenode_id).get('word')
                                    pos = sentence.find(id=fenode_id).get('pos')

                                    chapter_output.write('%s' '\t' '%s' '\t' '%s' '\n' % (fenode_id, word, pos))
                                    chapter_output.write('%s' '\t' '%s' '\n' % (fenode_id, 'TARGET'))

                                    #Find Negated
                                    if frame_tag.find('fe', {'name' : NEGATED_TAG_NAME}):
                                        try:
                                            negated = frame_tag.find('fe', {'name' : NEGATED_TAG_NAME})
                                            negated_fenode_idref = negated.find('fenode').get('idref')
                                            negated_word = sentence.find(id=negated_fenode_idref).get('word')
                                            negated_pos = sentence.find(id=negated_fenode_idref).get('pos')
                                        except AttributeError:
                                            negated = ''
                                            negated_fenode_idref = ''
                                            negated_word = ''
                                            negated_pos = ''

                                        chapter_output.write('%s' '\t' '%s' '\t' '%s' '\t' '%s' '\n'
                                                             % (negated_fenode_idref, negated['name'].upper(), negated_word, negated_pos))


                                    # Resolve Terminals if Scope on a complex graph
                                    def resolve_non_terminals(idref):
                                        """ This function resolves a complex graph to
                                            a simple flat list of tokens.
                                        """
                                        nonterminal = sentence.find(id=idref)
                                        edges = nonterminal.find_all('edge')
                                        edge_words = []
                                        for edge in edges:
                                            e_id = edge.get('idref')
                                            if sentence.find(id=e_id).get('word') is not None:
                                                try:
                                                    edge_word = sentence.find(id=e_id).get('word')
                                                    edge_words.append(edge_word)
                                                except:
                                                    pass
                                            if sentence.find(id=e_id).get('word') is None:
                                                edge_words.append(resolve_non_terminals(e_id))

                                        return edge_words

                                    scopelist = []

                                    if frame_tag.find('fe', {'name' : SCOPE_TAG_NAME}):
                                        scope = frame_tag.find('fe', {'name' : SCOPE_TAG_NAME})
                                        scope_fenode = scope.find_all('fenode')
                                        for s_f in scope_fenode:
                                            s_id = s_f.get('idref')
                                            if sentence.find(id=s_id).get('word') is not None:
                                                try:
                                                    scope_word = sentence.find(id=s_id).get('word')
                                                    #scope_pos = scope_word.get('pos')
                                                    scopelist.append(scope_word)
                                                except:
                                                    pass
                                            if sentence.find(id=s_id).get('word') is None:
                                                pass
                                            else:
                                                pass

                                            chapter_output.write('%s' '\t' '%s' '\t' '%s' '\n'
                                                                 % (s_id, scope['name'].upper(), resolve_non_terminals(s_id)))

                                    focuslist = []


                                    #chapter_output.write(str(scope_list))
                                    #Find Focus
                                    if frame_tag.find('fe', {'name' : FOCUS_TAG_NAME}):
                                        focus = frame_tag.find('fe', {'name' : FOCUS_TAG_NAME})
                                        focus_fenode = focus.find_all('fenode')
                                        for f_f in focus_fenode:
                                            f_id = f_f.get('idref')
                                            if sentence.find(id=f_id).get('word') is not None:
                                                try:
                                                    focus_word = sentence.find(id=f_id).get('word')
                                                    focus_pos = sentence.find(id=f_id).get('pos')
                                                    focuslist.append(focus_word)
                                                except:
                                                    pass
                                            if sentence.find(id=f_id).get('word') is None:
                                                pass
                                            else:
                                                pass

                                            chapter_output.write('%s' '\t' '%s' '\t' '%s' '\t' '%s' '\t' '%s' '\n'
                                                                 % (f_id, focus['name'].upper(), focus_pos, focus_word, resolve_non_terminals(f_id)))


                chapter_output.close()

            print('Cuewords statistics extracted to:', chapter_output.name)

    def xml_to_conll(self, xml_file_path):
        """ This function transforms corpus xml files into the CoNLL-2009 format
            which is needed for dependency parsing.

            Args:
                xml (str): Path to corpus files in tiger xml format

            Returns:
                The written files with .conll extension

            Example:
                >>> xml_to_conll('../res/xml/train/')
        """

        if not os.path.exists(CONLL_PATH):
            self.create_directories(CONLL_PATH)


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


    def remove_frames(self, xml_file_path, xml_output_file_path):
        """ This function removes Negation frames from corpus files in Tiger xml format.

            Args:
                xml_file_path (str): Path to corpus files in xml format
                xml_output_file_path (str): Path for output

            Returns:
                The written files without frame annotations

            Example:
                >>> remove_frames('../res/xml/train', '../res/xml/train/output')
        """

        if not os.path.exists(xml_file_path):
            self.create_directories(xml_file_path)

        if not os.path.exists(xml_output_file_path):
            self.create_directories(xml_output_file_path)

        # Go through all files in xml_file_path directory
        for file in os.listdir(xml_file_path):

            # Set path to file
            file = xml_file_path+file

            # Open files only, ignore subdirectories
            if os.path.isfile(file) and file.lower().endswith('.xml'):

                # Open Files
                chapter_input = open(file, 'r', encoding='utf8')

                # Create Same Filename in Output Folder
                chapter_output = open(xml_output_file_path+os.path.split(file)[-1], 'w', encoding='utf8')

                # Console log
                print('Removing Negation frames and splitwords from: ' + chapter_input.name + ' to: ' + chapter_output.name)

                # Parse with BeautifulSoup
                chapter_input = BeautifulSoup(chapter_input, 'xml')

                # Remove splitwords and frames from semantics
                for sem in chapter_input.find_all('sem'):
                    for splitword in sem.find_all('splitwords'):
                        splitword.decompose()

                    for frame in sem.find_all('frames'):
                        for f_r in frame.find_all('frame', {'name' : NEGATION_FRAME_NAME}):
                            f_r.decompose()

                # Write output
                chapter_output.write(chapter_input.prettify())

                # Close file
                chapter_output.close()

        print('Done!')

    def detect_negation(self, xml_file_path, xml_out, cuewords):
        """ This function detects negated sentences and split words
            from a token annotated corpus file in xml format
            and annotates them with negation, scope and focus frames.

            Args:
                xml (str): Path to a corpus file in xml format without frame annotations
                xml_out (str):  Path to an empty file with .xml extension
                cuewords (str): Path to the cuewords file created with the extract_cuewords.py module

            Returns:
                The written file with with frame annotations

            Example:
                >>> detect_negation('../res/xml/train/output',
                '../res/xml/train/output/tagged',
                '../res/cuewords/baskerville_cuewords.txt')
        """

        if not os.path.exists(xml_out):
            self.create_directories(xml_out)

        # Open txt file with cuewords
        cuewords = open(CUEWORDS_DATA_PATH+cuewords, 'r', encoding='utf8')

        # Empty list for collecting
        cueword_list = []

        # Read words from file into list
        for word in cuewords.readlines():
            word = word.strip()
            cueword_list.insert(0, word)

        # Go through all files in xml_file_path directory
        for file in os.listdir(xml_file_path):

            # Set path to file
            file = xml_file_path+file

            # Open files only, ignore subdirectories
            if os.path.isfile(file) and file.lower().endswith('.xml'):

                # Open Files
                chapter_input = open(file, 'r', encoding='utf8')

                # Create Same Filename in Tagged Folder
                chapter_output = open(xml_out+os.path.split(file)[-1], 'w', encoding='utf8')

                # Console log
                print('Writing Negation frames from: ' + chapter_input.name + ' to output file: ' + chapter_output.name)

                # Process xml input file with BeautifulSoup
                chapter_input = BeautifulSoup(chapter_input, 'xml')

                def detect_splitwords():
                    """ This function is a collection of functions for detecting splitwords only,
                        such as: un-erwarterer, außer-ordentlich, zweifel-los etc.
                        It is called from within the main loop and it consists of 5 basic rules.
                    """

                    # SPLITWORD RULES

                    # RULE 1: splitwords starting with 'un'
                    # Exceptions 'un' ADJA: unerwarterer, unglücklichen, unerschütterlichen
                    # Exceptions 'un' ADJD: ungewöhnlicher
                    if t_word[:2] == 'un' and (t_pos in UN_AUS_RULES_POS_TAGS):
                        create_splitword_tags(t_word[:2], t_word[2:])
                        create_negation_frame()
                        create_splitword_target(t_word[:2])
                        create_splitword_focus(t_word[2:])
                        create_splitword_negated(t_word[2:])
                        create_splitword_scope(t_word[2:])

                    # RULE 2: splitwords with 'außerordentlich'
                    if t_word[:15] == 'außerordentlich' and (t_pos in UN_AUS_RULES_POS_TAGS):
                        create_splitword_tags(t_word[:5], t_word[5:])
                        create_negation_frame()
                        create_splitword_target(t_word[:5])
                        create_splitword_focus(t_word[5:])
                        create_splitword_negated(t_word[5:])
                        create_splitword_scope(t_word[5:])

                    # RULE 3: splitwords ending with 'los'
                    # Exceptions: Some Focus Exceptions: 'zweifellos ADJD', 'ratlos ADJD'
                    if t_word[-3:] == 'los':
                        create_splitword_tags(t_word[:-3], t_word[-3:])
                        create_negation_frame()
                        create_splitword_target(t_word[-3:])
                        create_splitword_focus(t_word[:-3])
                        create_splitword_negated(t_word[:-3])
                        create_splitword_scope(t_word[:-3])

                    # RULE 4: splitwords ending with 'lose', or 'frei'
                    if t_word[-4:] == 'lose' or t_word[-4:] == 'frei':
                        create_splitword_tags(t_word[:-4], t_word[-4:])
                        create_negation_frame()
                        create_splitword_target(t_word[-4:])
                        create_splitword_focus(t_word[:-4])
                        create_splitword_negated(t_word[:-4])
                        create_splitword_scope(t_word[:-4])

                    # RULE 5: splitwords ending with 'loser|s|n'
                    if t_word[-5:-1] == 'lose':
                        create_splitword_tags(t_word[:-5], t_word[-5:])
                        create_negation_frame()
                        create_splitword_target(t_word[-5:])
                        create_splitword_focus(t_word[:-5])
                        create_splitword_negated(t_word[:-5])
                        create_splitword_scope(t_word[:-5])

                def guess_splitwords():
                    """ This function tries to guess splitwords starting with un-
                        and having ADJD or ADJA pos tags
                    """

                    if t_word[:2] == 'un' and (t_pos == 'ADJD' or t_pos == 'ADJA'):
                        create_splitword_tags(t_word[:2], t_word[2:])
                        create_negation_frame()
                        create_splitword_target(t_word[:2])
                        create_splitword_focus(t_word[2:])
                        create_splitword_negated(t_word[2:])
                        create_splitword_scope(t_word[2:])


                def detect_cuewords():
                    """ Collection of functions for detecting other cuewords,
                        such as: ni-emals, kein-er, kein, etc.
                        It is called from within the main loop and it consists of multiple rules.
                    """

                    # cuewords

                    if t_word[:2] == 'ni':
                        create_negation_frame()
                        create_target_focus_scope()

                    if t_word[:4] == 'kein':
                        create_negation_frame()
                        create_target_focus_scope()

                    if t_word[:4] == 'nein':
                        create_negation_frame()
                        create_target_focus_scope()


                def guess_cuewords():
                    """ This function tries to guess splitwords starting with
                        ni-
                    """

                    if t_word[:3] == 'nie':
                        create_negation_frame()
                        create_target_focus_scope()

                    if t_word[:3] == 'nic':
                        create_negation_frame()
                        create_target_focus_scope()


                def create_splitword_tags(wordpart_1, wordpart_2):
                    """
                    Function for creating splitword tags.

                    Args:
                        wordpart_1 (str): First part of the splitword
                        wordpart_2 (str): Second part of the splitword

                    Returns:
                        xml tags
                        <splitword idref="TOKEN-ID">
                            <part id="TOKEN-ID_s0" word="wordpart_1"/>
                            <part id="TOKEN-ID_s1" word="wordpart_2"/>
                        </splitword>

                    Example:
                        create_splitword_tags('zweifel','los')
                        or
                        word = "zweifellos"
                        create_splitword_tags(word[:-3], [:-3])
                    """

                    # Create new <splitwords> tag
                    if not sentence.sem.find('splitwords'):
                        splitwords = chapter_input.new_tag('splitwords')
                        sentence.sem.insert(2, splitwords)
                    else:
                        splitwords = sentence.sem.find('splitwords')

                    # Create new <splitword> tag within <splitwords>
                    splitword = chapter_input.new_tag('splitword', idref=t_id)
                    splitwords.append(splitword)

                    # Create sub tags <part> 1
                    part1 = chapter_input.new_tag('part', word=wordpart_1, id=t_id+'_s0')
                    splitword.insert(0, part1)

                    # Create sub tags <part> 2
                    part2 = chapter_input.new_tag('part', word=wordpart_2, id=t_id+'_s1')
                    splitword.insert(1, part2)


                def create_negation_frame():
                    """
                    Function for creating a Negation frame.
                    It looks for a <frames> tag within <sem> and creates a new one if not found.
                    Within it creates a <frame name="Negation"> tag.
                    Each new frame is set on the last index so other functions can find it easily.

                    Returns:
                        xml tag
                        <frame id="SENTENCE-ID_FRAME-ID" name="Negation">
                    """


                    # Create <frames>
                    if not sentence.sem.find('frames'):
                        frames = chapter_input.new_tag('frames')
                        sentence.sem.insert(3, frames)
                    else:
                        frames = sentence.sem.find('frames')

                    frame = chapter_input.new_tag('frame')
                    frame['name'] = NEGATION_FRAME_NAME
                    frames.append(frame)

                    def count_frames():
                        """ Returns the count of all Negation Frames """
                        frames = sentence.sem.frames.find_all('frame', {'name' : NEGATION_FRAME_NAME})
                        frame_count = []
                        for f_r in frames:
                            frame_count.append(f_r)
                        return len(frame_count)

                    frame['id'] = s_id+'_f'+str(count_frames())


                def create_splitword_target(word_part):
                    """
                    Function for creating a splitword target.

                    Args:
                        word_part (str): Target part of the negated slpitword

                    Returns:
                        xml tag
                        <target>
                            <fenode idref="SPLITWORDPART-ID" is_split="yes"/>
                        </target>

                    Example:
                        create_splitword_target('los')
                    """

                    split_word = sentence.sem.find('splitword', {'idref' : t_id})
                    wordpart_idref = split_word.find('part', {'word' : word_part})

                    last_frame = sentence.sem.frames.find_all('frame', {'name' : NEGATION_FRAME_NAME})[-1]

                    # Create <target>
                    target = chapter_input.new_tag('target')
                    last_frame.insert(0, target)

                    # Create target <fenode>
                    target_fenode = chapter_input.new_tag('fenode')
                    target_fenode['idref'] = wordpart_idref.get('id')
                    target_fenode['is_split'] = 'yes'
                    target.insert(0, target_fenode)


                def create_splitword_focus(word_part):
                    """
                    Function for creating a splitword focus.

                    Args:
                        word_part (str): Focus part of the negated splitword

                    Returns:
                        xml tag
                        <fe id="SENTENCE-ID_FE-ID" name="Focus">
                            <fenode idref="SPLITWORDPART-ID" is_split="yes"/>
                        </fe>

                    Example:
                        create_splitword_focus('zweifel')
                    """

                    split_word = sentence.sem.find('splitword', {'idref' : t_id})
                    wordpart_idref = split_word.find('part', {'word' : word_part})

                    last_frame = sentence.sem.frames.find_all('frame', {'name' : NEGATION_FRAME_NAME})[-1]

                    # Create focus
                    focus = chapter_input.new_tag('fe')
                    focus['name'] = FOCUS_TAG_NAME
                    focus['id'] = last_frame.get('id')+'_e1'
                    last_frame.insert(1, focus)

                    # Create focus <fenode>
                    focus_fenode = chapter_input.new_tag('fenode')
                    focus_fenode['idref'] = wordpart_idref.get('id')
                    focus_fenode['is_split'] = 'yes'
                    focus.insert(0, focus_fenode)

                def create_splitword_negated(word_part):
                    """
                    Function for creating the negated part of a splitword.

                    Args:
                        word_part (str): Negated part of the splitword

                    Returns:
                        xml tag
                        <fe id="SENTENCE-ID_FE-ID" name="Negated">
                            <fenode idref="SPLITWORDPART-ID" is_split="yes"/>
                        </fe>

                    Example:
                        create_splitword_negated('zweifel')
                    """

                    split_word = sentence.find('splitword', {'idref' : t_id})
                    wordpart_idref = split_word.find('part', {'word' : word_part})

                    last_frame = sentence.sem.frames.find_all('frame', {'name' : NEGATION_FRAME_NAME})[-1]

                    # Create negated
                    negated = chapter_input.new_tag('fe')
                    negated['name'] = NEGATED_TAG_NAME
                    negated['id'] = last_frame.get('id')+'_e2'
                    last_frame.insert(2, negated)

                    # Create negated <fenode>
                    negated_fenode = chapter_input.new_tag('fenode')
                    negated_fenode['idref'] = wordpart_idref.get('id')
                    negated_fenode['is_split'] = 'yes'
                    negated.insert(0, negated_fenode)

                def create_splitword_scope(word_part):
                    """
                    Function for creating the scope part of a splitword.

                    Args:
                        word_part (str): Scope part of the splitword

                    Returns:
                        xml tag
                        <fe id="SENTENCE-ID_FE-ID" name="Negated">
                            <fenode idref="SPLITWORDPART-ID" is_split="yes"/>
                        </fe>

                    Example:
                        create_splitword_scope('zweifel')
                    """

                    split_word = sentence.find('splitword', {'idref' : t_id})
                    wordpart_idref = split_word.find('part', {'word' : word_part})

                    last_frame = sentence.sem.frames.find_all('frame', {'name' : NEGATION_FRAME_NAME})[-1]

                    # Create scope
                    scope = chapter_input.new_tag('fe')
                    scope['name'] = SCOPE_TAG_NAME
                    scope['id'] = last_frame.get('id')+'_e3'
                    last_frame.insert(3, scope)

                    # Create scope <fenode>
                    scope_fenode = chapter_input.new_tag('fenode')
                    scope_fenode['idref'] = wordpart_idref.get('id')
                    scope_fenode['is_split'] = 'yes'
                    scope.insert(0, scope_fenode)


                def create_target_focus_scope():
                    """
                    Function for creating target focus and scope, for other cuewords.

                    Returns:
                        Full xml frame tag
                        <frame id="SENTENCE-ID_FRAME-ID" name="Negation">
                          <target>
                            <fenode idref="WORD-ID"/>
                          </target>
                          <fe id="67_f1_e1" name="Focus">
                            <fenode idref="WORD-ID"/>
                          </fe>
                          <fe id="67_f1_e1" name="Negated">
                            <fenode idref="WORD-ID"/>
                          </fe>
                          <fe id="67_f1_e3" name="Scope">
                            <fenode idref="WORD-ID"/>
                          </fe>
                       </frame>

                    Example:
                        create_target_focus_scope()
                    """

                    # Create <target>
                    target = chapter_input.new_tag('target')
                    last_frame = sentence.sem.frames.find_all('frame', {'name' : NEGATION_FRAME_NAME})[-1]
                    last_frame.insert(0, target)

                    # Create focus
                    focus = chapter_input.new_tag('fe')
                    focus['name'] = FOCUS_TAG_NAME
                    focus['id'] = last_frame.get('id')+'_e1'
                    last_frame.insert(1, focus)

                    # Create negated
                    negated = chapter_input.new_tag('fe')
                    negated['name'] = NEGATED_TAG_NAME
                    negated['id'] = last_frame.get('id')+'_e2'
                    last_frame.insert(2, negated)

                    # Create scope
                    scope = chapter_input.new_tag('fe')
                    scope['name'] = SCOPE_TAG_NAME
                    scope['id'] = last_frame.get('id')+'_e3'
                    last_frame.append(scope)


                    def create_target_fenode():
                        """
                        Function for creating target fenode
                        """
                        # Create target <fenode>
                        target_fenode = chapter_input.new_tag('fenode')
                        target_fenode['idref'] = t_id
                        target.insert(0, target_fenode)

                    def create_focus_fenode(t_id):
                        """
                        Function for creating target fenode

                        Args:
                            t_id (str): Terminal ID
                        """
                        # Create focus <fenode>
                        focus_fenode = chapter_input.new_tag('fenode')
                        focus_fenode['idref'] = t_id
                        focus.insert(0, focus_fenode)

                    def create_negated_fenode(t_id):
                        """
                        Function for creating negated fenode

                        Args:
                            t_id (str): Terminal ID
                        """
                        # Create focus <fenode>
                        negated_fenode = chapter_input.new_tag('fenode')
                        negated_fenode['idref'] = t_id
                        negated.insert(0, negated_fenode)

                    def create_scope_fenode(t_id):
                        """
                        Function for creating scope fenode

                        Args:
                            t_id (str): Terminal ID
                        """
                        # Create scope <fenode>
                        scope_fenode = chapter_input.new_tag('fenode')
                        scope_fenode['idref'] = t_id
                        scope.append(scope_fenode)


                    # Run Target Function and mark cueword
                    create_target_fenode()

                    # Find previous and next siblings of the cueword within a sentence
                    prev_siblings = sentence.find('t', id=t_id).find_previous_siblings('t')
                    next_siblings = sentence.find('t', id=t_id).find_next_siblings('t')

                    # Mark scope for terminals left of the cueword
                    for p_s in prev_siblings:

                        # Break scope if POS in SCOPE_START_FENODE
                        if p_s.get('pos') in SCOPE_START_FENODE:
                            break

                        # Create scope <fenode>
                        create_scope_fenode(p_s.get('id'))


                    # Mark scope for terminals right of the cueword
                    for n_s in next_siblings:

                        # End Scope if pos in SCOPE_END_FENODE
                        if n_s.get('pos') in SCOPE_END_FENODE or n_s.get('lemma') in SCOPE_END_LEMMA:
                            break

                        # Continue Scope for exceptions
                        if n_s.get('pos') in SCOPE_BREAKING_FENODE[0]:
                            ns_next = n_s.find_next_sibling('t')
                            if ns_next.get('pos') in SCOPE_CONTINUE_FENODE:
                                continue
                            elif ns_next.get('pos') not in SCOPE_CONTINUE_FENODE:
                                break

                        # Create scope <fenode>
                        create_scope_fenode(n_s.get('id'))


                    # Find negated for word nicht right of the cueword
                    for n_s in next_siblings:
                        if t_word == 'nicht':
                            if n_s.get('pos') in NICHT_NEGATED_RULES:
                                create_negated_fenode(n_s.get('id'))
                                break

                    # Find negated for word nicht left of the cueword
                    for p_s in prev_siblings:
                        if t_word == 'nicht':
                            if p_s.get('pos') in NICHT_NEGATED_RULES and not negated.find('fenode'):
                                create_negated_fenode(p_s.get('id'))
                                break

                    # Find focus for terminals right of the cueword
                    for n_s in next_siblings:

                        # RULE 1: nicht PTKNEG
                        if t_word == 'nicht' and t_pos == 'PTKNEG':
                            if n_s.get('pos') in NICHT_RULES and not focus.find('fenode'):
                                create_focus_fenode(n_s.get('id'))
                                break

                        if t_word == 'nein':
                            continue

                        elif n_s.get('pos') in FOCUS_LEMMA_RULES and not focus.find('fenode'):
                            create_focus_fenode(n_s.get('id'))

                        # RULE 2: kein
                        if t_word[:4] == 'kein' and t_pos == 'PIAT':
                            if n_s.get('pos') in NICHT_RULES and not focus.find('fenode'):
                                create_focus_fenode(n_s.get('id'))
                                break

                        elif n_s.get('pos') in FOCUS_LEMMA_RULES and not focus.find('fenode'):
                            create_focus_fenode(n_s.get('id'))

                    # Find focus for 'nichts' right of the cueword
                    for n_s in next_siblings:
                        if t_word == 'nichts' and t_pos in NICHTS_RULES:
                            if n_s.get('pos') in NICHTS_FOCUS_RULES and not focus.find('fenode'):
                                create_focus_fenode(n_s.get('id'))

                    # Find focus and target for terminals left of the cueword
                    for p_s in prev_siblings:

                        # RULE 1: nicht PTKNEG for previous siblings
                        if t_word == 'nicht' and t_pos == 'PTKNEG':
                            if p_s.get('pos') in NICHT_PREV_RULES and not focus.find('fenode'):
                                create_focus_fenode(p_s.get('id'))
                                break

                        elif t_word == 'nicht' and not focus.find('fenode'):
                            create_focus_fenode(t_id)

                        if p_s.get('pos') in FOCUS_LEMMA_RULES:
                            pass

                    if t_word == 'nichts' and t_pos == 'NN':
                        create_focus_fenode(t_id)


                ###########
                # The Loop
                for sentence in chapter_input.find_all('s'):

                    for terminal in sentence.find_all('t'):

                        # collect terminal word in lowercase
                        t_word = terminal.get('word').lower()

                        # collect terminal IDs
                        t_id = terminal.get('id')

                        # Collect terminal POS tags
                        t_pos = terminal.get('pos')

                        # collect sentence IDs
                        s_id = sentence.get('id')

                        if t_word in cueword_list:
                            detect_splitwords()
                            detect_cuewords()

                        elif t_word not in cueword_list:
                            guess_splitwords()
                            guess_cuewords()

                chapter_output.write(chapter_input.prettify())
                print('Done!')
                chapter_output.close()


    def evaluate(self, xml_gold_path, xml_output_path):
        """ This function iterates over Gold standard files and output files created with the detect_negation() module.
            It calculates the average f1 score between all cuewords.

            Args:
                xml_gold_path (str): Path to corpus gold files in xml format with frame annotations
                xml_output_path (str):  Path to corpus files in xml format created with detect_negation() module

            Returns:
                The average f1 score per file

            Example:
                >>> evaluate('../res/xml/train/', '../res/xml/train/output/tagged/')
        """

        # Go through all files in xml_gold_path directory
        for file in os.listdir(xml_gold_path):

            # Set path to file
            file = xml_gold_path+file

            # Open files only, ignore subdirectories
            if os.path.isfile(file) and file.lower().endswith('.xml'):

                # Open xml files
                chapter_input_gold = open(file, 'r', encoding='utf8')
                chapter_input_test = open(xml_output_path+os.path.split(file)[-1], 'r', encoding='utf8')

                # Check if filenams are the same
                chapter_input_gold_name = os.path.split(chapter_input_gold.name)[-1]
                chapter_input_test_name = os.path.split(chapter_input_test.name)[-1]

                if chapter_input_gold_name == chapter_input_test_name:

                    # Console log
                    chapter_input_gold_name = chapter_input_gold.name
                    chapter_input_test_name = chapter_input_test.name
                    #print('Calculating score for: ' + chapter_input_gold_name + ' and: ' + chapter_input_test_name)

                    # Process xml input file with BeautifulSoup
                    chapter_input_gold = BeautifulSoup(chapter_input_gold, 'xml')
                    chapter_input_test = BeautifulSoup(chapter_input_test, 'xml')

                    # Empty variables for collecting Target scores
                    target_precision_scores = 0
                    target_recall_scores = 0
                    target_f1_scores = 0
                    target_jaccard_scores = 0

                    # Empty variables for collecting Focus scores
                    focus_precision_scores = 0
                    focus_recall_scores = 0
                    focus_f1_scores = 0
                    focus_jaccard_scores = 0

                    # Empty variables for collecting Negated scores
                    negated_precision_scores = 0
                    negated_recall_scores = 0
                    negated_f1_scores = 0
                    negated_jaccard_scores = 0

                    # Empty variables for collecting Scope scores
                    scope_precision_scores = 0
                    scope_recall_scores = 0
                    scope_f1_scores = 0
                    scope_jaccard_scores = 0

                    # Count sentences and frames
                    sentence_count = 0
                    gold_frames_count = 0
                    test_frames_count = 0

                    scope_gold_frames_count = 0
                    #scope_test_frames_count = 0

                    # Find all Gold and Test Sentences
                    sentences_gold = chapter_input_gold.find_all('s')
                    sentences_test = chapter_input_test.find_all('s')

                    #targets_gold = chapter_input_gold.find_all('target')
                    #targets_test = chapter_input_test.find_all('target')

                    scope_gold_frames = chapter_input_gold.find_all('fe', {'name' : SCOPE_TAG_NAME})
                    scope_gold_frames_count = len(scope_gold_frames)

                    scope_test_frames = chapter_input_test.find_all('fe', {'name' : SCOPE_TAG_NAME})
                    scope_test_frames_count = len(scope_test_frames)

                    # Exit if number of sentences != between Gold and Test files
                    if len(sentences_gold) != len(sentences_test):
                        raise SystemExit(print('Number of sentences between Gold and Test files does not match.\nGold:',
                                               len(sentences_gold), 'Test:', len(sentences_test)))

                    # Zip Gold and Test Sentences
                    for s_gold, s_test in zip(sentences_gold, sentences_test):

                        sentence_count = sentence_count + 1

                        gold_frames = s_gold.find_all('frame', {'name' : NEGATION_FRAME_NAME})
                        test_frames = s_test.find_all('frame', {'name' : NEGATION_FRAME_NAME})

                        gold_frames_count = gold_frames_count + len(gold_frames)
                        test_frames_count = test_frames_count + len(test_frames)

                        for item in zip(gold_frames, test_frames):

                            #print('\n=========')
                            #print('\nFrame:', item[0].get('id'))

                            target_gold_list = []
                            target_test_list = []

                            focus_gold_list = []
                            focus_test_list = []

                            negated_gold_list = []
                            negated_test_list = []

                            scope_gold_list = []
                            scope_test_list = []

                            # Flatten a nested list of fenodes
                            def flatten(nested_list):
                                """ Flatten a nested list of fenodes """
                                t_l = []
                                for i in nested_list:
                                    if not isinstance(i, list):
                                        t_l.append(i)
                                    else:
                                        t_l.extend(flatten(i))
                                return t_l

                            # Target
                            if item[0].find('target'):
                                target_gold = item[0].find('target')
                                target_gold_fenode_id = target_gold.find('fenode').get('idref')
                                target_gold_word = s_gold.find(id=target_gold_fenode_id).get('word').lower()

                                try:
                                    target_test = item[1].find('target')
                                    target_test_fenode__id = target_test.find('fenode').get('idref')
                                    target_test_word = s_test.find(id=target_test_fenode__id).get('word').lower()
                                except:
                                    target_test_word = ''

                            elif item[1].find('target'):
                                target_test = item[1].find('target')
                                target_test_fenode__id = target_test.find('fenode').get('idref')
                                target_test_word = s_test.find(id=target_test_fenode__id).get('word').lower()

                                try:
                                    target_gold = item[0].find('target')
                                    target_gold_fenode_id = target_gold.find('fenode').get('idref')
                                    target_gold_word = s_gold.find(id=target_gold_fenode_id).get('word').lower()
                                except:
                                    target_gold_word = ''

                            target_gold_list.append(target_gold_word)
                            target_test_list.append(target_test_word)

                            # Sort lists
                            sorted_target_gold_list = sorted(flatten(target_gold_list))
                            sorted_target_test_list = sorted(flatten(target_test_list))

                            #print('\nTarget [Gold]:', sorted_target_gold_list)
                            #print('Target [Test]:', sorted_target_test_list)


                            # Focus
                            if item[0].find('fe', {'name' : FOCUS_TAG_NAME}):
                                focus_gold = item[0].find('fe', {'name' : FOCUS_TAG_NAME})
                                try:
                                    focus_gold_fenode_id = focus_gold.find('fenode').get('idref')
                                    focus_gold_word = s_gold.find(id=focus_gold_fenode_id).get('word').lower()
                                except:
                                    focus_gold_word = ''
                                if item[1].find('fe', {'name' : FOCUS_TAG_NAME}):
                                    focus_test = item[1].find('fe', {'name' : FOCUS_TAG_NAME})
                                    try:
                                        focus_test_fenode_id = focus_test.find('fenode').get('idref')
                                        focus_test_word = s_test.find(id=focus_test_fenode_id).get('word').lower()
                                    except:
                                        focus_test_word = ''
                                else:
                                    focus_test_word = ''

                            elif item[1].find('fe', {'name' : FOCUS_TAG_NAME}):
                                focus_test = item[1].find('fe', {'name' : FOCUS_TAG_NAME})
                                try:
                                    focus_test_fenode_id = focus_test.find('fenode').get('idref')
                                    focus_test_word = s_test.find(id=focus_test_fenode_id).get('word').lower()
                                except:
                                    focus_test_word = ''
                                if item[0].find('fe', {'name' : FOCUS_TAG_NAME}):
                                    focus_gold = item[0].find('fe', {'name' : FOCUS_TAG_NAME})
                                    focus_gold_fenode_id = focus_gold.find('fenode').get('idref')
                                    try:
                                        focus_gold_word = s_gold.find(id=focus_gold_fenode_id).get('word').lower()
                                    except AttributeError:
                                        focus_gold_word = ''
                                else:
                                    focus_gold_word = ''

                            focus_gold_list.append(focus_gold_word)
                            focus_test_list.append(focus_test_word)

                            # Sort lists
                            sorted_focus_gold_list = sorted(flatten(focus_gold_list))
                            sorted_focus_test_list = sorted(flatten(focus_test_list))

                            #print('\nFocus [Gold]:', sorted_focus_gold_list)
                            #print('Focus [Test]:', sorted_focus_test_list)


                            # Negated
                            if item[0].find('fe', {'name' : NEGATED_TAG_NAME}):
                                negated_gold = item[0].find('fe', {'name' : NEGATED_TAG_NAME})
                                negated_gold_fenode_id = negated_gold.find('fenode').get('idref')
                                try:
                                    negated_gold_word = s_gold.find(id=negated_gold_fenode_id).get('word').lower()
                                except AttributeError:
                                    negated_gold_word = ''
                                if item[1].find('fe', {'name' : NEGATED_TAG_NAME}):
                                    negated_test = item[1].find('fe', {'name' : NEGATED_TAG_NAME})
                                    try:
                                        negated_test_fenode_id = negated_test.find('fenode').get('idref')
                                        negated_test_word = s_test.find(id=negated_test_fenode_id).get('word').lower()
                                    except:
                                        negated_test_word = ''
                                else:
                                    negated_test_word = ''

                            elif item[1].find('fe', {'name' : NEGATED_TAG_NAME}):
                                negated_test = item[1].find('fe', {'name' : NEGATED_TAG_NAME})
                                try:
                                    negated_test_fenode_id = negated_test.find('fenode').get('idref')
                                    negated_test_word = s_test.find(id=negated_test_fenode_id).get('word').lower()
                                except:
                                    negated_test_word = ''
                                if item[0].find('fe', {'name' : NEGATED_TAG_NAME}):
                                    negated_gold = item[0].find('fe', {'name' : NEGATED_TAG_NAME})
                                    negated_gold_fenode_id = negated_gold.find('fenode').get('idref')
                                    try:
                                        negated_gold_word = s_gold.find(id=negated_gold_fenode_id).get('word').lower()
                                    except AttributeError:
                                        negated_gold_word = ''
                                else:
                                    negated_gold_word = ''
                            else:
                                negated_test_word = ''
                                negated_gold_word = ''

                            negated_gold_list.append(negated_gold_word)
                            negated_test_list.append(negated_test_word)

                            # Sort lists
                            sorted_negated_gold_list = sorted(flatten(negated_gold_list))
                            sorted_negated_test_list = sorted(flatten(negated_test_list))

                            #print('\nNegated [Gold]:', sorted_negated_gold_list)
                            #print('Negated [Test]:', sorted_negated_test_list)


                            # Resolve Terminals if Scope on a complex graph
                            def resolve_non_terminals(idref):
                                """ This function resolves a complex gold graph to
                                    a simple flat list of tokens.
                                """
                                nonterminal = s_gold.find(id=idref)
                                edges = nonterminal.find_all('edge')
                                edge_words = []
                                for edge in edges:
                                    e_id = edge.get('idref')
                                    if s_gold.find(id=e_id).get('word') is not None:
                                        try:
                                            edge_word = s_gold.find(id=e_id).get('word')
                                            edge_words.append(edge_word)
                                        except:
                                            pass
                                    if s_gold.find(id=e_id).get('word') is None:
                                        edge_words.append(resolve_non_terminals(e_id))

                                return edge_words

                            def resolve_non_terminals_test(idref):
                                """ This function resolves a complex test graph to
                                    a simple flat list of tokens.
                                """
                                nonterminal = s_test.find(id=idref)
                                edges = nonterminal.find_all('edge')
                                edge_words = []
                                for edge in edges:
                                    e_id = edge.get('idref')
                                    if s_test.find(id=e_id).get('word') is not None:
                                        try:
                                            edge_word = s_test.find(id=e_id).get('word')
                                            edge_words.append(edge_word)
                                        except:
                                            pass
                                    if s_test.find(id=e_id).get('word') is None:
                                        edge_words.append(resolve_non_terminals(e_id))

                                return edge_words

                            # Scope
                            if item[0].find('fe', {'name' : SCOPE_TAG_NAME}):
                                scope_gold = item[0].find('fe', {'name' : SCOPE_TAG_NAME})
                                scope_gold_fenodes = scope_gold.find_all('fenode')
                                for s_g in scope_gold_fenodes:
                                    s_id = s_g.get('idref')
                                    if s_gold.find(id=s_id).get('word') is not None:
                                        try:
                                            scope_word = s_gold.find(id=s_id).get('word')
                                            scope_gold_list.append(scope_word)
                                        except:
                                            pass
                                    if s_gold.find(id=s_id).get('word') is None:
                                        scope_gold_list.append(resolve_non_terminals(s_id))
                                    else:
                                        pass

                                if item[1].find('fe', {'name' : SCOPE_TAG_NAME}):
                                    scope_test = item[1].find('fe', {'name' : SCOPE_TAG_NAME})
                                    scope_test_fenodes = scope_test.find_all('fenode')
                                    for s_t in scope_test_fenodes:
                                        s_id = s_t.get('idref')
                                        if s_test.find(id=s_id).get('word') is not None:
                                            try:
                                                scope_word = s_test.find(id=s_id).get('word')
                                                scope_test_list.append(scope_word)
                                            except:
                                                pass
                                        elif s_test.find(id=s_id).get('word') is None:
                                            scope_test_list.append(resolve_non_terminals_test(s_id))
                                else:
                                    scope_test_list.append('')

                            elif item[1].find('fe', {'name' : SCOPE_TAG_NAME}):
                                scope_test = item[1].find('fe', {'name' : SCOPE_TAG_NAME})
                                scope_test_fenodes = scope_test.find_all('fenode')
                                for s_t in scope_test_fenodes:
                                    s_id = s_t.get('idref')
                                    if s_test.find(id=s_id).get('word') is not None:
                                        try:
                                            scope_word = s_test.find(id=s_id).get('word')
                                            scope_test_list.append(scope_word)
                                        except:
                                            pass
                                    if s_test.find(id=s_id).get('word') is None:
                                        scope_test_list.append(resolve_non_terminals_test(s_id))
                                    else:
                                        pass

                                if item[0].find('fe', {'name' : SCOPE_TAG_NAME}):
                                    scope_gold = item[1].find('fe', {'name' : SCOPE_TAG_NAME})
                                    scope_gold_fenodes = scope_gold.find_all('fenode')
                                    for s_g in scope_gold_fenodes:
                                        s_id = s_g.get('idref')
                                        if s_gold.find(id=s_id).get('word') is not None:
                                            try:
                                                scope_word = s_gold.find(id=s_id).get('word')
                                                scope_gold_list.append(scope_word)
                                            except:
                                                pass
                                        if s_gold.find(id=s_id).get('word') is None:
                                            scope_gold_list.append(resolve_non_terminals(s_id))
                                        else:
                                            pass
                                else:
                                    scope_gold_list.append('')

                            # Sort lists
                            sorted_scope_gold_list = sorted(flatten(scope_gold_list))
                            sorted_scope_test_list = sorted(flatten(scope_test_list))

                            #print('\nScope [Gold]:', sorted_scope_gold_list)
                            #print('Scope [Test]:', sorted_scope_test_list)


                            # If lists are same length, ok
                            if len(sorted_scope_gold_list) == len(sorted_scope_test_list):
                                pass

                            # If lists are different lengths, add empty elements
                            if len(sorted_scope_gold_list) > len(sorted_scope_test_list):
                                difference = len(sorted_scope_gold_list) - len(sorted_scope_test_list)
                                empty_element = 0

                                while empty_element < difference:
                                    sorted_scope_test_list.append('')
                                    empty_element = empty_element + 1

                            elif len(sorted_scope_test_list) > len(sorted_scope_gold_list):
                                difference = len(sorted_scope_test_list) - len(sorted_scope_gold_list)
                                empty_element = 0

                                while empty_element < difference:
                                    sorted_scope_gold_list.append('')
                                    empty_element = empty_element + 1


                            # Align items in the lists for sklearn, set 1 for matched items, else set 0
                            sorted_target_gold_list_normalized = [1 for element in sorted_target_gold_list]
                            sorted_target_test_list_normalized = [1 if element in sorted_target_gold_list else 0 for element in sorted_target_test_list]

                            sorted_focus_gold_list_normalized = [1 for element in sorted_focus_gold_list]
                            sorted_focus_test_list_normalized = [1 if element in sorted_focus_gold_list else 0 for element in sorted_focus_test_list]

                            sorted_negated_gold_list_normalized = [1 for element in sorted_negated_gold_list]
                            sorted_negated_test_list_normalized = [1 if element in sorted_negated_gold_list else 0 for element in sorted_negated_test_list]

                            sorted_scope_gold_list_normalized = [1 for element in sorted_scope_gold_list]
                            sorted_scope_test_list_normalized = [1 if element in sorted_scope_gold_list else 0 for element in sorted_scope_test_list]


                            # Sklearn calculations
                            #target_precision_scores = target_precision_scores + precision_score(sorted_target_gold_list_normalized, sorted_target_test_list_normalized, average='weighted')
                            #target_recall_scores = target_recall_scores + recall_score(sorted_target_gold_list_normalized, sorted_target_test_list_normalized, average='weighted')
                            target_f1_scores =  target_f1_scores + f1_score(sorted_target_gold_list_normalized, sorted_target_test_list_normalized, average='weighted')
                            #target_jaccard_scores = target_jaccard_scores + jaccard_similarity_score(sorted_target_gold_list, sorted_target_test_list)

                            #focus_precision_scores = focus_precision_scores + precision_score(sorted_focus_gold_list_normalized, sorted_focus_test_list_normalized, average='weighted')
                            #focus_recall_scores = focus_recall_scores + recall_score(sorted_focus_gold_list_normalized, sorted_focus_test_list_normalized, average='weighted')
                            focus_f1_scores =  focus_f1_scores + f1_score(sorted_focus_gold_list_normalized, sorted_focus_test_list_normalized, average='weighted')
                            #focus_jaccard_scores = focus_jaccard_scores + jaccard_similarity_score(sorted_focus_gold_list, sorted_focus_test_list)

                            #negated_precision_scores = negated_precision_scores + precision_score(sorted_negated_gold_list_normalized, sorted_negated_test_list_normalized, average='weighted')
                            #negated_recall_scores = negated_recall_scores + recall_score(sorted_negated_gold_list_normalized, sorted_negated_test_list_normalized, average='weighted')
                            negated_f1_scores =  negated_f1_scores + f1_score(sorted_negated_gold_list_normalized, sorted_negated_test_list_normalized, average='weighted')
                            #negated_jaccard_scores = negated_jaccard_scores + jaccard_similarity_score(sorted_negated_gold_list, sorted_negated_test_list)

                            scope_precision_scores = scope_precision_scores + precision_score(sorted_scope_gold_list_normalized, sorted_scope_test_list_normalized, average='weighted')
                            scope_recall_scores = scope_recall_scores + recall_score(sorted_scope_gold_list_normalized, sorted_scope_test_list_normalized, average='weighted')
                            scope_f1_scores =  scope_f1_scores + f1_score(sorted_scope_gold_list_normalized, sorted_scope_test_list_normalized, average='weighted')
                            scope_jaccard_scores = scope_jaccard_scores + jaccard_similarity_score(sorted_scope_gold_list, sorted_scope_test_list)


                    print('\n=============================')
                    print('====== EVALUATION for:', chapter_input_test_name, '======')
                    print('Total Sentences:', sentence_count,
                          '\nGold frames:', gold_frames_count,
                          '\nTest frames:', test_frames_count, '\n')

                    print('----- CUEWORDS -----')
                    #print('Precision:\t', target_precision_scores / gold_frames_count)
                    #print('Recall:\t', target_recall_scores / gold_frames_count)
                    print('F1 score:\t', target_f1_scores / gold_frames_count)
                    #print('Jaccard similarity:\t', target_jaccard_scores / gold_frames_count)

                    print('\n----- FOCUS -----')
                    #print('Precision:\t', focus_precision_scores / gold_frames_count)
                    #print('Recall:\t', focus_recall_scores / gold_frames_count)
                    print('F1 score:\t', focus_f1_scores / gold_frames_count)
                    #print('Jaccard similarity:\t', focus_jaccard_scores / gold_frames_count)

                    print('\n----- NEGATED -----')
                    #print('Precision:\t', negated_precision_scores / gold_frames_count)
                    #print('Recall:\t', negated_recall_scores / gold_frames_count)
                    print('F1 score:\t', negated_f1_scores / gold_frames_count)
                    #print('Jaccard similarity:\t', negated_jaccard_scores / gold_frames_count)

                    print('\n----- SCOPE -----')
                    print('Precision:\t', scope_precision_scores / scope_gold_frames_count)
                    print('Recall:\t', scope_recall_scores / scope_gold_frames_count)
                    print('F1 score:\t', scope_f1_scores / scope_gold_frames_count)
                    print('Jaccard similarity:\t', scope_jaccard_scores / scope_gold_frames_count)

        print('Done!')

    def create_directories(self, path):
        """ This function creates missing directories that are needed for the output files

            Example: create_directories(../res/xml/train/output/tagged)

            Returns: created directories
        """
        os.makedirs(path)
        print('Directory created at:', path)
        return path


if __name__ == "__main__":

    TRAIN = NegationDetection()
    TRAIN.extract_cuewords(CUEWORDS_FILE, XML_TRAIN_FILES_PATH)
    TRAIN.cueword_statistics(XML_TRAIN_FILES_PATH)
    TRAIN.xml_to_conll(XML_TRAIN_FILES_PATH)
    TRAIN.remove_frames(XML_TRAIN_FILES_PATH, XML_TRAIN_FILES_OUTPUT_PATH)
    TRAIN.detect_negation(XML_TRAIN_FILES_OUTPUT_PATH, XML_TRAIN_FILES_TAGGED_PATH, CUEWORDS_FILE)
    TRAIN.evaluate(XML_TRAIN_FILES_PATH, XML_TRAIN_FILES_TAGGED_PATH)

    TEST = NegationDetection()
    TEST.remove_frames(XML_TEST_FILES_PATH, XML_TEST_FILES_OUTPUT_PATH)
    TEST.detect_negation(XML_TEST_FILES_OUTPUT_PATH, XML_TEST_FILES_TAGGED_PATH, CUEWORDS_FILE)
    TEST.evaluate(XML_TEST_FILES_PATH, XML_TEST_FILES_TAGGED_PATH)

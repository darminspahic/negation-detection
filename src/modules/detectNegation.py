#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Author: Darmin Spahic <Spahic@stud.uni-heidelberg.de>
Project: Negation Detection

Module name:
detect_negation

Short description:
This is the main module and it detects negated sentences and
split words from a token annotated corpus file in xml format
and annotates them with negation, scope and focus frames.

License: MIT License
Version: 1.0

"""

import codecs
import os
import sys

from bs4 import BeautifulSoup
import lxml

################
# PATH SETTINGS
################

XML_TRAIN_FILES_PATH = '../../res/xml/train/'
XML_TEST_FILES_PATH = '../../res/xml/test/'

XML_TRAIN_FILES_OUTPUT_PATH = '../../res/xml/train/output/'
XML_TEST_FILES_OUTPUT_PATH = '../../res/xml/test/output/'

XML_TRAIN_FILES_TAGGED_PATH = '../../res/xml/train/output/tagged/'
XML_TEST_FILES_TAGGED_PATH = '../../res/xml/test/output/tagged/'

CUEWORDS_DATA_PATH = '../../res/cuewords/'
CUEWORDS_STATS_PATH = '../../res/cuewords/stats/'

CUEWORDS_FILE = 'baskerville_cuewords.txt'
CUEWORDS_FILE_POS_TAGGED = 'baskerville_cuewords_postagged.txt'

CONLL_PATH = '../../res/conll/'

TRAIN_RESULTS_FILE = '../../results/results-train.txt'
TEST_RESULTS_FILE = '../../results/results-test.txt'

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

def detect_negation(xml_file_path, xml_out, cuewords):
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
            >>> detect_negation('../../res/xml/train/output',
            '../../res/xml/train/output/tagged',
            '../../res/cuewords/baskerville_cuewords.txt')
    """

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


if __name__ == "__main__":
    detect_negation(XML_TRAIN_FILES_OUTPUT_PATH, XML_TRAIN_FILES_TAGGED_PATH, CUEWORDS_FILE)

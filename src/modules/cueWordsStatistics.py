#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Author: Darmin Spahic <Spahic@stud.uni-heidelberg.de>
Project: Negation Detection

Module name:
cueword_statistics

Short description:
This module writes various statistics
about the cuewords, scope, focus and negated targets.

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

CONLL_PATH = '../../res/conll/'

NEGATION_FRAME_NAME = 'Negation' #CaseSensitive
NEGATED_TAG_NAME = 'Negated' #CaseSensitive
FOCUS_TAG_NAME = 'Focus' #CaseSensitive
SCOPE_TAG_NAME = 'Scope' #CaseSensitive

def cueword_statistics(xml_file_path):
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

if __name__ == "__main__":
    cueword_statistics(XML_TRAIN_FILES_PATH)
    

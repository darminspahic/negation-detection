#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Author: Darmin Spahic <Spahic@stud.uni-heidelberg.de>
Project: Negation Detection

Module name:
evaluate

Short description:
This function iterates over Gold standard files
and output files created with the detect_negation module.
It calculates the average f1 score between all cuewords.

License: MIT License
Version: 1.0

"""

# import dependencies
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

XML_TRAIN_FILES_PATH = '../../res/xml/train/'
XML_TEST_FILES_PATH = '../../res/xml/test/'

XML_TRAIN_FILES_OUTPUT_PATH = '../../res/xml/train/output/'
XML_TEST_FILES_OUTPUT_PATH = '../../res/xml/test/output/'

XML_TRAIN_FILES_TAGGED_PATH = '../../res/xml/train/output/tagged/'
XML_TEST_FILES_TAGGED_PATH = '../../res/xml/test/output/tagged/'

NEGATION_FRAME_NAME = 'Negation' #CaseSensitive
NEGATED_TAG_NAME = 'Negated' #CaseSensitive
FOCUS_TAG_NAME = 'Focus' #CaseSensitive
SCOPE_TAG_NAME = 'Scope' #CaseSensitive

def evaluate(xml_gold_path, xml_output_path):
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
                                        edge_word = s_gold.find(id=e_id).get('word').lower()
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
                                        edge_word = s_test.find(id=e_id).get('word').lower()
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
                                        scope_word = s_gold.find(id=s_id).get('word').lower()
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
                                            scope_word = s_test.find(id=s_id).get('word').lower()
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
                                        scope_word = s_test.find(id=s_id).get('word').lower()
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
                                            scope_word = s_gold.find(id=s_id).get('word').lower()
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


                        # If lists are same length, check if items are same
                        if len(sorted_scope_gold_list) == len(sorted_scope_test_list):
                            sorted_scope_test_list_intersection = set(sorted_scope_gold_list).intersection(sorted_scope_test_list)
                            sorted_scope_test_list_intersection = list(sorted_scope_test_list_intersection)
                            if len(sorted_scope_test_list_intersection) < len(sorted_scope_test_list):
                                difference = len(sorted_scope_test_list) - len(sorted_scope_test_list_intersection)
                                empty_element = 0

                                while empty_element < difference:
                                    sorted_scope_test_list_intersection.append('')
                                    empty_element = empty_element + 1
                                    
                                sorted_scope_test_list = sorted_scope_test_list_intersection

                        # If lists are different lengths, add empty elements
                        elif len(sorted_scope_gold_list) > len(sorted_scope_test_list):
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
                        sorted_target_gold_list_normalized = [1 if element in sorted_target_gold_list and not element == "" else 0 for element in sorted_target_gold_list]
                        sorted_target_test_list_normalized = [1 if element in sorted_target_gold_list else 0 for element in sorted_target_test_list]

                        sorted_focus_gold_list_normalized = [1 if element in sorted_focus_gold_list and not element == "" else 0 for element in sorted_focus_gold_list]
                        sorted_focus_test_list_normalized = [1 if element in sorted_focus_gold_list else 0 for element in sorted_focus_test_list]

                        sorted_negated_gold_list_normalized = [1 if element in sorted_negated_gold_list and not element == "" else 0 for element in sorted_negated_gold_list]
                        sorted_negated_test_list_normalized = [1 if element in sorted_negated_gold_list else 0 for element in sorted_negated_test_list]

                        sorted_scope_gold_list_normalized = [1 if element in sorted_scope_gold_list and not element == "" else 0 for element in sorted_scope_gold_list]
                        sorted_scope_test_list_normalized = [1 if element in sorted_scope_gold_list else 1 if not element == "" else 0 for element in sorted_scope_test_list]

                        #print(sorted_scope_gold_list_normalized)
                        #print(sorted_scope_test_list_normalized)


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
                      '\nNegation Gold frames:', gold_frames_count,
                      '\nNegation Test frames:', test_frames_count, '\n')

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

                print('\n----- SCOPE -----\nScope Gold frames:', scope_gold_frames_count, '\nScope Test frames:', scope_test_frames_count, '\n')
                print('Precision:\t', scope_precision_scores / scope_test_frames_count)
                print('Recall:\t', scope_recall_scores / scope_test_frames_count)
                print('F1 score:\t', scope_f1_scores / scope_test_frames_count)
                print('Jaccard similarity:\t', scope_jaccard_scores / scope_test_frames_count)

    print('Done!')



if __name__ == "__main__":
    evaluate(XML_TRAIN_FILES_PATH, XML_TRAIN_FILES_TAGGED_PATH)


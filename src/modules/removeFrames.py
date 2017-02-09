#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Author: Darmin Spahic <Spahic@stud.uni-heidelberg.de>
Project: Negation Detection

Module name:
remove_frames

Short description:
This module removes Negation frames from corpus files in xml format.

License: MIT License
Version: 1.0

"""

# import dependencies
import os, sys
import codecs
from bs4 import BeautifulSoup
import lxml

XML_TRAIN_FILES_PATH = '../../res/xml/train/'
XML_TRAIN_FILES_OUTPUT_PATH = '../../res/xml/train/output/'

NEGATION_FRAME_NAME = 'Negation' #CaseSensitive

def remove_frames(xml_file_path, xml_output_file_path):
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

if __name__ == "__main__":

    remove_frames(XML_TRAIN_FILES_PATH, XML_TRAIN_FILES_OUTPUT_PATH)

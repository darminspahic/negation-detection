# Negation Detection

This program detects negated sentences from xml annotated corpora in TIGER-XML format and
annotates them with Negation frames, Scope, Focus and Target tags.


## Installation
Install dependencies with pip:
- $ pip install -r src/requirements.txt

Or install the requirements separately:
- Python >= 3.5.2 [Download] (https://www.python.org/downloads/)
- Java >= 1.8.0_111 [Download] (https://java.com/en/download/)
- Beautiful Soup >= 4.5.1 [Download](https://www.crummy.com/software/BeautifulSoup/#Download), [Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
  - $ apt-get install python-bs4
  - $ easy_install beautifulsoup4
  - $ pip install beautifulsoup4
- LXML [Docs] (http://lxml.de/)
  - $ pip install lxml
- Scikit Learn Module: sklearn.metrics [Download](http://scikit-learn.org/), [Docs](http://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics)
  - $ pip install -U scikit-learn
  
- \(Optional) Install the SALTO Annotation Tool in order to view annotated xml files [Web] (http://www.coli.uni-saarland.de/projects/salsa/page.php?id=software)

Clone the repository:
```bash
$ git clone https://gitlab.cl.uni-heidelberg.de/negation-detection/ws16.git
```

Optional:
- Install mate-tools [Web](http://www.ims.uni-stuttgart.de/forschung/ressourcen/werkzeuge/matetools.en.html), [Download](https://code.google.com/archive/p/mate-tools/downloads), [Wiki](https://code.google.com/archive/p/mate-tools/wikis)


## Program structure
The main program can either be run with the main wrapper class:
- Main module > src/main.py

Or separately as modules:
- Xml to CoNLL-2009 parser > src/modules/xmlToConll.py
- Dependency parser
- Cue word extraction > src/modules/extractCueWords.py
- Frame removal > src/modules/removeFrames.py
- Rulesets extractor > src/modules/cueWordsStatistics.py
- Detect negated sentences > src/modules/detectNegation.py
- Evaluation > src/modules/evaluation.py


## Main example
Split the train and test data to res/xml/train/ and res/xml/test/ accordingly. 
When resplitting the files for new tests, be sure to remove the output folders res/xml/train/output/ and res/xml/test/output/ To run the module main.py cd into:
```bash
$ cd src/
```
and run
```bash
$ python main.py
```
The output files will be written to: res/xml/train/output/tagged/ and res/xml/test/output/tagged/
Open the files from the output folder with the SALTO Annotation Tool in order to view the results.


## Modules
The following section shows examples on how to run various modules.


### Xml to CoNLL-2009 parser
To parse annotated xml files in res/xml/train/ into CoNLL-2009 format, cd into:
```bash
$ cd src/modules/
```
and run
```bash
$ python xmlToConll.py
```
The output will be written to: res/conll/


### Dependency parser
Our program uses [mate-tools](https://code.google.com/archive/p/mate-tools/) to parse sentences and annotate them with dependencies. 
This is an important step for the manual rule creation of negation targets.
To annotate the previous output with dependencies and write [CoNLL-2009] (http://ufal.mff.cuni.cz/conll2009-st/task-description.html) 
files, download the [mate-tools parser and German language model](https://code.google.com/archive/p/mate-tools/wikis/ParserAndModels.wiki) to parser/ and cd into
```bash
$ cd parser/
```
and run
```bash
$ java -Xmx3G -classpath anna-3.61.jar is2.parser.Parser -model parser-ger-3.6.model -test <input_file> -out <output_file>
```
where \<input_file\> can be any file that has already been tagged and lemmatized. For example:
```bash
$ java -Xmx3G -classpath anna-3.61.jar is2.parser.Parser -model parser-ger-3.6.model -test ../res/conll/baskerville_ch4.jr.conll -out ../res/conll/baskerville_ch4.jr.dep.conll
```
This step can be skipped, since all the rules are already extracted.


### Cue word extraction
To extract cue words from annotated xml files in res/xml/train/ cd into:
```bash
$ cd src/modules/
```
and run:
```bash
$ python extractCueWords.py
```
Two files with cue words from all documents within the res/xml/train/ folder will be written. 
One file will be written to res/cuewords/baskerville_cuewords.txt alphabetically sorted and without duplicates, 
and the other to res/cuewords/baskerville_cuewords_postagged.txt alphabetically sorted, POS tagged and also without duplicates.


### Frame removal
To remove frames from annotated data in res/xml/train/ in order to prepare the files for final testing, cd into:
```bash
$ cd src/modules/
```
and run
```bash
$ python removeFrames.py
```
Files without frame annotations will be written to res/xml/train/output/


### Rulesets extraction
To extract rulesets from res/xml/test/ and write a txt file with various cueword statistics, cd into:
```bash
$ cd src/modules/
```
and run
```bash
$ python cueWordsStatistics.py
```
Files with cue word statistics will be written to res/cuewords/stats/


### Scope, Focus, Target detection
To detect negated sentences based on cue words from res/xml/test/ and write xml files with frame annotations, cd into:
```bash
$ cd src/modules/
```
and run
```bash
$ python detectNegation.py
```
Files with negated splitwords and sentences, annotated with frame annotations \(focus, scope, negated) will be written to res/xml/train/output/
Open the file with Salto in order to view the annotations.


### Evaluation
To evaluate the results, cd into:
```bash
$ cd src/modules/
```
and run
```bash
$ python evaluation.py
```
The standard output is written to the console. Use python evaluation.py > outputfile.txt to output the results to a txt file.


## Contributors
[Darmin Spahic](https://github.com/darminspahic), Robert Sass

## References
Ballesteros, Díaz, Francisco, Gervás, Carrillo de Albornoz, Plaza. UCM-2: a Rule-Based Approach to Infer the Scope of Negation via Dependency Parsing.


## License
MIT License

Copyright (c) 2016-2017 negation-detection

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

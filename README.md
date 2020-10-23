# KANJIVG DATASET

Dataset for training models in teaching robots to draw
## Important Points !

1. characters are now used from kanjivg collection of japanese characters

2. original characters are defined using bezeir curves, this dataset modifies the characters svg files by converting bezeri curves into line segments which are easier to handle

3. few characters are removed because of in-compaitability reasons, will be restored in future commits

### scripts and their functions

1.**bresenhamsalgo.py** --> this module has implementation for segmenting a given strait line

2.**drawing_utils.py** --> simple python module with most used functions for drawing strokes

3.**extract_kanjivg.py** --> converts characters defined in bezeir curves into characters with simple line segments

4.**local_strokegenerator.py** --> python generator, which yields data required for training local model

5.**kanjivg_modified.tar.gz** --> compressed file with kanjivg modified characters (bezeir to line segment converted)

6.**derprecated/** --> folder with python scripts which create pickled datasets (generates large datasets as much as 55GB or more depending on sample size, using python generator is much lighter and faster less I/O during training)

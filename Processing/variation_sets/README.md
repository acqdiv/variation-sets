# Processing

Code in this directory contains various scripts for processing variation sets.
The scripts in this folder are written to use `python3`.

## Requirements

This really only requires SQLAlchemy, however, if you want to play it safe, we have provided a requirements.txt:

`pip install -r requirements.txt`

##  get_variation_sets.py

`get_variation_sets.py` is a means of both counting and dumping all utterances that constitute a variation set in the ACQDIV database. If you are ready to get st

`python3 get_variation_sets.py -h`

Many of the flags are required, so here's an example using the cats gold dataset:

`python3 get_variation_sets.py -f fixtures/gold-cats.sqlite3 -w 2 -w 10 -m 1`

The output files are written to the `results` directory.

Required flags include:

`-f` indicates the file, followed by the filename

`-w` indicates the window size that we are searching through. If you want to search a range of window, then you use two of these: `-w 3 -w 5` would go through window sizes of 3. 4, 5

`-m` indicates the number of minimum matches and is used similarly to `-w` in that if you want to use a range, you use it twice

Optional Flags:

`-t` indicates at what tier `morphemes` vs `words` you want to process, defaults to words: `-t morphemes`

`-v` runs the analysis only on verbs and nouns

`-n` runs the incremental analysis (default is anchor)

`-z #`  does fuzzy matching on a word or phrase level. Matching on a word level is accomplished using levenstein distance (see: https://en.wikipedia.org/wiki/Levenshtein_distance) and is accomplished by passing an integar.For example if you want `dog` and `dogs` to register as the same word, then you want to pass `-z 1`. In order to match at a phrasal level, using the python difflib SequenceMatcher, then pass a float between `0.01` and `0.99`. In tests on gold standards, numbers between `0.5` and `0.6` have worked out the best: `-z 0.55`.

`-e` when running in the BNC English data (different database format than ACQDIV)

`-c` when running on Chintang adult data

`-r` when running the randomized corpus data from NAL (different database format)


### Output

`get_variation_sets.py` will create two `.csv` files: `DAY_MONTH_YEAR_utterances.csv` and `DAY_MONTH_YEAR_counts.csv`.


#### Counts

At a minimum this will have a column for `session_id`, `total_utterances`, and then columns for each permutation of window-size and matching numbers (e.g. `fuzzy_3_2` for a window of 3 and a minimum matches of 2).


#### Utterances

This has column headers `unit`, `session_id`, `language`, `utterance`, `window_size`, `matches`

`unit` is just a count id for the pairs of utterances that constitute the variation set.
As of the time of this writing, there is no other information about the position or anything, there could be any number of utterances in between or following.

Here's an example:
```
'unit','session_id','language','utterance','window_size','matches'
0,1,English,"see the dog",3,3
0,1,English,"do you see the dog",3,3
1,1,...
```

## Get age in days per session

`python3 get_age_in_days.py test.sqlite3`

Output:

```
"session_id","corpus","age_in_days","unique_speaker_id","speaker_label","macrorole"
"1","Chintang","1825","6","DLCh1","Target_Child"
"2","Cree","774","20","CHI","Target_Child"
"3","Indonesian","617","22","CHI","Target_Child"
"4","Inuktitut","916","32","ALI","Target_Child"
"5","Japanese_Miyata","522","34","CHI","Target_Child"
"6","Japanese_MiiPro","1096","36","ALS","Target_Child"
"7","Russian","625","41","ALJ","Target_Child"
"9","Turkish","242","46","CHI","Target_Child"
"10","Yucatec","1118","48","ARM","Target_Child"
```

## Tests

In order to run tests, we have provided a script: `tests.sh`:

`./tests.sh`

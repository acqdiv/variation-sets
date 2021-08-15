# Notes for English BNC

1. Run `combine.R` data to clean up the BNC data and to reduce the sample to 1M words.

2. Follow the `sqlite-instructions.txt` commands.

3. Generate the variation sets output:

`python3 get_variation_sets.py -f English_Adults/english.sqlite3 -w 1 -w 10 -m 1 -v`

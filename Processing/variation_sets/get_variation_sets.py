"""This is a script that takes the variation set data from an sqlite database, analyzes it for variation
sets and then creates a single CSV file. To see all of the options, you can call this script with the -h flag."""

import os
import sys
import csv
import time
import argparse

from itertools import groupby

import sqlalchemy as sa
import db_backend as db
import db_backend_randomized as db_randomized

import utils as vs

engine = None
conn = None


def setup(url):
    """Sqlite DB connection."""
    url = "sqlite:///" + url
    global engine, conn
    engine = sa.create_engine(url)
    conn = engine.connect()


def file_check(out_file_name):
    """Checks to see whether a file already exists."""
    if out_file_name in os.listdir():
        check = input("""There is already a file with the name that will be created and this will overwrite it. Are you
        sure that you want to do this? y/n: """)
        if check != "y":
            sys.exit()
    else:
        return True


def _multi_field(name):
    """There's no way this is the most efficient way to do this but it iterates through every possible permutation of
    window size and match size.
    TODO: unnest
    """
    fields = []
    # if there is a window range
    if len(args.window) > 1:
        for i in range(int(args.window[0]), int(args.window[1]) + 1):
            # matches range
            if len(args.minimum_matches) > 1:
                for j in range(int(args.minimum_matches[0]), int(args.minimum_matches[1]) + 1):
                    fields.append(name + "_" + str(i) + "_" + str(j))
            # single match size
            else:
                fields.append(name + "_" + str(i) + "_" + args.minimum_matches[0])
    # single window
    else:
        # matches range
        if len(args.minimum_matches) > 1:
            for j in range(int(args.minimum_matches[0]), int(args.minimum_matches[1]) + 1):
                fields.append(name + "_" + args.window[0] + "_" + str(j))
        # single match size
        else:
            fields.append(name + "_" + args.window[0] + "_" + args.minimum_matches[0])
    return fields


def _create_fields(args):
    """Create the header for the columns in the output data."""
    fields = ['session_id', 'total_utterances']
    if args.fuzzy[0] is None:
        fields.extend(_multi_field("strict"))
    else:
        fields.extend(_multi_field("fuzzy"))
    return fields


def _win_min_iter(args):
    """Permutations of each of the windows and min_matches. Again this could be done better, but I turned it into
    an iterator. So it can be reused."""
    if len(args.window) > 1:
        for i in range(int(args.window[0]), int(args.window[1]) + 1):
            if len(args.minimum_matches) > 1:
                for j in range(int(args.minimum_matches[0]), int(args.minimum_matches[1]) + 1):
                    yield i, j
            else:
                yield i, int(args.minimum_matches[0])
    else:
        if len(args.minimum_matches) > 1:
            for j in range(int(args.minimum_matches[0]), int(args.minimum_matches[1]) + 1):

                yield int(args.window[0]), j
        else:
            yield int(args.window[0]), int(args.minimum_matches[0])


def write_dumps(utterances_to_dump, count, dump_out, window, matches, session_id, args):
    """Write utterance pair along with item number to csv, one utterance per line"""
    count = 0
    for utterance_pair in utterances_to_dump:
        count += 1
        if args.write_output:
            to_write = ' '.join([i for i in utterance_pair[0] if not isinstance(i, type(None))])
            dump_out.writerow([count, session_id, to_write, window, matches])
            to_write = ' '.join([i for i in utterance_pair[1] if not isinstance(i, type(None))])
            dump_out.writerow([count, session_id, to_write, window, matches])
    return count


def _out_filename(args):
    """Create file name for output file"""
    base_name = os.path.basename(args.filename)
    file_root_name = os.path.splitext(base_name)[0]

    filename_root = file_root_name + "_w"
    for i in args.window:
        filename_root += "_"
        filename_root += i

    filename_root += "_m"
    for i in args.minimum_matches:
        filename_root += "_"
        filename_root += i

    if args.nouns_verbs:
        filename_root += "_v"

    if args.incremental:
        filename_root += "_n"

    if args.fuzzy[0]:
        to_add = str(args.fuzzy[0])
        # remove decimal point
        to_add = to_add.replace(".", "")
        filename_root = filename_root + "_z" + to_add

    if args.tier == 'morphemes':
        filename_root += "_morph"

    counts_filename = "results/" + filename_root + "_counts.csv"
    utterances_filename = "results/" + filename_root + "_utterances.csv"

    return counts_filename, utterances_filename


def write_output(query, args):
    """Write the output to disk. TODO: expand args to incorporate this."""
    tier = args.tier  # Identify if word or morpheme tier
    fields = _create_fields(args)  # Create column names for CSV output

    counts_filename, utterances_filename = _out_filename(args) # Create the filenames for counts and utterances output

    if isinstance(args.fuzzy, type(None)):
        fuzzy = None
    else:
        fuzzy = args.fuzzy[0]

    with open(counts_filename, 'w') as counts_output, open(utterances_filename, 'w') as utterances_output:
        counts_out = csv.writer(counts_output, dialect='unix')
        counts_out.writerow(fields)

        utterances_out = csv.writer(utterances_output, dialect='unix')
        utterances_out.writerow(["unit", "session_id", "utterance", "window_size", "matches"])
        count = 0

        # Iterate over utterances by session
        for session, rows in groupby(query, lambda r: r['session_id']):
            # Here are the fields being returned and an example:
            # sesssion_id_fk, utterance_id, speaker_id, speaker macrorole, utterance
            # e.g.: (1, 1, 5, 'Adult', 5, 'habinɨŋ habinɨŋ')

            print('Processing session number:', session)
            everything = [row for row in rows]

            utterance_ids = [row[1] for row in everything]

            utterances = None
            if args.english_bnc:
                # Special case for BNC's different database format (argh!)
                # Note: get_utterances returns [['a', 'b'], ['x', 'a']] by type
                utterances = get_utterances_bnc(tier, utterance_ids, args, session)
            elif args.random_text:
                # Case for randomized denormalized tables from NAL
                utterances = get_utterances_randomized(tier, utterance_ids, args, session)
            else:
                utterances = get_utterances(tier, utterance_ids, args)

            # Begin writing output for counts
            to_write = [session]
            to_write.append(len(utterance_ids))

            utterances_to_dump = None
            num_variation_sets = None

            # Iterate over pairs of utterances
            for pair in _win_min_iter(args):
                utterances_by_window = vs.window(utterances, pair[0])

                if args.incremental:
                    num_variation_sets, utterances_to_dump = vs.matches_incremental(utterances_by_window, pair[1], fuzzy)
                    if len(utterances_to_dump) > 0:
                        count = write_dumps(utterances_to_dump, count, utterances_out, pair[0], pair[1], session, args)

                # Default: anchor method
                else:
                    num_variation_sets, utterances_to_dump = vs.matches_anchor(utterances_by_window, pair[1], fuzzy)
                    if len(utterances_to_dump) > 0:
                        count = write_dumps(utterances_to_dump, count, utterances_out, pair[0], pair[1], session, args)

                to_write.append(num_variation_sets)
            counts_out.writerow(to_write)


def _range_check(the_args):
    """Check window and minimum matches are properly formatted."""
    if not the_args:
        sys.exit("You must specify a min. match/window value or range with -w and -m")
    elif len(the_args) > 2:
        sys.exit("Ranges must consist of one or two terms")
    try:
        a = [int(i) for i in the_args]
        if len(a) == 2 and a[0] > a[1]:
            sys.exit("In ranges, please make the first integer the lower number")
    except ValueError:
        sys.exit("Window/Minimum match must be an integer ex: -w 2")


def _type_checker(the_args):
    try:
        the_args = the_args[0]
    except TypeError:
        pass

    if the_args is None:
        return [None]
    try:
        return [int(the_args)]
    except ValueError:
        return [float(the_args)]


def get_utterances(tier, utterance_ids, args):
    """Get all utterances given (a subset, e.g. CDS) a list of utterance ids."""
    utterances = []
    if tier == 'words':
        # TODO: unpack it?
        s = sa.select([
            db.Word.utterance_id_fk.label('uid'), db.Word.word, db.Word.pos
        ], db.Word.utterance_id_fk.in_(utterance_ids)).order_by(db.Word.id)
        query = conn.execute(s)
        for utterance, words in groupby(query, lambda r: r['uid']):
            temp = []
            for word in words:
                if args.nouns_verbs:
                    if word[2] == 'N' or word[2] == 'V':
                        temp.append(word[1].lower())
                else:
                    temp.append(word[1].lower())
            utterances.append(temp)

    elif tier == 'morphemes':
        s = sa.select(
            [db.Morpheme.utterance_id_fk.label('uid'), db.Morpheme.morpheme,
                db.Morpheme.pos],
            db.Morpheme.utterance_id_fk.in_(utterance_ids)).order_by(db.Morpheme.id)
        query = conn.execute(s)
        for utterance, morphemes in groupby(query, lambda r: r['uid']):
            temp = []
            for morpheme in morphemes:
                if morpheme[1]:
                    if args.nouns_verbs:
                        if morpheme[2] == 'N' or morpheme[2] == 'V':
                            temp.append(morpheme[1].lower())
                    else:
                        temp.append(morpheme[1].lower())
            utterances.append(temp)
    return utterances

def get_utterances_randomized(tier, utterance_ids, args, session):
    """Get all utterances given (a subset, e.g. CDS) a list of utterance ids."""
    utterances = []
    if tier == 'words':
        s = sa.select([db_randomized.Result.utterance_id_fk_rand.label('uid'),
                       db_randomized.Result.word,
                       db_randomized.Result.pos,
                       db_randomized.Result.session_id_fk]).where(db_randomized.Result.session_id_fk == session)
        query = conn.execute(s)
        for utterance, words in groupby(query, lambda r: r['uid']):
            temp = []
            for word in words:
                if args.nouns_verbs:
                    if word[2] == 'N' or word[2] == 'V':
                        temp.append(word[1])
                else:
                    temp.append(word[1])
            utterances.append(temp)

    elif tier == 'morphemes':
        s = sa.select([db_randomized.Result.utterance_id_fk_rand.label('uid'),
                       db_randomized.Result.morpheme,
                       db_randomized.Result.pos,
                       db_randomized.Result.session_id_fk]).where(db_randomized.Result.session_id_fk == session)
        query = conn.execute(s)
        for utterance, morphemes in groupby(query, lambda r: r['uid']):
            temp = []
            for morpheme in morphemes:
                if morpheme[1]:
                    if args.nouns_verbs:
                        if morpheme[2] == 'N' or morpheme[2] == 'V':
                            temp.append(morpheme[1])
                    else:
                        temp.append(morpheme[1])
            utterances.append(temp)
    return utterances


def get_utterances_bnc(tier, utterance_ids, args, session):
    """Get all utterances given (a subset, e.g. CDS) a list of utterance ids."""
    utterances = []
    if tier == 'words':
        # TODO: unpack it?
        s = sa.select([
            db.Word.utterance_id_fk.label('uid'), db.Word.word, db.Word.pos, db.Word.session_id_fk,
        ]).where(sa.and_(db.Word.session_id_fk == session, db.Word.utterance_id_fk.in_(utterance_ids))).order_by(db.Word.id)
        query = conn.execute(s)
        for utterance, words in groupby(query, lambda r: r['uid']):
            temp = []
            for word in words:
                if args.nouns_verbs:
                    if word[2] == 'N' or word[2] == 'V':
                        temp.append(word[1])
                else:
                    temp.append(word[1])
            utterances.append(temp)

    elif tier == 'morphemes':
        s = sa.select(
            [db.Morpheme.utterance_id_fk.label('uid'), db.Morpheme.morpheme,
                db.Morpheme.pos],
            db.Morpheme.utterance_id_fk.in_(utterance_ids)).order_by(db.Morpheme.id)
        query = conn.execute(s)
        for utterance, morphemes in groupby(query, lambda r: r['uid']):
            temp = []
            for morpheme in morphemes:
                if morpheme[1]:
                    if args.nouns_verbs:
                        if morpheme[2] == 'N' or morpheme[2] == 'V':
                            temp.append(morpheme[1])
                    else:
                        temp.append(morpheme[1])
            utterances.append(temp)
    return utterances

def get_session_utterances(args):
    if args.random_text:
        """Get utterance IDs in the randomized texts from NAL (denormalized table). Data is all adults."""
        print("Processing randomized text format")
        # s = sa.select([db_randomized.Result.session_id_fk.label('session_id'), db_randomized.Result.utterance_id_fk_rand]).distinct()
        s = sa.select([db_randomized.Result.session_id_fk.label('session_id'),
                       db_randomized.Result.utterance_id_fk_rand]).distinct()
        query = conn.execute(s)
        return query

    elif args.english_bnc:
        """Get utterance IDs in the BNC corpus (has different database format than ACQDIV)."""
        print("Processing English BNC corpus for ADS")
        s = sa.select([db.Utterance.session_id_fk.label('session_id'),
                       db.Utterance.id,
                       db.Speaker.id,
                       db.Speaker.macrorole,
                       db.Utterance.speaker_id_fk,
                       db.Utterance.utterance]).where(sa.and_(
            db.Utterance.source_id == db.Speaker.session_id_fk,
            db.Utterance.speaker_label == db.Speaker.speaker_label,
            db.Speaker.macrorole == "Adult")).order_by(db.Utterance.session_id_fk, db.Utterance.id)
        query = conn.execute(s)
        return query

    elif args.chintang_adults:
        """Get utterance IDS for adult Chintang sessions in ACQDIV database v1.0.0."""
        print("Processing Chintang ADS in ACQDIV database format")
        # Chintang adult session IDs that aren't missing speaker information
        chintang_adult_sessions = [498, 504, 506, 520, 527, 533, 561, 562, 576, 577, 582, 587, 665, 671, 689, 700, 702,
                                   711]
        s = sa.select([db.Utterance.session_id_fk.label('session_id'),
                       db.Utterance.id,
                       db.Speaker.id,
                       db.Speaker.macrorole,
                       db.Utterance.speaker_id_fk,
                       db.Utterance.utterance],
                      db.Utterance.session_id_fk.in_(chintang_adult_sessions)).where(sa.and_(
            db.Utterance.session_id_fk == db.Speaker.session_id_fk,
            db.Utterance.speaker_id_fk == db.Speaker.id,
            db.Speaker.macrorole == "Adult")).order_by(db.Utterance.id)
        query = conn.execute(s)
        return query

    else:
        """Get utterance IDS for CDS in the ACQDIV database v1.0.0."""
        print("Processing ACQDIV database for CDS")
        s = sa.select([db.Utterance.session_id_fk.label('session_id'),
                       db.Utterance.id,
                       db.Speaker.id,
                       db.Speaker.macrorole,
                       db.Utterance.speaker_id_fk,
                       db.Utterance.utterance]).where(sa.and_(
            db.Utterance.session_id_fk == db.Speaker.session_id_fk,
            db.Utterance.speaker_id_fk == db.Speaker.id,
            db.Speaker.macrorole == "Adult")).order_by(db.Utterance.id)
        query = conn.execute(s)
        return query


def main(args):
    setup(args.filename)
    query = get_session_utterances(args)
    # file_check(out_file)  # Check if file already exists on disk (give user option for exiting)
    write_output(query, args)  # Write CSV to disk


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for variation sets")
    parser.add_argument("-f", "--file", dest="filename", type=str, help="required: name of file *.sqlite")
    parser.add_argument("-t", "--tier", dest="tier", type=str, default="words", help="morphemes or words; "
                                                                                     "default is words")
    parser.add_argument("-w", "-window", action="append", dest="window", help="""window size, use once for a single
    window, twice for a range ex: -w 2 OR -w 2 -w 5""")
    parser.add_argument("-n", "--incremental", dest="incremental", action="store_true",
                        help="incremental scanning, otherwise defaults to anchor")
    parser.add_argument("-m", "-minimum", action="append",
                        dest="minimum_matches",
                        help="""minimum matches, use once for a single minimum match size, twice for a range ex:
                        -m 2 OR -m 2 -m 5""")
    parser.add_argument("-v", dest="nouns_verbs", action="store_true",
                        help="make variation sets only on nouns and verbs")
    parser.add_argument("-z", dest="fuzzy", action="append",
                        help="fuzzy matching, number is how much overlap there should be")
    parser.add_argument("-e", dest="english_bnc", action="store_true",
                        help="Run this code on the English BNC corpus")
    parser.add_argument("-c", dest="chintang_adults", action="store_true",
                        help="Run this code on the Chintang adult data")
    parser.add_argument("-r", dest="random_text", action="store_true",
                        help="Run this code on the randomized data")
    parser.add_argument("-o", dest="write_output", action="store_true",
                        help="Write the utterances to disk")


    args = parser.parse_args()

    if not args.filename:
        sys.exit("You need to pass a filename: -f filename")
    if args.tier not in ["words", "morphemes"]:
        sys.exit("-t|--tier must be either 'words' or 'morphemes'")

    args.fuzzy = _type_checker(args.fuzzy)

    _range_check(args.window)
    _range_check(args.minimum_matches)

    # Main
    start_time = time.time()
    main(args)
    print("%s seconds --- Finished" % (time.time() - start_time))

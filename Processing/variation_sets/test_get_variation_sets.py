
import get_variation_sets as gvs
import utils as vs

import unittest
import argparse

from itertools import groupby


class SmallSampleTest(unittest.TestCase):

    def setUp(self):

        self.filename = "fixtures/test.sqlite3"
        gvs.setup(self.filename)
        self.query = gvs.get_session_utterances()

        self.data = list()
        self.session_ids = list()

        for session, rows in groupby(self.query, lambda r: r['session_id']):
            self.session_ids.append(session)
            self.data.append([row for row in rows])

        self.utt_ids = list()
        for rows in self.data:
            self.utt_ids.append([row[2] for row in rows if row[4] not in ["Target_Child", "Child"]])

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-v", dest="nouns_verbs", action="store_true")
        self.parser.add_argument("-w", "-window", action="append", dest="window")
        self.parser.add_argument("-m", "-minimum", action="append", dest="minimum_matches")
        self.args = self.parser.parse_args(['-w', '2', '-m', '2'])

        self.args.window = [2]
        self.args.minimum_matches = [2]

        self.utterances = list()
        for id_list in self.utt_ids:
            self.utterances.append(gvs.get_utterances("words", id_list, self.args))

    def test_structure_using_len(self):
        """Test that the structure of the reading in is correct"""
        a = [3, 14, 1, 10, 12, 15, 2]
        self.assertEqual([len(i) for i in self.data], a)

    def test_session_ids(self):
        """Test that the right session numbers are read in"""
        a = [1, 3, 5, 6, 7, 9, 11]
        self.assertEqual(self.session_ids, a)

    def test_session_ids_num(self):
        """Test that the right number of utterance ids are read in"""
        a = [len(i) for i in self.utt_ids]
        b = [3, 14, 1, 10, 12, 15, 2]
        self.assertEqual(a, b)

    def test_get_utterances_words(self):
        """Test that utterances are getting correctly read in from their ids"""
        a = [['da', 'da', None, 'Tante', 'Tante', 'Tante'],
             ['masih', 'diem', 'aja', 'inih'],
             ['ngapain', 'tu', 'Tante', 'ngapain', 'ngapain', 'Tante', None, 'apain'],
             ['mandinya', 'sama', 'siapa'],
             [None],
             ['lagi', 'nggosok', 'liatin'],
             ['ta', 'gosok', 'giginya'],
             ['hi', 'gitu', 'hi', 'hi'],
             ['hmm', 'pinter'],
             [None, 'ini', 'dah', 'cepet'],
             ['tuh', 'ban'],
             ['mandinya', 'sama', 'siapa']]

        self.assertEqual(self.utterances[1], a)

    def test_win_min_iter_w_2_m_2(self):
        """Test that the right window and match sizes are being run,
        in this case a window of 2 and minimum matches of 2"""

        a = [pair for pair in gvs._win_min_iter(self.args)]
        self.assertEqual(a, [(2, 2)])

    def test_win_min_iter_w_2_w_4_m_2(self):
        """Test that a window range is correctly executed"""
        self.args.window = [2, 4]
        self.args.minimum_matches = [2]

        a = [pair for pair in gvs._win_min_iter(self.args)]
        actual_answer = [(2, 2), (3, 2), (4, 2)]
        self.assertEqual(a, actual_answer)

    def test_win_min_iter_w_2_m_2_m_4(self):
        """Test that a minimum matches range is correctly executed"""
        self.args.window = [2]
        self.args.minimum_matches = [2, 4]

        a = [pair for pair in gvs._win_min_iter(self.args)]
        actual_answer = [(2, 2), (2, 3), (2, 4)]
        self.assertEqual(a, actual_answer)

    def test_win_min_iter_w_2_w_4_m_2_m_4(self):
        """Test that both a window and minimum matches range are
        correcly executed"""

        self.args.window = [2, 4]
        self.args.minimum_matches = [2, 4]
        actual_answer = [(2, 2), (2, 3), (2, 4),
                         (3, 2), (3, 3), (3, 4),
                         (4, 2), (4, 3), (4, 4)]

        a = [pair for pair in gvs._win_min_iter(self.args)]
        self.assertEqual(a, actual_answer)

    def test_utterances_by_window_window_2(self):
        """Test that utterances are correctly retrieved
        given a certain window size, in this case 2"""

        self.args.window = [2]
        self.args.minimum_matches = [2]

        a = [(['Alja', 'ne', 'trogaj', 'kisu'],
              ['Alja', 'tam', 'Pusha', 'est']),
             (['Alja', 'tam', 'Pusha', 'est'],
              ['ne', 'umeeshq']),
             (['ne', 'umeeshq'],
              ['shapku', 'odeli']),
             (['shapku', 'odeli'],
              ['prishla', 'drugaja', 'devochka']),
             (['prishla', 'drugaja', 'devochka'],
              ['merzni-merzni', 'volchij', 'xvost']),
             (['merzni-merzni', 'volchij', 'xvost'],
              ['pushistyj']),
             (['pushistyj'],
              ['da', 'ne', 'bu']),
             (['da', 'ne', 'bu'],
              ['zhivot', 'u', 'nego', 'vesq']),
             (['zhivot', 'u', 'nego', 'vesq'],
              ['Ne', 'skazhu', 'nichego', 'skazhi'])]

        for pair in gvs._win_min_iter(self.args):
            utterances_by_window = vs.window(self.utterances[4], pair[0])
            self.assertEqual(a, [i for i in utterances_by_window])

    def test_matches_incremental(self):
        """Test that the correct number of matches are retrieved given the
        incremental method of mathing is used"""

        self.args.window = [2]
        self.args.minimum_matches = [2]

        pair = [pair for pair in gvs._win_min_iter(self.args)][0]

        a = [(0, []),
             (0, []),
             (0, []),
             (0, []),
             (0, []),
             (1, [(['onu', 'kaldırdı', 'Necla'], ['Necla', 'kaldırdı'])]),
             (0, [])]

        counts = list()

        for utterance in self.utterances:
            utterances_by_window = vs.window(utterance, pair[0])
            counts.append(vs.matches_incremental(utterances_by_window, pair[1], None))

        self.assertEqual(a, counts)

    def test_matches_anchor(self):
        """Test that the correct number of matches are retrieved given the
        anchor method is used"""

        self.args.window = [2]
        self.args.minimum_matches = [2]

        pair = [i for i in gvs._win_min_iter(self.args)][0]

        counts = list()
        a = [(0, []),
             (0, []),
             (0, []),
             (0, []),
             (0, []),
             (1, [(['onu', 'kaldırdı', 'Necla'], ['Necla', 'kaldırdı'])]),
             (0, [])]

        for utterance in self.utterances:
            utterances_by_window = vs.window(utterance, pair[0])
            counts.append(vs.matches_anchor(utterances_by_window, pair[1], None))

        self.assertEqual(a, counts)


class GoldTest(unittest.TestCase):

    def setUp(self):

        self.filename = "fixtures/gold.sqlite3"
        gvs.setup(self.filename)
        self.query = gvs.get_session_utterances()

        self.data = list()
        self.session_ids = list()

        for session, rows in groupby(self.query, lambda r: r['session_id']):
            self.session_ids.append(session)
            self.data.append([row for row in rows])

        self.utt_ids = list()
        for rows in self.data:
            self.utt_ids.append([row[2] for row in rows if row[4] not in ["Target_Child", "Child"]])

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-v", dest="nouns_verbs", action="store_true")
        self.parser.add_argument("-w", "-window", action="append", dest="window")
        self.parser.add_argument("-m", "-minimum", action="append", dest="minimum_matches")
        self.parser.add_argument("-n", "--incremental", dest="incremental", action="store_true")
        self.args = self.parser.parse_args(['-w', '2', '-m', '2'])

        self.args.window = [2]
        self.args.minimum_matches = [2]

    def get_counts(self, args):
        to_test = list()

        for id_list in self.utt_ids:
            session_variation_sets = list()
            utterances = gvs.get_utterances("words", id_list, args)

            for pair in gvs._win_min_iter(args):
                utterances_by_window = vs.window(utterances, pair[0])
                if args.incremental:
                    num_variation_sets = vs.matches_incremental(utterances_by_window, pair[1], None)
                else:
                    num_variation_sets = vs.matches_anchor(utterances_by_window, pair[1], None)
                session_variation_sets.append(num_variation_sets)
            to_test.append(session_variation_sets)

        return(to_test)

    def test_anchor_w_2_4_m_1_3(self):
        args = self.args
        args.window = [2, 4]
        args.minimum_matches = [1, 3]

        gold_gold = [[(1, [(['d', 'e', 'f'], ['d', 'g', 'h'])]),
                      (0, []),
                      (0, []),
                      (2, [(['d', 'e', 'f'], ['d', 'g', 'h']), (['d', 'g', 'h'], ['e', 'g', 'h'])]),
                      (1, [(['d', 'g', 'h'], ['e', 'g', 'h'])]),
                      (0, []),
                      (1, [(['d', 'e', 'f'], ['d', 'g', 'h'])]),
                      (0, []),
                      (0, [])],
                     [(3, [(['a', 'b', 'x'], ['x', 'c', 'd']), (['x', 'c', 'd'], ['d', 'x', 'e']),
                           (['d', 'x', 'e'], ['f', 'x', 'g'])]),
                      (1, [(['x', 'c', 'd'], ['d', 'x', 'e'])]),
                      (0, []),
                      (2, [(['a', 'b', 'x'], ['x', 'c', 'd']), (['x', 'c', 'd'], ['d', 'x', 'e'])]),
                      (1, [(['x', 'c', 'd'], ['d', 'x', 'e'])]),
                      (0, []),
                      (1, [(['a', 'b', 'x'], ['x', 'c', 'd'])]),
                      (0, []),
                      (0, [])],
                     [(3, [(['A', 'B', 'C'], ['D', 'B', 'E']), (['D', 'B', 'E'], ['D', 'F', 'G']),
                           (['D', 'F', 'G'], ['D', 'K', 'L'])]),
                      (0, []),
                      (0, []),
                      (3, [(['A', 'B', 'C'], ['D', 'B', 'E']), (['D', 'B', 'E'], ['D', 'F', 'G']),
                           (['D', 'F', 'G'], ['D', 'F', 'G'])]),
                      (1, [(['D', 'F', 'G'], ['D', 'F', 'G'])]),
                      (1, [(['D', 'F', 'G'], ['D', 'F', 'G'])]),
                      (3, [(['A', 'B', 'C'], ['D', 'B', 'E']), (['D', 'B', 'E'], ['D', 'F', 'G']),
                           (['D', 'F', 'G'], ['D', 'F', 'G'])]),
                      (1, [(['D', 'F', 'G'], ['D', 'F', 'G'])]),
                      (1, [(['D', 'F', 'G'], ['D', 'F', 'G'])])]]

        self.assertEqual(gold_gold, self.get_counts(args))

    def test_anchor_w_2_4_m_1_3_nouns_and_verbs(self):
        args = self.args
        args.window = [2, 4]
        args.minimum_matches = [1, 3]
        args.nouns_verbs = True

        gold_gold = [[(1, [(['d', 'e', 'f'], ['d', 'g', 'h'])]),
                      (0, []),
                      (0, []),
                      (2, [(['d', 'e', 'f'], ['d', 'g', 'h']), (['d', 'g', 'h'], ['e', 'g', 'h'])]),
                      (1, [(['d', 'g', 'h'], ['e', 'g', 'h'])]),
                      (0, []),
                      (1, [(['d', 'e', 'f'], ['d', 'g', 'h'])]),
                      (0, []),
                      (0, [])],
                     [(3, [(['a', 'b', 'x'], ['x', 'c', 'd']), (['x', 'c', 'd'], ['d', 'x', 'e']),
                           (['d', 'x', 'e'], ['f', 'x', 'g'])]),
                      (1, [(['x', 'c', 'd'], ['d', 'x', 'e'])]),
                      (0, []),
                      (2, [(['a', 'b', 'x'], ['x', 'c', 'd']), (['x', 'c', 'd'], ['d', 'x', 'e'])]),
                      (1, [(['x', 'c', 'd'], ['d', 'x', 'e'])]),
                      (0, []),
                      (1, [(['a', 'b', 'x'], ['x', 'c', 'd'])]),
                      (0, []),
                      (0, [])],
                     [(2, [(['D'], ['D', 'G']), (['D', 'G'], ['D'])]),
                      (0, []),
                      (0, []),
                      (2, [(['D'], ['D', 'G']), (['D', 'G'], ['D', 'G'])]),
                      (1, [(['D', 'G'], ['D', 'G'])]),
                      (0, []),
                      (2, [(['D'], ['D', 'G']), (['D', 'G'], ['D', 'G'])]),
                      (1, [(['D', 'G'], ['D', 'G'])]),
                      (0, [])]]

        self.assertEqual(gold_gold, self.get_counts(args))

    def test_incremental_w_2_4_m_1_3_nouns_and_verbs(self):
        args = self.args
        args.window = [2, 4]
        args.minimum_matches = [1, 3]
        args.nouns_verbs = True
        args.incremental = True

        gold_gold = [[(1, [(['d', 'e', 'f'], ['d', 'g', 'h'])]),
                      (0, []),
                      (0, []),
                      (2, [(['d', 'e', 'f'], ['d', 'g', 'h']), (['d', 'e', 'f'], ['d', 'g', 'h'])]),
                      (0, []),
                      (0, []),
                      (2, [(['d', 'e', 'f'], ['d', 'g', 'h']), (['d', 'e', 'f'], ['d', 'g', 'h'])]),
                      (0, []),
                      (0, [])],
                     [(3, [(['a', 'b', 'x'], ['x', 'c', 'd']), (['x', 'c', 'd'], ['d', 'x', 'e']),
                           (['d', 'x', 'e'], ['f', 'x', 'g'])]),
                      (1, [(['x', 'c', 'd'], ['d', 'x', 'e'])]),
                      (0, []),
                      (4, [(['a', 'b', 'x'], ['x', 'c', 'd']), (['x', 'c', 'd'], ['d', 'x', 'e']),
                           (['x', 'c', 'd'], ['d', 'x', 'e']), (['d', 'x', 'e'], ['f', 'x', 'g'])]),
                      (2, [(['x', 'c', 'd'], ['d', 'x', 'e']), (['x', 'c', 'd'], ['d', 'x', 'e'])]),
                      (0, []),
                      (3, [(['a', 'b', 'x'], ['x', 'c', 'd']), (['x', 'c', 'd'], ['d', 'x', 'e']),
                           (['d', 'x', 'e'], ['f', 'x', 'g'])]),
                      (1, [(['x', 'c', 'd'], ['d', 'x', 'e'])]),
                      (0, [])],
                     [(2, [(['D'], ['D', 'G']), (['D', 'G'], ['D'])]), (0, []), (0, []),
                      (3, [(['D'], ['D', 'G']), (['D'], ['D', 'G']), (['D', 'G'], ['D'])]),
                      (0, []),
                      (0, []),
                      (3, [(['D'], ['D', 'G']), (['D'], ['D', 'G']), (['D', 'G'], ['D'])]),
                      (0, []),
                      (0, [])]]

        self.assertEqual(gold_gold, self.get_counts(args))

    def test_incremental_w_2_4_m_1_3(self):
        args = self.args
        args.window = [2, 4]
        args.minimum_matches = [1, 3]
        args.incrementas = True

        gold_gold = [[(1, [(['d', 'e', 'f'], ['d', 'g', 'h'])]),
                      (0, []),
                      (0, []),
                      (2, [(['d', 'e', 'f'], ['d', 'g', 'h']), (['d', 'g', 'h'], ['e', 'g', 'h'])]),
                      (1, [(['d', 'g', 'h'], ['e', 'g', 'h'])]),
                      (0, []),
                      (1, [(['d', 'e', 'f'], ['d', 'g', 'h'])]),
                      (0, []),
                      (0, [])],
                     [(3, [(['a', 'b', 'x'], ['x', 'c', 'd']), (['x', 'c', 'd'], ['d', 'x', 'e']),
                           (['d', 'x', 'e'], ['f', 'x', 'g'])]),
                      (1, [(['x', 'c', 'd'], ['d', 'x', 'e'])]),
                      (0, []),
                      (2, [(['a', 'b', 'x'], ['x', 'c', 'd']), (['x', 'c', 'd'], ['d', 'x', 'e'])]),
                      (1, [(['x', 'c', 'd'], ['d', 'x', 'e'])]),
                      (0, []),
                      (1, [(['a', 'b', 'x'], ['x', 'c', 'd'])]),
                      (0, []),
                      (0, [])],
                     [(3, [(['A', 'B', 'C'], ['D', 'B', 'E']), (['D', 'B', 'E'], ['D', 'F', 'G']),
                           (['D', 'F', 'G'], ['D', 'K', 'L'])]),
                      (0, []),
                      (0, []),
                      (3, [(['A', 'B', 'C'], ['D', 'B', 'E']), (['D', 'B', 'E'], ['D', 'F', 'G']),
                           (['D', 'F', 'G'], ['D', 'F', 'G'])]),
                      (1, [(['D', 'F', 'G'], ['D', 'F', 'G'])]),
                      (1, [(['D', 'F', 'G'], ['D', 'F', 'G'])]),
                      (3, [(['A', 'B', 'C'], ['D', 'B', 'E']), (['D', 'B', 'E'], ['D', 'F', 'G']),
                           (['D', 'F', 'G'], ['D', 'F', 'G'])]),
                      (1, [(['D', 'F', 'G'], ['D', 'F', 'G'])]),
                      (1, [(['D', 'F', 'G'], ['D', 'F', 'G'])])]]

        self.assertEqual(gold_gold, self.get_counts(args))

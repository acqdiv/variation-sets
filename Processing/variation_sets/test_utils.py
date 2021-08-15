"""
Tests for utils.py
"""

import unittest
import utils


class WindowsTest(unittest.TestCase):
    def test_windows(self):
        a = ["A", "B", "C", "D"]
        assert list(utils.window(a)) == [('A', 'B'), ('B', 'C'), ('C', 'D')]

    def test_windows_3(self):
        a = ["A", "B", "C", "D"]
        assert list(utils.window(a, 3)) == [('A', 'B', 'C'), ('B', 'C', 'D')]


class MatchesAnchorTest(unittest.TestCase):
    a = [[('A', 'B', 'C'), ('D', 'E', 'F'), ('D', 'G', 'H'), ('D', 'G', 'I'), ('D', 'G', 'I')]]

    def test_matches_anchor(self):
        assert utils.matches_anchor(iter(self.a), 49, None) == (0, [])

    def test_matches_anchor_0(self):
        assert utils.matches_anchor(iter(self.a), 0, None) == (1, [(('A', 'B', 'C'), ('D', 'E', 'F'))])

    def test_matches_anchor_1(self):
        assert utils.matches_anchor(iter(self.a), 1, None) == (0, [])

    def test_matches_anchor_1_1(self):
        b = [self.a[0][1:]]
        assert utils.matches_anchor(iter(b), 1, None) == (1, [(('D', 'E', 'F'), ('D', 'G', 'H'))])

    def test_matches_anchor_1_2(self):
        b = [self.a[0][1:]]
        assert utils.matches_anchor(iter(b), 2, None) == (0, [])

    def test_matches_anchor_2_1(self):
        b = [self.a[0][2:]]
        assert utils.matches_anchor(iter(b), 1, None) == (1, [(('D', 'G', 'H'), ('D', 'G', 'I'))])

    def test_matches_anchor_2_2(self):
        b = [self.a[0][2:]]
        assert utils.matches_anchor(iter(b), 2, None) == (1, [(('D', 'G', 'H'), ('D', 'G', 'I'))])

    def test_matches_anchor_3_2(self):
        b = [self.a[0][3:]]
        assert utils.matches_anchor(iter(b), 2, None) == (1, [(('D', 'G', 'I'), ('D', 'G', 'I'))])

    def test_matches_anchor_3_3(self):
        b = [self.a[0][3:]]
        assert utils.matches_anchor(iter(b), 3, None) == (1, [(('D', 'G', 'I'), ('D', 'G', 'I'))])

    def test_matches_anchor_3_4(self):
        b = [self.a[0][3:]]
        assert utils.matches_anchor(iter(b), 4, None) == (0, [])

    def test_matches_anchor_gap(self):
        b = [[('A', 'B', 'C'), ('X', 'Y', 'Z'), ('A', 'B', 'C')]]
        assert utils.matches_anchor(iter(b), 3, None) == (1, [(('A', 'B', 'C'), ('A', 'B', 'C'))])


class MatchesIncrementalTest(unittest.TestCase):
    def test_matches_incremental_gap(self):
        a = [[('A', 'B', 'C'), ('X', 'Y', 'Z'), ('A', 'B', 'C')]]
        assert utils.matches_incremental(iter(a), 1, None) == (0, [])

    def test_matches_incremental_nogap(self):
        a = [[('A', 'B', 'C'), ('A', 'B', 'C')]]
        assert utils.matches_incremental(iter(a), 1, None) == (1, [(('A', 'B', 'C'), ('A', 'B', 'C'))])

    def test_matches_incremental_nogap_2(self):
        a = [[('A', 'B', 'C'), ('A', 'B', 'C'), ('A', 'B', 'C')]]
        assert utils.matches_incremental(iter(a), 2, None) == (2, [(('A', 'B', 'C'), ('A', 'B', 'C')),
                                                                   (('A', 'B', 'C'), ('A', 'B', 'C'))])

    def test_matches_incremental_2_utts(self):
        a = [[('A', 'B', 'C'), ('A', 'B', 'C')],
             [('A', 'B', 'C'), ('A', 'B', 'C')]]
        assert utils.matches_incremental(iter(a), 3, None) == (2, [(('A', 'B', 'C'), ('A', 'B', 'C')),
                                                                   (('A', 'B', 'C'), ('A', 'B', 'C'))])

    def test_matches_incremental_2_utts_to_many(self):
        a = [[('A', 'B', 'C'), ('A', 'B', 'C')],
             [('A', 'B', 'C'), ('A', 'B', 'C')]]
        assert utils.matches_incremental(iter(a), 4, None) == (0, [])

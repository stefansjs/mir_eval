'''
Unit tests for mir_eval.segment
'''

import numpy as np
import json
import mir_eval
import glob

# We only need 1% absolute tolerance
A_TOL = 1e-2

# Path to the fixture files
REF_GLOB    = 'data/segment/ref*.lab'
EST_GLOB    = 'data/segment/est*.lab'
MIREX_GLOB  = 'data/segment/score*.json'

def generate_data():

    ref_files = sorted(glob.glob(REF_GLOB))
    est_files = sorted(glob.glob(EST_GLOB))
    sco_files = sorted(glob.glob(MIREX_GLOB))

    for ref_f, est_f, sco_f in zip(ref_files, est_files, sco_files):
        ref_t, ref_l = mir_eval.io.load_annotation(ref_f)
        est_t, est_l = mir_eval.io.load_annotation(est_f)
        est_t, est_l = mir_eval.util.adjust_intervals(est_t, labels=est_l, t_min=0.0, t_max=ref_t.max())

        with open(sco_f, 'r') as f:
            scores = json.load(f)

        yield ref_t, ref_l, est_t, est_l, scores

def test_boundaries():

    def __test_detection(_window, _ref_t, _est_t):
        precision, recall, fmeasure = mir_eval.boundary.detection(_ref_t, _est_t, window=_window)

        assert np.allclose(precision,   scores['P@%.1f'%_window], atol=A_TOL)
        assert np.allclose(recall,      scores['R@%.1f'%_window], atol=A_TOL)
        assert np.allclose(fmeasure,    scores['F@%.1f'%_window], atol=A_TOL)

    def __test_deviation(_ref_t, _est_t):
        t_to_p, p_to_t = mir_eval.boundary.deviation(_ref_t, _est_t)

        assert np.allclose(t_to_p,  scores['T_to_P'], atol=A_TOL)
        assert np.allclose(p_to_t,  scores['P_to_T'], atol=A_TOL)

    # Iterate over fixtures
    for ref_t, ref_l, est_t, est_l, scores in generate_data():

        # Test boundary detection at each window size
        for window in [0.5, 3.0]:
            yield (__test_detection, window, ref_t, est_t)

        # Test boundary deviation
        yield (__test_deviation, ref_t, est_t)

    # Done
    pass

def test_structure():

    def __test_pairwise(_ref_t, _ref_l, _est_t, _est_l):
        precision, recall, fmeasure = mir_eval.structure.pairwise(_ref_t, _ref_l, _est_t, _est_l)

        assert np.allclose(precision,   scores['Pair-P'], atol=A_TOL)
        assert np.allclose(recall,      scores['Pair-R'], atol=A_TOL)
        assert np.allclose(fmeasure,    scores['Pair-F'], atol=A_TOL)

    def __test_entropy(_ref_t, _ref_l, _est_t, _est_l):
        s_over, s_under, _ = mir_eval.structure.nce(_ref_t, _ref_l, _est_t, _est_l)

        assert np.allclose(s_over,  scores['S_Over'],   atol=A_TOL)
        assert np.allclose(s_under, scores['S_Under'],  atol=A_TOL)

    # Iterate over fixtures
    for ref_t, ref_l, est_t, est_l, scores in generate_data():

        yield (__test_pairwise, ref_t, ref_l, est_t, est_l)
        yield (__test_entropy, ref_t, ref_l, est_t, est_l)

    # Done
    pass


import utils
import unittest
import os
import json
class TestUtilsMethods(unittest.TestCase):

    def test_export_equals_import(self):
        sixteenth_per_beat = 13
        beats_per_bar = 52
        num_bars = 36
        sixteenth_duration = 24
        swing = False
        swing_amount = 0.3
        beat_pattern = []
        is_active = [1,1,1,1,1,1]
        file_name = 'temp.drum'
        utils.export_file(sixteenth_per_beat, beats_per_bar, num_bars, sixteenth_duration, swing, beat_pattern, is_active, swing_amount, file_name)
        s_p_b, b_p_b, n_b, s_d, s, b_p, is_a, s_a = utils.import_file(file_name)
        self.assertEquals(sixteenth_per_beat, s_p_b)
        self.assertEquals(beats_per_bar, b_p_b)
        self.assertEquals(num_bars, n_b)
        self.assertEquals(sixteenth_duration, s_d)
        self.assertEquals(swing, s)
        self.assertEquals(beat_pattern, b_p)
        os.remove(file_name)

    def test_inc_beat(self):
        s_p = 1
        s_p_b = 4
        b_p = 0
        b_p_b = 4
        ba_p = 1
        n_b = 3
        s_p, b_p, ba_p = utils.increment_beat_position(s_p, s_p_b, b_p, b_p_b, ba_p, n_b)
        self.assertEquals(s_p, 2)
        self.assertEquals(b_p, 0)
        self.assertEquals(ba_p, 1)

    def test_inc_beat_rollover(self):
        s_p = 3
        s_p_b = 4
        b_p = 3
        b_p_b = 4
        ba_p = 3
        n_b = 1
        s_p, b_p, ba_p = utils.increment_beat_position(s_p, s_p_b, b_p, b_p_b, ba_p, n_b)
        self.assertEquals(s_p, 0)
        self.assertEquals(b_p, 0)
        self.assertEquals(ba_p, 0)

    def test_nonexistent_file(self):
        self.assertFalse(utils.is_valid_file('awdawd.drum'))
    
    def test_wrong_extension(self):
        self.assertFalse(utils.is_valid_file('drum.dum'))
        
    def test_missing_attribute(self):
        data = {}
        data['sixteenth_per_beat'] = 4
        data['beats_per_bar'] = 4
        data['num_bars'] = 1
        data['sixteenth_duration'] = 150
        data['swing'] = False
        data['beat_pattern'] = [
                                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            
                                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            
                                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
                              ]
        with open('test.drum', 'w') as outfile:
            json.dump(data, outfile)
            
        self.assertFalse(utils.is_valid_file('test.drum'))
        os.remove('test.drum')
        
    def test_bad_beat_pattern(self):
        data = {}
        data['sixteenth_per_beat'] = 4
        data['beats_per_bar'] = 4
        data['num_bars'] = 1
        data['vol'] = 0.1
        data['sixteenth_duration'] = 150
        data['swing'] = False
        data['beat_pattern'] = [
                                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            
                                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            
                                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
                              ]
        with open('test.drum', 'w') as outfile:
            json.dump(data, outfile)
            
        self.assertFalse(utils.is_valid_file('test.drum'))
        os.remove('test.drum')
        
    def test_correct_pattern(self):
        data = {}
        data['sixteenth_per_beat'] = 4
        data['beats_per_bar'] = 4
        data['num_bars'] = 1
        data['sixteenth_duration'] = 150
        data['swing'] = False
        empty = [
                                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            
                                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            
                                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                                  
                                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                                  
                                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                                  
                                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
                              ]
        data['beat_pattern'] = [empty, empty, empty, empty]
        data['swing_amount'] = 0.3
        data['is_active'] = [1,1,1,1,1,1]
        with open('test.drum', 'w') as outfile:
            json.dump(data, outfile)
            
        self.assertTrue(utils.is_valid_file('test.drum'))
        os.remove('test.drum')

from typing import Set, Any

import skrf as rf
import matplotlib.pyplot as plt
import numpy as np
import re
import sys
import pysp2
import scipy.signal as sig
from collections import defaultdict


class S2p(object):
    def read_list_of_pass_band_frequencies_from_text_file(self, file_name):
        with open(file_name, "r") as f:
            lines = f.readlines()
        lines = [float(string) for string in lines]
        return sorted(list(set(lines)))

    def is_filter_good(self, title, low_db, high_db):
        print(f"\n\n============ {title} ===========")
        good = 1
        if "PASS_BAND" in title:
            list_of_frequencies = self.pass_band_frequencies
            frequency_db_dict = self.pass_band_frequency_db_dict

        for freq in list_of_frequencies:
            print('is_filter_good?:', self.s2p_file, ' Frequency:', freq, ':db=', frequency_db_dict[freq], 'Expected db range', low_db, high_db)
            if low_db < frequency_db_dict[freq] < high_db:
                good = 1
            else:
                good = 0
                print('is_filter_good?:', self.s2p_file, ' NO:  Frequency:', freq, ':db=', frequency_db_dict[freq], 'Expected db range', low_db, high_db)
                break
        print(self.s2p_file, " is good in ", title, "  ", good)
        return good

    def extract_frequencies_db_in_band(self, left, right):
        print('-------- extract_frequencies_db_in_band', left, right)
        frequency_db_dict = defaultdict(float)
        for s21_db_value, frequency_value in zip(self.s21_db, self.frequencies):
            frequency_value_only = float(re.sub('-.*', '', str(frequency_value)))
            s21_db_value = float(str(s21_db_value).replace('[', '').replace(']', ''))
            # if len(frequency_value_only) > 1:
            if left < frequency_value_only < right:
                print(f'{self.s2p_file}:: {frequency_value_only}  {s21_db_value}')
                frequency_db_dict[frequency_value_only] = s21_db_value
        return frequency_db_dict

    def __init__(self, s2p_file='x6.s2p'):
        self.pass_band_low = 6.25
        self.pass_band_high = 6.75
        self.stop_band_left_low = 5.4
        self.stop_band_left_high = 5.7
        self.stop_band_right_low = 7.3
        self.stop_band_right_high = 7.6

        self.s2p_file = s2p_file
        self.network = rf.Network(self.s2p_file)
        self.s21_db = self.network.s21.s_db
        self.frequencies = self.network.frequency

        self.pass_band_frequencies = self.read_list_of_pass_band_frequencies_from_text_file("pass_band_frequencies")
        self.pass_band_frequency_db_dict = self.extract_frequencies_db_in_band(self.pass_band_low, self.pass_band_high)

        self.stop_band_left_frequency_db_dict = self.extract_frequencies_db_in_band(self.stop_band_left_low, self.stop_band_left_high)
        self.stop_band_right_frequency_db_dict = self.extract_frequencies_db_in_band(self.stop_band_right_low, self.stop_band_right_high)



class Spacex(object):
    def read_all_sp2_files(self, file_name):
        with open(file_name, "r") as f:
            lines = f.readlines()
            lines = [string.strip() for string in lines]
        return sorted(list(set(lines)))

    def __init__(self):
        self.pass_band_high_db_threshold = 0
        self.pass_band_low_db_threshold = -20
        # Assume yield to be 0
        filters_processed = 0

        # Read the filenames of all sp2 files to be analyzed
        all_s2p_files = self.read_all_sp2_files("all_s2p_files")
        # Create a list of all s2p objects
        self.all_s2p_objects = []
        for s2p_file in all_s2p_files:
            self.all_s2p_objects.append(S2p(s2p_file))
            # good_pass_band_filters += S2p(s2p_file).is_filter_good('PASS_BAND', self.pass_band_low_db_threshold, self.pass_band_high_db_threshold)
            filters_processed += 1
        # Find yield for few db thresholds
        for low_db_threshold_increment in range(20):
            good_pass_band_filters = 0
            low_db_threshold = self.pass_band_low_db_threshold - low_db_threshold_increment
            for s2p_object in self.all_s2p_objects:
                good_pass_band_filters += s2p_object.is_filter_good('PASS_BAND', low_db_threshold, self.pass_band_high_db_threshold)
            print('Low_db_threshold=', low_db_threshold, '  Number of filters processed=', filters_processed, ' good_pass_band_filters=', good_pass_band_filters, '  Yield=', 100*good_pass_band_filters/filters_processed)
            print('\n\n')


if __name__ == "__main__":
    x = Spacex()

import skrf as rf
import matplotlib.pyplot as plt
import numpy as np
import pysp2
import scipy.signal as sig


class Spacex(object):
    def __xinit__(self):
        # Read the .s2p file
        data = np.loadtxt('Measurement_00076.s2p', delimiter=',')

        # Get the frequency and S21 data
        freq = data[:, 0]
        s21 = data[:, 1]

        # Find the stopband frequencies
        stopband_start = 1e9
        stopband_end = 10e9
        stopband_freq = freq[(freq >= stopband_start) & (freq <= stopband_end)]

        # Calculate the stopband power
        stopband_power = np.sum(np.abs(s21[freq >= stopband_start]) ** 2)

        # Print the stopband powgeter
        print('Stopband power:', stopband_power)

        # Plot the S21 data
        plt.plot(freq, s21)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('S21 (dB)')
        plt.show()

    def __xinit__(self):
        # Create a frequency object
        freq = rf.Frequency(start=1e9, stop=10e9, npoints=1001)

        # Print the frequency in dB
        print(freq.f_db)


    def __xinit__(self):
        print("Initializing spacex")
        network = rf.Network('Measurement_00076.s2p')

        #pass_band = network.get_passband()
        #stop_band = network.get_stopband()
        #print(pass_band)
        #print(stop_band)

        # Print the network parameters
        # print(network.s)

        # Plot the network parameters
        network.plot_s_mag()

        line = rf.Network('Measurement_00076.s2p')
        #print('S-parameters=', line,'\n\n')
        self.filter_regions(network)
        line.plot_s_db()
        # plt.show()

        # Get the frequency response of the filter
        # s_params = network.s
        # Plot the passband of the filter
        # network.plot_s_db(m=0, n=0, marker='o')
        network.plot_s_complex()
        print(network)
        # Show the plot
        plt.show()

    def filter_regions(self, network, minimum=-3, maximum=-30, *, offset=0.0):
        data = np.where(np.logical_and(network.s_db <= minimum + offset, maximum + offset < network.s_db))[0]
        sequences = np.split(data, np.array(np.where(np.diff(data) > 1)[0]) + 1)

        ranges = []
        for seq in sequences:
            if len(seq) > 1:
                if np.ptp([minimum, maximum]) * 0.95 < np.ptp(network[np.min(seq):np.max(
                        seq)].s_db):  # only select regions that are at least 95% of wanted np.ptp
                    ranges.append((np.min(seq), np.max(seq)))  # spans of points
            else:
                ranges.append(seq[0])  # single point
        print(ranges)
        return ranges  # ranges are [(start stop),] in terms of data points


if __name__ == "__main__":
    x = Spacex()
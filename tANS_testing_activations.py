import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math

# import my tANS function
from Functions import Coder, Utils, CompTensor

d = 'trace/mobilenet_v2/'

range_ = (1,7)

# importing the symbol table
print("Importing symbol tables")

s_tabs = [ pd.read_csv(f"{d}input_{i}_flat.apack", sep = " ", header = None) for i in range(range_[0],range_[1])]

for s_tab in s_tabs:            
    s_tab.columns = ["vmin","OL","abits","obits","vcnt"]

# importing the data
print("Importing data")
data = [np.load(f"{d}input_{i}.npy") for i in range(range_[0],range_[1])]

# converting each data point to a symbol, offset pair
print("Converting data to CompTensors")

comp_tensors = []
for i, dat in enumerate(data):
    print(f"\tProcessing data {i}")
    comp_tensors.append([CompTensor.CompTensor(d,s_tabs[i]) for d in dat])

# Getting freqs, must be a power of 2
print("Getting frequencies APack")
freqs = []

for s_tab in s_tabs:
    # Get frequencies from the symbol table
    freq = list(s_tab.vcnt)

    # rescale so the sum of freq is 2**10, this ensures the Coder works effieciently
    # before I was just rescaling to the most accurate power of 2, but the coder would time out
    # building the object
    # Note: the rescale_list_to_power_of_2 function ensures that the sum of the list is a power of 2
    #       and also that no element is zero (bumps up the smallest elements to 1)
    freq = Utils.rescale_list_to_power_of_2(freq, 2**10)
    
    # append to freqs
    freqs.append(freq)
    
# offsets
def int_to_binary_list(value, nbits):
    if value >= 2**nbits or value < 0:
        raise ValueError(f"Value {value} cannot be represented in {nbits} bits.")
    
    binary_list = [int(bit) for bit in bin(value)[2:].zfill(nbits)]
    return binary_list

# make offset bitstream for one tensor

offset_stream = []

for i in range(len(comp_tensors)):
    offset_stream.append([])
    for j in range(len(comp_tensors[i])):
        offset_stream[i].append([])
        for k in range(len(comp_tensors[i][j].points)):
            offset_stream[i][j].extend(int_to_binary_list(comp_tensors[i][j].points[k].off, comp_tensors[i][j].points[k].OL))
            
import time
print("Compressing Activations APack")
nbits = 8 # takes 4 bits to represent each symbol

all_run_times = []
all_build_times = []
all_comp_ratios = []
all_bps = []

for i in range(len(freqs)):
    print(f"\tCompressing Layer {i}")

    run_times = []
    build_times = []
    comp_ratios = []
    bp_sym = []

    for j in range(len(comp_tensors[i])):
        print(f"\t\tCompressing tensor {j}")
        
        # compressing the symbols
        time_start = time.time()
        
        c = Coder.Coder(sum(freqs[i]), [i for i in range(len(freqs[i]))], freqs[i], fast = False)
        
        time_end = time.time()
        build_time_taken = time_end - time_start

        msg = [p.symbol for p in comp_tensors[i][j].points]

        time_start = time.time()
        out, comp_bits = c.encode_decode(msg)
        time_end = time.time()
        run_time_taken = time_end - time_start
        
        # factoring in the offset bits  
        total_comp_bits = comp_bits + len(offset_stream[i][j])

        if out != msg:
            print("Error in encoding and decoding")
            break
        
        run_times.append(run_time_taken)
        build_times.append(build_time_taken)
        comp_ratios.append(len(msg) * nbits / total_comp_bits)
        bp_sym.append(total_comp_bits / len(msg))
        
    # print average stats
    print("\t\tAverage run time taken: %f seconds" % np.mean(run_times))
    print("\t\tAverage build time taken: %f seconds" % np.mean(build_times))
    print("\t\tAverage compression ratio: %f" % np.mean(comp_ratios))
    print("\t\tAverage bits per symbol: %f" % np.mean(bp_sym))
    
    # add stats to all lists
    all_run_times.append(run_times)
    all_build_times.append(build_times)
    all_comp_ratios.append(comp_ratios)
    all_bps.append(bp_sym)
    
# display stats in a dataframe

freqs = freqs

stats_apack = pd.DataFrame({"Layer": [i for i in range(len(freqs))],
                      "Run Time": [np.mean(all_run_times[i]) for i in range(len(freqs))],
                      "Build Time": [np.mean(all_build_times[i]) for i in range(len(freqs))],
                      "Compression Ratio": [np.mean(all_comp_ratios[i]) for i in range(len(freqs))],
                      "Bits per Symbol": [np.mean(all_bps[i]) for i in range(len(freqs))]})

# save the stats to a csv file
stats_apack.to_csv(f"{d}stats_apack.csv", index = False)

# get average compressino ration
print("Average Compression Ratio Activations APack:", np.mean(stats_apack["Compression Ratio"]))

# Calculate frequency of each uint8 value
def calculate_frequency(array):
    # Ensure the input array is of type uint8
    if array.dtype != np.uint8:
        raise ValueError("Input array must be of type uint8")
    
    # Initialize an array of zeros with a length of 256 to store frequencies
    frequency = np.zeros(256, dtype=int)
    
    # Iterate through the array and count the occurrences of each value
    for value in array:
        frequency[value] += 1
        
    return frequency

freqs = [calculate_frequency(d) for d in data]

# rescale the frequencies to a power of 2
freqs = [Utils.rescale_list_to_power_of_2(freq, 2**10) for freq in freqs]
print(sum(freqs[0]))

import time
print("Compressing Activations 256")
nbits = 8 # takes 4 bits to represent each symbol

all_run_times = []
all_build_times = []
all_comp_ratios = []
all_bps = []

for i in range(len(freqs)):
    print(f"\tCompressing Layer {i}")

    run_times = []
    build_times = []
    comp_ratios = []
    bp_sym = []

    for j in range(len(data[i])):
        print(f"\t\tCompressing tensor {j}")
        
        time_start = time.time()
        
        c = Coder.Coder(sum(freqs[i]), [i for i in range(len(freqs[i]))], freqs[i], fast = False)
        
        time_end = time.time()
        build_time_taken = time_end - time_start

        msg = list(data[i][j].flatten())

        time_start = time.time()
        out, comp_bits = c.encode_decode(msg)
        time_end = time.time()
        run_time_taken = time_end - time_start

        if out != msg:
            print("Error in encoding and decoding")
            break
        
        
        run_times.append(run_time_taken)
        build_times.append(build_time_taken)
        comp_ratios.append(len(msg) * nbits / comp_bits)
        bp_sym.append(comp_bits / len(msg))
        
    # print average stats
    print("\t\tAverage run time taken: %f seconds" % np.mean(run_times))
    print("\t\tAverage build time taken: %f seconds" % np.mean(build_times))
    print("\t\tAverage compression ratio: %f" % np.mean(comp_ratios))
    print("\t\tAverage bits per symbol: %f" % np.mean(bp_sym))
    
    # add stats to all lists
    all_run_times.append(run_times)
    all_build_times.append(build_times)
    all_comp_ratios.append(comp_ratios)
    all_bps.append(bp_sym)
    
freqs = freqs

stats_256 = pd.DataFrame({"Layer": [i for i in range(len(freqs))],
                      "Run Time": [np.mean(all_run_times[i]) for i in range(len(freqs))],
                      "Build Time": [np.mean(all_build_times[i]) for i in range(len(freqs))],
                      "Compression Ratio": [np.mean(all_comp_ratios[i]) for i in range(len(freqs))],
                      "Bits per Symbol": [np.mean(all_bps[i]) for i in range(len(freqs))]})

# save 
stats_256.to_csv(f"{d}stats_256.csv", index = False)

# get average compressino ration
print("Average Compression Ratio Activations 256:", np.mean(stats_256["Compression Ratio"]))
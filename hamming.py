import copy
import random
import math
import sys


# Self explanatory, returns True if
#   x is a power of 2 and False otherwise
def is_pow_two(x):
    if x <= 0:
        return False
    x = int(x)
    if (math.log(x, 2) % 1 == 0):
        return True
    else:
        return False


# Pads a string of binary digits by 
#   prepending "0" to the string, as the MSB
# Does not change the value of the input
def pad_binary(bits, desired_number_of_bits):
    while len(bits) < desired_number_of_bits:
        bits = "0" + bits
    return bits


# Determine the positions of the parity bits
# These positions are all powers of 2 from
#   0 to total_bits (the input parameter)
def get_parity_positions(total_bits):
    parity_positions = []
    for i in range(total_bits):
        if is_pow_two(i):
            parity_positions.append(i)
    return parity_positions


# Get the indices that are covered by a parity
#   bit at position "position".
# This is also dependent on the total number
#   of bits
def bit_positions(position, total_bits):
    starts = range(position-1, total_bits, position*2)
    positions = []
    for start in starts:
        for i in range(position):
            positions.append(start+i)
    indexes = [i for i in positions if i < total_bits]
    return indexes


# Determine the number of parity bits required to
#   cover n data bits
def get_number_of_parity_bits(data_bits):
    n = data_bits
    k = 0
    while (2**k) - k -1 < n:
        k+=1
    return k


# Determine the maximum number of data bits that
#   can be fit into n bits, allowing
#   space for parity bits.
def get_number_of_data_bits(total_bits):
    data_bits = 0
    k = 0
    while data_bits+k < total_bits:
        data_bits += 1
        k = get_number_of_parity_bits(data_bits)
    return data_bits


# Create a dictionary mapping of
#   {parity_bit_index:[covered indexes]} pairs
# Keys are indexes and values are lists of indexes
def get_parity_bit_mapping(data_bits):
    parity_bit_map = dict()
    parity_bits = get_number_of_parity_bits(data_bits)
    total_bits = parity_bits + data_bits
    parity_positions = get_parity_positions(total_bits)
    for position in parity_positions:
        covered_indexes = bit_positions(position, total_bits)
        parity_bit_index = position-1
        parity_bit_map[parity_bit_index] = covered_indexes
    return parity_bit_map


# First step of algorithm, this essentially explodes
#   the data block into a dictionary that uses keys
#   to represent indexes and sets the values
#   to either 'p' to represent a parity bit or
#   an actual data bit
def expand(data_block):
    hamming_block = dict()
    n_data_bits = len(data_block)
    n_parity_bits = get_number_of_parity_bits(n_data_bits)
    n_total_bits = n_parity_bits+n_data_bits
    parity_bit_mapping = get_parity_bit_mapping(n_data_bits)
    i = 0
    for newi in range(n_total_bits):
        if newi in parity_bit_mapping:
            hamming_block[newi] = 'p'
            continue
        else:
            hamming_block[newi] = int(data_block[i])
            i += 1
            continue
    return hamming_block


# This is the second step of the algorith.
# It sets the values of the parity bits inside the exploded
#   data block according to Hamming's algorithm
def fill_parity_bits(hamming_block):
    n_data_bits = get_number_of_data_bits(len(hamming_block))
    parity_bit_mapping = get_parity_bit_mapping(n_data_bits)
    for (pindex, bits_to_check) in parity_bit_mapping.items():
        bits = [hamming_block[i] for i in bits_to_check if i != pindex]
        odd = sum(bits) % 2
        hamming_block[pindex] = odd
    return hamming_block


# Converts a dictionary of hamming bit values into a binary
#   string. This is possible because the key values are contiguous.
def dict_to_bin(hamming_block):
    binstr = ""
    for i in range(len(hamming_block)):
        binstr += str(hamming_block[i])
    return binstr


# Inverse of the dict_to_bin function, converts a binary string
#   into a dictionary of (index, bit) pairs
def bin_to_dict(binstr):
    hamming_block = dict()
    i = 0
    for b in binstr:
        hamming_block[i] = int(b)
        i+=1
    return hamming_block


# Check a series of bits for errors using the parity bits
# Returns the number of incorrect values, although the 
#   correct value is recoverable for a certain number
#   of bad bits, dependent on the number of parity bits
def check_hamming_dict(hamming_block):
    n_data_bits = get_number_of_data_bits(len(hamming_block))
    parity_bit_mapping = get_parity_bit_mapping(n_data_bits)
    bad_indexes = []
    for (pindex, bits_to_check) in parity_bit_mapping.items():
        bits = [hamming_block[i] for i in bits_to_check if i != pindex]
        correct_parity_bit = sum(bits) % 2
        input_parity_bit = hamming_block[pindex]
        if correct_parity_bit != input_parity_bit:
            bad_indexes.append(pindex+1)
    if not bad_indexes:
        return None
    else:
        return sum(bad_indexes)-1


# Fix a corrupted series of bits. This will work for
#   a certain number of bad bits depending on the number
#   of parity bits chosen.
def fix_hamming_dict(hamming_block):
    n_data_bits = get_number_of_data_bits(len(hamming_block))
    i = check_hamming_dict(hamming_block)
    if i == None:
        return hamming_block
    else:
        hamming_block_ = copy.deepcopy(hamming_block)
        hamming_block_[i] = int(not hamming_block[i])
        return hamming_block_


# Generate a dictionary of data bits and parity bits
#   from a binary string
def encode_hamming(binary):
    data_block = bin_to_dict(binary)
    expanded = expand(data_block)
    hamming_block = fill_parity_bits(expanded)
    return hamming_block


# This function is used for testing, it returns a corrupted version
#   of some existing hamming-encoded data. The data_bits_only flag
#   toggles whether the function should corrupt both data bits and
#   parity bits, or just data bits.
def generate_bad_hamming_dict(hamming_block, data_bits_only=False):
    n_data_bits = get_number_of_data_bits(len(hamming_block))
    parity_positions = get_parity_bit_mapping(n_data_bits).keys()
    data_positions = [i for i in range(len(hamming_block)) if i not in parity_positions]
    if data_bits_only == True:
        i = data_positions[random.randint(0, len(data_positions)-1)]
    else:
        i = random.randint(0, len(hamming_block)-1)
    hamming_block_ = copy.deepcopy(hamming_block)
    hamming_block_[i] = int(not hamming_block[i])
    return hamming_block_


# Converts raw bytes into a binary string
def bytes_to_binary(input_bytes, bits_per_byte):
    binary = ""
    for byte in input_bytes:
        binary += pad_binary(bin(ord(byte))[2:], bits_per_byte)
    return binary


# Converts raw bytes into a hamming-encoded binary string
# The scramble flag is used for testing purposes, and generates 
# corrupted, but reparable data.
def bytes_to_hamming_binary(input_bytes, bits_per_hamming_block, 
                            bits_per_input_byte, scramble=False):
    index = 0
    n_data_bits = get_number_of_data_bits(bits_per_hamming_block)
    full_hamming_binary = ""
    input_binary = bytes_to_binary(input_bytes, bits_per_input_byte)
    while index < len(input_binary):
        current_binary = input_binary[index:index+n_data_bits]
        current_hamming = encode_hamming(current_binary)
        if scramble == False:
            hamming_binary = dict_to_bin(current_hamming)
        else:
            bad_binary = generate_bad_hamming_dict(current_hamming, True)
            hamming_binary = dict_to_bin(bad_binary)
        full_hamming_binary += hamming_binary
        index += n_data_bits
    return full_hamming_binary


# Decode a hamming bit dictionary into a binary string. Returns
#   only data bits.
def decode_hamming(hamming_block):
    n_data_bits = get_number_of_data_bits(len(hamming_block))
    parity_bit_map = get_parity_bit_mapping(n_data_bits)
    binary = ""
    for i in range(len(hamming_block)):
        if i in parity_bit_map.keys():
            continue
        else:
            binary += str(hamming_block[i])
    return binary


# Decode a hamming-encoded binary string into a series of 
#   bytes representing the actual data.
def hamming_binary_to_bytes(hamming_binary, 
                            bits_per_hamming_block, 
                            autofix=True):
    index = 0
    output_bytes = ""
    while index < len(hamming_binary):
        current_binary = hamming_binary[index:index+bits_per_hamming_block]
        current_hamming = bin_to_dict(current_binary)
        if autofix == True:
            current_hamming_ = fix_hamming_dict(current_hamming)
        else:
            current_hamming_ = copy.deepcopy(current_hamming)
        decoded = decode_hamming(current_hamming_)
        byte = chr(int(decoded, 2))
        output_bytes+=byte
        index += bits_per_hamming_block
    return output_bytes


# Split the data and parity bits from hamming-encoded blocks
#   into a list of (data bits, parity bits) pairs. The
#   order of these bits is maintained, and the position
#   of them can be deduced via the general algorithm
# This function is not for normal use of the algorithm
# Also is home to an ungodly list comprehension, I'm just
#   too scared to try replace it with a proper loop
def split_hamming_binary(hamming_binary, bits_per_hamming_block):
    data_bits = get_number_of_data_bits(bits_per_hamming_block)
    parity_positions = get_parity_bit_mapping(data_bits).keys()
    blocks = [hamming_binary[start:start+bits_per_hamming_block] 
              for start in range(0, len(hamming_binary),
                                 bits_per_hamming_block)]
    split_blocks = []
    for block in blocks:
        parity_bits = ""
        data_bits = ""
        for index in range(len(block)):
            if index in parity_positions:
                parity_bits += block[index]
            else:
                data_bits += block[index]
        split_blocks.append((data_bits, parity_bits))
    return split_blocks


# Generate hamming binary data from an input string
#   provided as the first command-line argument
def run():
    if len(sys.argv) < 2:
        print("Usage: python3 %s input_string" % sys.argv[0])
        exit(1)
    input_string = sys.argv[1]
    bits_per_input_byte = 8
    n_parity_bits = get_number_of_parity_bits(bits_per_input_byte) 
    bits_per_hamming_block = n_parity_bits + bits_per_input_byte
    hamming_binary = bytes_to_hamming_binary(input_string,
                                             bits_per_hamming_block,
                                             bits_per_input_byte,
                                             scramble=True)
    print(hamming_binary)


if __name__ == "__main__":
    run()

import Decoder,Encoder

class Coder:
    def __init__(self, s_list, L_s, fast = False):
        """Initializes the coder

        Args:
            s_list (list): list of symbols in the message
            L_s (list): list of frequencies of the symbols
        """
        self.s_list = s_list
        self.L_s = L_s
        self.L = sum(L_s)
                        
        # initialize the decoding table
        self.decoding_table = Decoder.DecodeTable(self.L, s_list, L_s, fast= fast)
        
        # spread symbols using the spread function
        self.spread = self.decoding_table.symbol_spread
        
        # initialize the encoder
        self.encoder = Encoder.Encoder(self.L, s_list, L_s, self.spread)
        
    def encode(self, data):
        """Encodes the data using the encoder

        Args:
            data (list): a list of symbols to encode

        Returns:
            list: returns the final state in [0,L) and the bitstream
        """
        return self.encoder.encode(data)[1] - self.L, self.encoder.encode(data)[0], self.encoder.encode(data)[2]
    
    def decode(self, state, bitstream, orig_state):
        """Decodes the bitstream using the decoding table

        Args:
            state (int): the initial state of the decoding process
            bitstream (list): the bitstream to decode

        Returns:
            list: returns the decoded symbols
        """
        # note we reverse the decoded symbols since the bitstream is decoded in opposite order
        res = self.decoding_table.decode(state, bitstream, orig_state)
        res.reverse()
        return res
    
    @staticmethod
    def calculate_bits(number):
        if number == 0:
            return 1  # Special case for zero
        num_bits = 0
        while number:
            number >>= 1  # Right shift by 1 bit
            num_bits += 1
        return num_bits
    
    def encode_decode(self, data, verbose = False):
        """Encodes and decodes the data, and returns the decoded data

        Args:
            data (list): a list of symbols to encode and decode

        Returns:
            list: returns the decoded symbols
        """
        
        state, bitstream, orig_state = self.encode(data)
        res = self.decode(state, bitstream, orig_state)
        # if there is an error 
        if res != data:
            print("Error in encoding and decoding")
            
        # compute how many bits saved
        orig_bits = len(data) * Coder.calculate_bits(len(self.s_list))
        comp_bits = len(bitstream)
        
        if verbose:
            print("Original bits: %d, Compressed bits: %d, Saved: %d" % (orig_bits, comp_bits, orig_bits - comp_bits))
        
        return res, orig_bits - comp_bits
    
    def encode_decode_string(self, data):
        """Encodes and decodes the string data, and returns the decoded data

        Args:
            data (str): a string to encode and decode

        Returns:
            list: returns the decoded symbols
        """
        data_t = list(data)
        return "".join(self.encode_decode(data_t))
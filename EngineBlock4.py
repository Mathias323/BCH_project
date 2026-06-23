from OpenroadFec_3 import BCH_from_standard
from BlockMemoryClass5 import BlockMemory
import numpy as np



class EngineBlock_encoder:
    def __init__(self):
        self.fec=BCH_from_standard()

        self.B=16
        self.N=128                  #straight from standard, one half of a consituent codeword in bits
        self.G=2
        self.guardblocks=2*self.G
        self.amt_guardblocks=(self.N/self.B)*((self.N/self.B)+self.guardblocks+1)
        self.k=239
        self.parityamount=17


        #block logic
        self.bit_count=0
        self.big_block_input=np.zeros((32,111),dtype=np.uint8)
        self.big_block_output=np.zeros((32,128),dtype=np.uint8)

        self.r=0
        self.R=0
        self.c=0
        self.C=0

        #state matrix logic
        self.state_matrix=BlockMemory()
        
  

    def encode_block(self, block): #takes np.array(32,111) returns np.array(2,8,16,16)
        #for the 2 rows of big blocks, simply just follows
        #the "identifier quadruple" defined by k
        #page 45 right below figure 29
        starting_row=len(self.state_matrix.memory)
        new_rows=np.zeros((2,self.N // self.B, self.B, self.B), dtype=np.uint8)

        for R in range(starting_row, starting_row+2): 
            for r in range(self.B):
                memory_part=np.zeros(self.N,dtype=np.uint8)
                for k in range(self.N):
                    memory_part[k]=self.state_matrix.get_bit((R^1)-2*self.G-2*(self.N//self.B)+2*(k//self.B),(k//self.B),(k%self.B)^r,r)

                pre_encoded = np.concatenate((memory_part, block[(R-starting_row)*16 + r]))
                codeword=self.fec.encode_systematic_ending(pre_encoded)

                for k in range(self.N, self.N*2):
                    new_rows[R - starting_row, (k-self.N)//self.B, r, (k % self.B) ^ r] = codeword[k]

        self.state_matrix.shift_up(2)
        self.state_matrix.memory[-2:]=new_rows
        
        return new_rows
      
    
class EngineBlock_decoder:
    def __init__(self, iterations):
        self.fec=BCH_from_standard()

        self.iterations=iterations
        self.B=16
        self.N=128                  #straight from standard, one half of a consituent codeword in bits
        self.G=2
        self.guardblocks=2*self.G
        self.amt_guardblocks=(self.N/self.B)*((self.N/self.B)+self.guardblocks+1)
        self.k=239
        self.parityamount=17

        #block logic
        self.bit_count=0
        self.big_block_input=np.zeros((32,128),dtype=np.uint8)
        self.big_block_output=np.zeros((32,111),dtype=np.uint8)

        self.r=0
        self.R=0
        self.c=0
        self.C=0

        #state matrix logic
        self.state_matrixes=[]
        for i in range(self.iterations):
            self.state_matrixes.append(BlockMemory())

        self.blocks_seen = 0
        self.blocks_per_stage_latency = self.state_matrixes[0].rows // 2
        self.total_latency_blocks = self.iterations * self.blocks_per_stage_latency


        


    def decode_block(self, block): #takes np.array(2,8,16,16) returns np.array(32,111)

        starting_row=len(self.state_matrixes[0].memory)

        for state_matrix in self.state_matrixes:
            for R in range(starting_row, starting_row+2): 
                for r in range(self.B):
                    codeword=np.zeros(2* self.N, dtype=np.uint8)

                    for k in range(self.N):
                        codeword[k]=state_matrix.get_bit((R^1)-2*self.G-2*(self.N//self.B)+2*(k//self.B),(k//self.B),(k%self.B)^r,r)

                    for k in range(self.N, self.N*2):
                        codeword[k]=block[R - starting_row, (k - self.N) // self.B, r, (k % self.B) ^ r]

                    decoded = self.fec.decode_ending(codeword, True)

                    for k in range(self.N):
                        state_matrix.write_bit((R^1)-2*self.G-2*(self.N//self.B)+2*(k//self.B),(k//self.B),(k%self.B)^r,r,decoded[k])

                    for k in range(self.N, self.N*2):
                        block[R - starting_row, (k - self.N) // self.B, r, (k % self.B) ^ r]=decoded[k]

            out_block = state_matrix.memory[:2].copy()

            state_matrix.shift_up(2)
            state_matrix.memory[-2:] = block

            block = out_block

        decoded_rows = np.zeros((32, 111), dtype=np.uint8)

        for R in range(2):
            for r in range(self.B):
                row = R * self.B + r

                for i in range(self.k - self.N): 
                    decoded_rows[row, i] = block[R, i // self.B, r, (i % self.B) ^ r]


        self.blocks_seen += 1
        valid = self.blocks_seen > self.total_latency_blocks

        return decoded_rows, valid
           

def main():
    encoder = EngineBlock_encoder()
    decoder = EngineBlock_decoder(3)

    np.set_printoptions(threshold=np.inf)

    num_blocks = 150
    compare_blocks = 100
    bit_error_probability = 0.01

    inputs = [
        np.random.randint(0, 2, (32, 111), dtype=np.uint8)
        for _ in range(num_blocks)
    ]

    outputs = []

    injected_errors = 0
    injected_bits = 0

    for input_block in inputs:
        encoded = encoder.encode_block(input_block)

        noisy_encoded = encoded.copy()

        # 1% independent bit-flip chance on the encoded block
        error_mask = np.random.random(noisy_encoded.shape) < bit_error_probability
        noisy_encoded[error_mask] ^= 1

        injected_errors += np.count_nonzero(error_mask)
        injected_bits += noisy_encoded.size

        decoded, valid = decoder.decode_block(noisy_encoded)

        if valid:
            outputs.append(decoded)

    usable_blocks = min(compare_blocks, len(outputs), len(inputs))

    total_output_errors = 0
    total_output_bits = 0

    for i in range(usable_blocks):
        total_output_errors += np.count_nonzero(outputs[i] != inputs[i])
        total_output_bits += inputs[i].size

    channel_ber = injected_errors / injected_bits
    output_ber = total_output_errors / total_output_bits

    print("Target channel BER %:", bit_error_probability * 100)
    print("Actual injected channel BER %:", channel_ber * 100)
    print("Output BER %:", output_ber * 100)
    print("Compared blocks:", usable_blocks)
    print("Output bit errors:", total_output_errors)
    print("Output bits checked:", total_output_bits)

if __name__ == "__main__":
    main()






        
        





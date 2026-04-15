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
        

    def take_input(self, input): #unconfirmed
        for i in input:
            self.big_block_input[self.r][self.c+16*self.C]=i
            self.c+=1
            if self.c==16 or (self.C==6 and self.c==15):
                self.c=0
                self.r+=1
                if self.r==32:
                    self.r=0
                    self.C+=1
                    if self.C==7:
                        self.encode_block(self.big_block_input)
                        self.C=0    
                

    def encode_block(self, block): #unconfirmed
        starting_row=len(self.state_matrix.memory)
        new_rows=[]

        for R in range(starting_row, starting_row+2):
            for r in range(self.B):
                memory_part=[]
                for k in range(self.N):
                    memory_part.append(self.state_matrix.get_bit((R^1)-2*self.G-2*(self.N//self.B)+2*(k//self.B),(k//self.B),(k%self.B)^r,r))
                    print((R^1)-2*self.G-2*(self.N//self.B)+2*(k//self.B),(k//self.B),(k%self.B)^r,r)
                memory_part=np.array(memory_part,dtype=np.uint8)
                pre_encoded=np.concatenate((block[(R-starting_row)*16+r],memory_part))
                codeword=self.fec.encode_systematic(pre_encoded)

                new_single_row=[]
                for k in range(self.N,self.N*2):
                    new_single_row.append(codeword[16*((k-self.N)//self.B)+(k%self.B)^r])
                new_rows.append(new_single_row)
                print(new_single_row)

        new_rows=np.array(new_rows,dtype=np.uint8)
        new_rows = new_rows.reshape(2, 8, 16, 16)
        self.state_matrix.shift_up()
        self.state_matrix.memory[:-2]=self.state_matrix.memory[2:]
        self.state_matrix.memory[:2]=new_rows
        


        return self.big_block_output
    
    
    
class EngineBlock_decoder:
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
        

    def take_input(self, input): #unconfirmed
        for i in input:
            self.big_block_input[self.r][self.c+16*self.C]=i
            self.c+=1
            if self.c==16 or (self.C==6 and self.c==15):
                self.c=0
                self.r+=1
                if self.r==32:
                    self.r=0
                    self.C+=1
                    if self.C==7:
                        self.ship_input_block(self.big_block_input)
                        self.C=0    
                

    def ship_input_block(self, block): #unconfirmed
        memory_part=[]
        for i in range(len(block)):
            if i<16:
                odd=1
            else:
                odd=0
            for j in range(8):
                memory_part.append(self.state_matrix.read_block_col(odd+j*2,j,i%16))
            memory_array=np.concatenate(memory_part)
            info_part=block[i]

            combined=np.concatenate((info_part,memory_array))
            encoded=self.fec.encode_systematic(combined)
            self.big_block_output[i]=encoded[:128]
            memory_part=[]
        self.state_matrix.shift_up()
        
        print(self.big_block_output)
        return self.big_block_output
    


def main():
    engine=EngineBlock_encoder()
    np.set_printoptions(threshold=np.inf)
    for i in range(3552):
        engine.take_input(np.array([i%2],dtype=np.uint8))

if __name__ == "__main__":
    main()






        
        





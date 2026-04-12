from OpenroadFec_3 import BCH_from_standard
import numpy as np



class EngineBlock:
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
        self.state_matrix=np.zeros(((self.N//self.B)*16, (self.G*2+(self.N//self.B)+1)*16),dtype=np.uint8) # this comes out to be a 208x128 matrix, 128 per row because that is the codeword length, and 368 because of guard band etc
        print(((self.N//self.B)*16, (self.G*2+(self.N//self.B)+1)*16))
        

    def take_input(self, input):
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
                        self.ship_input_block()
                        self.C=0    
                

    def ship_input_block(self):
        #print(self.big_block_input)
        return None




engine=EngineBlock()
np.set_printoptions(threshold=np.inf)
for i in range(3552):
    engine.take_input(np.array([1],dtype=np.uint8))





        
        





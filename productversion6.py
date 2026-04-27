from OpenroadFec_3 import BCH_from_standard
import numpy as np


class productioncode:
    def __init__(self):
        self.encoder=BCH_from_standard()
        self.pre_encode_block=np.zeros((239,239),dtype=np.uint8)



    def take_input(self, input):
        pass

    def encode(self, block):
        temp=[]
        print("block shape 0" f"{block.shape}")
        for i in range(len(block)):
            temp.append(self.encoder.encode_systematic(block[i]))
        temp=np.array(temp)
        print("block shape 1" f"{temp.shape}")
        temp2=[]
        for j in range(len(temp[0])):
            temp2.append(self.encoder.encode_systematic(temp[:,j]))
        temp2=np.array(temp2)
        print("block shape 2" f"{temp2.shape}")
        return temp2



    def decode(self, block, iterations):
        pass



def main():
    product=productioncode()
    print(product.encode(product.pre_encode_block))

    
if __name__ == "__main__":
    main()
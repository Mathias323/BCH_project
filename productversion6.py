from OpenroadFec_3 import BCH_from_standard
import numpy as np


class productioncode:
    def __init__(self):
        self.bch=BCH_from_standard()
        self.pre_encode_block=np.zeros((239,239),dtype=np.uint8)
        self.input_count=0


    # def take_input(self, input):

    #     for i in range(len(input)):
    #         self.pre_encode_block[self.input_count//239][self.input_count%239]=input[i]

    #         if self.input_count==(239*239)-1:
    #             block=self.encode(self.pre_encode_block)
    #             self.encoded_blocks.append(block)

    #             self.input_count=0
    #         else:
    #             self.input_count+=1

            
       

    def encode(self, block):
        temp=[]

        for i in range(len(block)):
            temp.append(self.bch.encode_systematic_ending(block[i]))

        temp=np.array(temp)

        temp2=[]
        for j in range(len(temp[0])):
            temp2.append(self.bch.encode_systematic_ending(temp[:,j]))

        temp2=np.array(temp2).T

        return temp2



    def decode(self, block, iterations):
        temp=block.copy()
        for i in range(iterations):
            for j in range(len(block)):
                temp[:,j]=self.bch.decode_ending(temp[:,j],return_full=True)
            for k in range(len(block)):
                temp[k]=self.bch.decode_ending(temp[k],return_full=True)

        temp = temp[:239, :239]
        return temp


def main():
    product=productioncode()
    print(product.decode(product.encode(product.pre_encode_block),1))

    
if __name__ == "__main__":
    main()
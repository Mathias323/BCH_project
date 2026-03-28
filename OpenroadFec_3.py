import numpy as np

#This code aims to implement 1 enc_dec block from the OFEC coder block as outlined in figure 28 from the openroad standard.

##Bch decoder to a specified primitive polynomial and error correcting amount

class BCH_from_standard:
    def __init__(self):
        #The huge difference between this version and the version in part 2 is that this has the concrete numbers from the standard instead of variables.
        #

        self.t=2                                                                    #t is the amount of errors this code can correct
        self.r=8                                                                    #r is the degree of the primitive polynomial
        self.n=2**self.r-1                                                          #n is the codeword vectors length in bits
        self.g=np.array([1,1,0,0,0,1,1,0,1,1,1,1,0,1,1,0,1],dtype=np.uint8)         #g is the generator polynomial
        self.k=self.n-(len(self.g)-1)                                               #k is the uncoded data vectors length in bits
        

    
    def divide_polynomial(self, polynomial_a,polynomial_divider, fixed_length_remainder=False):
        #finds the remainder by xoring the generator polynomium alinged with the current bit index
        #returns the quotient as index 0 and returns remainder at index 1
        #the quotient is array is degree, deg_poly_a - deg_poly_divider, or 0, whichever is lowest
        #the remainder array is just equal to degree poly_a if it is lower than divider
        #or the remainder array is degree poly_divider -1 if deg_poly_a >= deg_poly_divider, or if fixed length is set to true then it is 0 padded to that degree aswell.
        #starting at msb, returns array length div degree -1 since the remainder will always be smaller than the divisor
        #i do not know how this works, consult the notes if you want to know the theory.
        a_deg=len(polynomial_a)-1
        div_deg=len(polynomial_divider)-1

        temp_remainder=np.copy(polynomial_a)
        temp_quotient=np.zeros(max(0,(a_deg - div_deg) + 1), dtype=np.uint8) #the max() here just lets you put  deg_a < deg_divider into the function

        for i in range(a_deg, div_deg-1, -1):
            if temp_remainder[i]==1:
                temp_quotient[i- div_deg] = 1
                temp_remainder[i-div_deg:i+1]=np.bitwise_xor(temp_remainder[i-div_deg:i+1],polynomial_divider)

        if fixed_length_remainder and (a_deg<(div_deg-1)):
            pad_needed=div_deg-len(temp_quotient)
            pad=np.zeros(pad_needed,dtype=np.uint8)
            temp_remainder=np.concatenate((temp_remainder,pad))

        return temp_quotient, temp_remainder[:div_deg]


    def encode_systematic(self, message): 
        #this encode the message by shifting the message by the amount of redundancy bits (generator length -1)
        #and then adding the remainder of the message divided by the generator polynomial (the padding makes it so those digits are 0)
        #thereby making the remainder will be 0, which gives the error correcting ability through linearity
        if len(message) != self.k:
            raise ValueError(f"Message must have length {self.k}")
        if not isinstance(message, np.ndarray):
            raise ValueError("Message must be a numpy array")
        
        padding=np.zeros(len(self.g)-1,dtype=np.uint8)
        message_padded=np.concatenate((padding,message)) #shifts the message by appending 0's to equal to the amount of space the remainder will take
        remainder=self.divide_polynomial(message_padded,self.g)[1] #calculates the remainder
        message_padded[0:len(remainder)]=remainder #sets the padded 0's to the remainder

        parity_bit = np.array([np.bitwise_xor.reduce(message_padded)], dtype=np.uint8) #np.bitwise_xor.reduce xor's through the vector
        final_message = np.concatenate((message_padded, parity_bit))

        return final_message
    


    def random_message(self, length):
        #generates a message that consists of randomly chosen 1s and 0s of specified length. 
        return np.random.randint(0, 2, length, dtype=np.uint8)
    



    #unuseable for now
    # def test_messages(self, amount, amount_errors):
    #     for j in range(amount):
    #         mess=self.random_message(self.k)
    #         encoded_mess=self.encode_systematic(mess)
    #         for i in range(amount_errors):
    #             encoded_mess[np.random.randint(0,self.n)]^=1
    #         decoded=self.bch_decode(encoded_mess)
    #         if not np.array_equal(mess,decoded):
    #             return False
    #         print("decoded", j)
    #     return True
    



#primitive_polynomial=np.array([1,1,0,0,1]) #primal polynomial 1+x+x^4
encoder=BCH_from_standard()
print(encoder.encode_systematic(encoder.random_message(encoder.k)))
#print(encoder.test_messages(100, 2))


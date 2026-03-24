import numpy as np

#Initial build of a block code using a primitive polynomial, it was build mainly to understand the fundamentals
#it has 2 different encoding/decoding versions, 1 that is based on simple algebra.
#and the second version that is systematic, meaning that the message is visible as plaintext in the codeword
#this is an improvement both for slightly more simply decoding, and especially for bugfixing and clarity.

class BCH_basic:
    def __init__(self, polynomial, error_correcting_amount):
        if not isinstance(polynomial, np.ndarray):
            raise ValueError("Polynomial must be a numpy array")
        if not isinstance(error_correcting_amount, int):
            raise ValueError("error_correcting_amount must be a int")
        
        self.polynomial=polynomial
        self.error_correcting_amount=error_correcting_amount


        self.r=len(polynomial)-1                                                     #r is the degree of the primitive polynomial
        self.n=2**self.r-1                                                           #n is the codeword vectors length in bits
        self.g=self.get_generator(self.polynomial,self.error_correcting_amount)      #g is the generator polynomial
        self.k=self.n-(len(self.g)-1)                                                #k is the uncoded data vectors length in bits
        self.syndrome_box=self.gen_syndrome_box()


    def gen_syndrome_box(self):
        identity_matrix=np.identity(self.n,dtype=int)
        syndrome_box=np.zeros((self.n,len(self.g)-1),dtype=int) 
        for i in range(self.n):
            syndrome_box[i]=self.divide_polynomial(identity_matrix[i],self.g)[1]
        print(syndrome_box)
        return syndrome_box


    def multiply_polynomial_unbounded(self, polynomial_a,polynomial_b): #multiplies 2 polynomials, expanding it to size of a plus size b minus 1
        temp_polynomial=np.zeros((len(polynomial_a)+len(polynomial_b)-1),dtype=int)
        for i in range(len(polynomial_a)):
            if polynomial_a[i]==1:
                temp_polynomial[i:len(polynomial_b)+i]=np.bitwise_xor(temp_polynomial[i:len(polynomial_b)+i],polynomial_b)
        return temp_polynomial
    

    def divide_polynomial(self, polynomial_a,polynomial_divider): 
        #finds the remainder by xoring the generator polynomium alinged with the current bit index
        #returns the quotient as index 0 and returns remainder at index 1
        #starting at msb, returns array length div degree -1 since the remainder will always be smaller than the divisor
        #i do not know how this works, consult the notes if you want to know the theory.
        a_deg=len(polynomial_a)-1
        div_deg=len(polynomial_divider)-1

        temp_remainder=np.copy(polynomial_a)
        temp_quotient=np.zeros(a_deg - div_deg + 1, dtype=int)

        for i in range(a_deg, div_deg-1, -1):
            if temp_remainder[i]==1:
                temp_quotient[i- div_deg] = 1
                temp_remainder[i-div_deg:i+1]=np.bitwise_xor(temp_remainder[i-div_deg:i+1],polynomial_divider)
        return (temp_quotient,temp_remainder[:div_deg])


    def get_generator(self, primitive,  error_correcting_amount):
        if error_correcting_amount==1:
            return primitive
        else:
            pass
        

    def encode_systematic(self, message): # takes message and shifts it by appending 0's, then calculates what those 0's should be in order for the remainder to be 0
        if len(message) != self.k:
            raise ValueError(f"Message must have length {self.k}")
        if not isinstance(message, np.ndarray):
            raise ValueError("Message must be a numpy array")
        
        padding=np.zeros(len(self.g)-1,dtype=int)
        message_padded=np.append(padding,message)
        remainder=self.divide_polynomial(message_padded,self.g)[1]
        message_padded[0:len(remainder)]=remainder

        return message_padded

    def decode_systematic(self, codeword):  #decode via a simple algebraic rule, and can corrects 1 error via to the linearity of syndrome function
        message, syndrome=self.divide_polynomial(codeword,self.g)
        if np.all(syndrome == 0):
            return codeword[self.n-self.k:self.n+1]
        for i in range(len(self.syndrome_box)):
            if np.array_equal(syndrome,self.syndrome_box[i]):
                codeword[i]^=1
                return codeword[self.n-self.k:self.n+1]
        return "message for sure is errored" #doesnt really happen if you try to error correct.
    
    def encode(self, message): # takes message and multiplies it by the generator, there is no reduction, since we know it wont go out of bounds
        if len(message) != self.k:
            raise ValueError(f"Message must have length {self.k}")
        if not isinstance(message, np.ndarray):
            raise ValueError("Message must be a numpy array")
        
        return self.multiply_polynomial_unbounded(message,self.g)
    

    def decode(self, codeword):  #decode via a simple algebraic rule, and can corrects 1 error via to the linearity of syndrome function
        message, syndrome=self.divide_polynomial(codeword,self.g)
        if np.all(syndrome == 0):
            return message
        for i in range(len(self.syndrome_box)):
            if np.array_equal(syndrome,self.syndrome_box[i]):
                codeword[i]^=1
                return self.divide_polynomial(codeword,self.g)[0]
        return "message for sure is errored" #doesnt really happen if you try to error correct.
    

    def random_message(self, length): # just for testing
        return np.random.randint(0, 2, length, dtype=int)

primitive_polynomial=np.array([1,1,0,0,1]) #primal polynomial 1+x+x^4



## Just testing down here ####
primitive_polynomial = np.array([1,0,0,1,0,0,0,1], dtype=int)
primitive_polynomial=np.array([1,1,0,0,1]) #primal polynomial 1+x+x^4
encoder=BCH_basic(primitive_polynomial,1)
#print("r =", encoder.r)
#print("n =", encoder.n)
#print("g =", encoder.g)
#print("k =", encoder.k)

mess=encoder.random_message(11)
encoded_mess=encoder.encode_systematic(mess)

print(mess)
print(encoded_mess)
encoded_mess[2]^=1
decoded=encoder.decode(encoded_mess)
print(decoded)
print(np.array_equal(mess,decoded))
#print(decoded,mess,np.array_equal(decoded,mess))


 
import numpy as np

#this code aims to attain a better understanding of BCH codes, Mainly a construction based on theory and 

##Bch decoder to a specified primitive polynomial and error correcting amount
## still needs a lot of refinement, especially with cleaning up readability

class BCH_actual:
    def __init__(self, polynomial, error_correcting_amount):
        if not isinstance(polynomial, np.ndarray):
            raise ValueError("Polynomial must be a numpy array")
        if not isinstance(error_correcting_amount, int):
            raise ValueError("error_correcting_amount must be a int")
        

        #constants that are straight from theory
        self.polynomial=polynomial                                                  #p is the primitive polymonial that defines the finite field
        self.t=error_correcting_amount                                              #t is the amount of errors this code can correct
        self.r=len(polynomial)-1                                                    #r is the degree of the primitive polynomial
        self.n=2**self.r-1                                                          #n is the codeword vectors length in bits
        self.g=self.get_generator(self.t)                                           #g is the generator polynomial
        self.k=self.n-(len(self.g)-1)                                               #k is the uncoded data vectors length in bits

        #constants that are used heavily in the coding
        self.field_element_len=len(self.polynomial)-1                                  #the length of a np.array containing a field element
        self.field_elements=self.get_field_elements()                                  #an array of all the field elements 
        self.field_element_0=np.zeros(self.field_element_len,dtype=np.uint8)           #the field element that is all 0's, not included in the rotation.
        self.field_elements_amount=2**(self.field_element_len)-1                       #the amount of field elements


    def multiply_polynomial_unbounded(self, polynomial_a  ,polynomial_b):
        #Takes two 1d np.arrays of any size, and returns a 1d array of size a + b -1
        #multiplies 2 bit polynomials.
        temp_polynomial=np.zeros((len(polynomial_a)+len(polynomial_b)-1),dtype=np.uint8)
        for i in range(len(polynomial_a)):
            if polynomial_a[i]==1:
                temp_polynomial[i:len(polynomial_b)+i]=np.bitwise_xor(temp_polynomial[i:len(polynomial_b)+i],polynomial_b)
        return temp_polynomial

    def divison_in_field(self, element_a,element_divider):
        #takes two field elements and returns a field element
        #it does this by subtracting the dividers power from the base and modulating to keep it within the scope of the amount of field elements
        #this works because the elements cycle.
        matches = np.all(self.field_elements == element_a, axis=1)
        element_degree_a = np.where(matches)[0]
        if len(element_degree_a) == 0:
            return self.field_element_0
        else:
            element_degree_a = element_degree_a[0]

        matches = np.all(self.field_elements == element_divider, axis=1)
        element_degree_divider = np.where(matches)[0]
        if len(element_degree_divider) == 0:
            raise ValueError ("divison by 0 in divison_in_field")
        else:
            element_degree_divider = element_degree_divider[0]

        return self.field_elements[(element_degree_a-element_degree_divider)%self.field_elements_amount]

    
    def multiply_polynomial_bounded(self, polynomial_a,polynomial_b):
        #multiplies 2 field elements, returning a field elemetn
        #it does this simply by summing their power and modulating to keep it within the scope of the amount of field elements
        #this works because the elements cycle.
        matches = np.all(self.field_elements == polynomial_a, axis=1)
        a_degree = np.where(matches)[0]
        if len(a_degree) == 0:
            return self.field_element_0
        else:
            a_degree = a_degree[0]
        matches = np.all(self.field_elements == polynomial_b, axis=1)
        b_degree = np.where(matches)[0]
        if len(b_degree) == 0:
            return self.field_element_0
        else:
            b_degree = b_degree[0]

        return self.field_elements[(a_degree+b_degree)%self.field_elements_amount]
    
    

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


    def get_generator(self,error_correcting_amount): ##### this is pretty much garbage, it works but has tons of possible improvments both coding and theory wise.
        # oh and also this is almost always just straight up pulled from a standard, so this function is pretty much for fun.
        if error_correcting_amount==1:
            return self.polynomial
        else:
            #what we need is another polynomium that when divided by primitive has a remainder=0, but p(x)^2 ect doesnt directly work i dont recall why consult notes guess
            #what we do to get it is guess on a polynomium then we calculate the remainder, and if it is 0 or has only powers of x^3 then it works
            p_len=len(self.polynomial)
            partial_generator_list=np.zeros((self.t,p_len),dtype=np.uint8)
            partial_generator_list[0]=self.polynomial
            for j in range(0,self.t-1):
                remainder_list=np.zeros((p_len,p_len-1),dtype=np.uint8)# this should after the loop be a list of the possible remainders for my monomonials 
                #of power x^1+2j, which the remainders should have length deg_prim, and there should be amount deg_prim+1 so it max has the same amount of
                #components as the original primitve, due to matrix math w/e w/e linear space etc that should mean it can always hit 0 with that amount of
                #different remainders
                for i in range(p_len):
                    power=i*(3+2*j)
                    monomial = np.zeros(power + 1, dtype=np.uint8)
                    monomial[power] = 1
                    remainder_list[i]=(self.divide_polynomial(monomial,self.polynomial,True)[1]) 
                print("the remainder list going into can_hit_0")
                print(remainder_list) 
                partial_generator_list[j+1]=self.can_hit_0(remainder_list)

            actual_gen=self.polynomial
            for i in range(1,len(partial_generator_list)):
                actual_gen=self.multiply_polynomial_unbounded(actual_gen,partial_generator_list[i])
            return actual_gen


            
    def can_hit_0(self, poly_list): #checks for a valid p_3,p_5 etc, by finding a nontrivial solution to hit the 0 vector.
        #an extension of get_generator function, therefore also just for fun.
        list_len=len(poly_list)
        duration=2**list_len

        comp_poly=np.zeros(len(poly_list[0]),dtype=np.uint8)
        for i in range(1,duration):
            temp_poly=np.zeros(len(poly_list[0]),dtype=np.uint8)
            for j in range(list_len):
                if (i>>j) & 1:
                    temp_poly=np.bitwise_xor(temp_poly,poly_list[j])
            if np.array_equal(comp_poly,temp_poly):
                p_next = np.zeros(list_len, dtype=np.uint8)
                for j in range(list_len):
                    p_next[j] = (i >> j) & 1
                return p_next
        raise ValueError("No combination hit zero")


    def encode_systematic(self, message): 
        #this encode the message by shifting the message by the amount of redundancy bits (generator length -1)
        #and then adding the remainder of the message divided by the generator polynomial (the padding makes it so those digits are 0)
        #thereby making the remainder will be 0, which gives the error correcting ability through linearity
        if len(message) != self.k:
            raise ValueError(f"Message must have length {self.k}")
        if not isinstance(message, np.ndarray):
            raise ValueError("Message must be a numpy array")
        
        padding=np.zeros(len(self.g)-1,dtype=np.uint8)
        message_padded=np.append(padding,message) #shifts the message by appending 0's to equal to the amount of space the remainder will take
        remainder=self.divide_polynomial(message_padded,self.g)[1] #calculates the remainder
        message_padded[0:len(remainder)]=remainder #sets the padded 0's to the remainder
        return message_padded
    


    def get_field_elements(self): #simply gets all the field elements defined by the primitive polynomial upon initialization
        field_elements=np.zeros(((2**(self.field_element_len))-1,self.field_element_len),dtype=np.uint8) # will be a list of every single field element, or x^n, # doesnt contain the 0 element
        field_elements[0]=np.concatenate((np.array([1],dtype=np.uint8),np.zeros(self.field_element_len-1,dtype=np.uint8))) # first entry is just x^0
        append_0=np.array([0],dtype=np.uint8)  #i couldnt find an easy way to just shift right and bitmask in np
        for i in range(1,len(field_elements)):
            field_elements[i]=self.divide_polynomial(np.concatenate((append_0,field_elements[i-1]))[:self.field_element_len+1],self.polynomial)[1]
        #print(field_elements, "field elements")
        return field_elements
    

    
    def gen_syndrome_box(self,codeword): #runs at start to generate the syndrome array # which is a np array with error_correcting_amount*2 entries
        #each being length deg_primitive.
        syndrome_box=np.zeros((self.t*2,self.field_element_len),dtype=np.uint8)

        for i in range(self.t*2): #fills the syndrome box with the codeword syndrome equal to the codeword(x^(i+1))
            temp_syndrome=self.field_element_0
            for j in range(len(codeword)):
                if codeword[j]==1:
                    #print("it enters", i, j)
                    #print(temp_syndrome)
                    temp_syndrome=np.bitwise_xor(temp_syndrome,self.field_elements[(j*(i+1))%self.field_elements_amount])
            #print(temp_syndrome, "this gets added")
            syndrome_box[i]=temp_syndrome
        return syndrome_box
        

    def berlekamp_massey(self, syndrome_box): ######!!!! disclaimer: i dont really fully understand this algorithm so the comments may be misleading !!!######
        ## this algorithm itteratively finds the locator polynomial which is 
        ##a(x)=L[i]*x^i e.g. it has field elements as coefficients, and also takes field elements as x. its degree should be equal to the amount of errors.

        one = self.field_elements[0] #this is the element x^0
        c_x = np.zeros((2*self.t + 1, self.field_element_len), dtype=np.uint8) #this is an array of coefficients.
        c_x[0] = one

        b_x = np.zeros((2*self.t + 1, self.field_element_len), dtype=np.uint8) #b is just a placeholder for our previous guess, since we need a buffer.
        b_x[0] = one

        L=0 #is the degree of our current locator polynomial.
        m=1 #this is a counter of how many iterations since last major update to c_x
        b=self.field_elements[0] #this is the last nonzero discrepancy.

        for i in range(2*self.t):
            d=np.copy(syndrome_box[i])
            for j in range(1,L+1): # this loops calculates how good the the current c_x explains the the syndrome sequence.
                temp=self.multiply_polynomial_bounded(c_x[j],syndrome_box[i-j])
                d=np.bitwise_xor(d,temp)

            if np.all(d == 0): #this if statement essentially says, if the difference we calculate is 0, then the locator currently works for
                #the syndromes that we have calulated, and we move onto the next syndrome.
                m += 1
            else:
                t_x = np.copy(c_x) #saves a temporary copy of our current polynomial c_x while we modify it.
                factor = self.divison_in_field(d, b) #this finds the element that will cancel out the current discrepency
                for j in range(len(b_x)):
                    if j + m < len(c_x):
                        temp = self.multiply_polynomial_bounded(factor, b_x[j])
                        c_x[j + m] = np.bitwise_xor(c_x[j + m], temp)  
                        #this whole loop corrects a coefficient in our current polynomial, by finding the right index and then 
                        #incorporating the factor that we calculated right before.
                if 2 * L <= i:  #this checks if the need another degree to explain the locator polynomial.
                    L = i + 1 - L
                    b_x = t_x
                    b = np.copy(d)
                    m = 1
                else:
                    m += 1
        return c_x[:L+1]


    def chien_search(self, error_locating_polynomium):
        #Simply brute force looks for roots to the polynomial a(x)=L[i]*x^i where both L[i] and x^i are field elements
        #in more plain terms, it plugs each field element (as x) into the equation untill it equals the 0 element.
        error_pos=[]
        locator_len=len(error_locating_polynomium)
        for i in range(len(self.field_elements)):
            temp=error_locating_polynomium[0]
            for j in range(1,locator_len):
                #temp_a=self.field_elements[(i*j)%(2**((len(self.polynomial)-1))-1)]
                temp_a=self.field_elements[((self.n - i) * j) % self.n]
                temp_other=self.multiply_polynomial_bounded(error_locating_polynomium[j],temp_a)
                temp=np.bitwise_xor(temp,temp_other)

            if np.array_equal(temp,self.field_element_0):
                error_pos.append(i)
        return error_pos



    def bch_decode(self, codeword):
        #simply uses the previous functions in correct order to restore a codeword(if it detects errors)
        #and then pulls out the message that is just slicing due to the systematic encoding function
        message, syndrome=self.divide_polynomial(codeword,self.g)

        syndrome_box=self.gen_syndrome_box(codeword)

        message, syndrome=self.divide_polynomial(codeword,self.g)
        if np.all(syndrome == 0):
            return codeword[self.n-self.k:self.n+1]
        else:
            error_locating_polynomium=self.berlekamp_massey(syndrome_box)
            error_indexes=self.chien_search(error_locating_polynomium)
            for i in error_indexes:
                codeword[i]^=1
            return codeword[self.n-self.k:self.n+1]
        
    

    def random_message(self, length):
        #generates a message that consists of randomly chosen 1s and 0s of specified length. 
        return np.random.randint(0, 2, length, dtype=np.uint8)
    
    def test_messages(self, amount, amount_errors):
        for j in range(amount):
            mess=self.random_message(self.k)
            encoded_mess=self.encode_systematic(mess)
            for i in range(amount_errors):
                encoded_mess[np.random.randint(0,self.n)]^=1
            decoded=self.bch_decode(encoded_mess)
            if not np.array_equal(mess,decoded):
                return False
            print("decoded", j)
        return True
    



#primitive_polynomial=np.array([1,1,0,0,1]) #primal polynomial 1+x+x^4
primitive_polynomial=np.array([1,0,1,1,1,0,0,0,1], dtype=np.uint8)
encoder=BCH_actual(primitive_polynomial,5)

print(encoder.test_messages(100, 2))


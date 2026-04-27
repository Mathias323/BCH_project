import numpy as np

#This code aims to implement 1 enc_dec block from the OFEC coder block as outlined in figure 28 from the openroad standard.

##Bch decoder to a specified primitive polynomial and error correcting amount

class BCH_from_standard:
    def __init__(self):
        #The huge difference between this version and the version in part 2 is that this has the concrete numbers from the standard instead of variables.
        self.t=2                                                                    #t is the amount of errors this code can correct
        self.r=8                                                                    #r is the degree of the primitive polynomial
        self.n=2**self.r                                                            #n is the codeword vectors length in bits, it has 1 more than standard bch due to parity bit
        self.g=np.array([1,1,0,0,0,1,1,0,1,1,1,1,0,1,1,0,1],dtype=np.uint8)         #g is the generator polynomial
        self.p=np.array([1,0,1,1,1,0,0,0,1])                                        #p is the primitive polynomial that defines the field, i pulled this out of thing air.
        self.k=self.n-(len(self.g)-1)-1                                             #k is the uncoded data vectors length in bits again -1 because of parity bit
        
        #field element constants
        self.field_element_len=len(self.p)-1                                           #the length of a np.array containing a field element
        self.field_elements=self.get_field_elements()                                  #an array of all the field elements 
        self.field_element_0=np.zeros(self.field_element_len,dtype=np.uint8)           #the field element that is all 0's, not included in the rotation.
        self.field_elements_amount=2**(self.field_element_len)-1                       #the amount of field elements

        #A_table
        self.a_table=self.get_A_table()


    def get_field_elements(self): #simply gets all the field elements defined by the primitive polynomial upon initialization
        field_elements=np.zeros(((2**(self.field_element_len))-1,self.field_element_len),dtype=np.uint8) # will be a list of every single field element, or x^n, # doesnt contain the 0 element
        field_elements[0]=np.concatenate((np.array([1],dtype=np.uint8),np.zeros(self.field_element_len-1,dtype=np.uint8))) # first entry is just x^0
        append_0=np.array([0],dtype=np.uint8)  #i couldnt find an easy way to just shift right and bitmask in np
        for i in range(1,len(field_elements)):
            field_elements[i]=self.divide_polynomial(np.concatenate((append_0,field_elements[i-1]))[:self.field_element_len+1],self.p)[1]
        #print(field_elements, "field elements")
        return field_elements
    
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
        final_message = np.concatenate((parity_bit, message_padded))

        return final_message
    

    def get_A_table(self):
        temp_A_table=[]
        for j in range(self.field_elements_amount):
            temp=[]
            for i in range(self.field_elements_amount):
                y=self.field_elements[i]
                y_sq=self.field_elements[(i*2)%255]
                result=np.bitwise_xor(y,y_sq)
                if np.array_equal(result,self.field_elements[j]):
                    temp.append(i)
            temp_A_table.append(temp)
        return temp_A_table
            

    
    def decode(self, mess, return_full=False):
        working_mess=mess[1:]
        parity_syn=np.bitwise_xor.reduce(mess)

        s_1_temp=self.field_element_0
        s_3_temp=self.field_element_0
        for i in range(self.field_elements_amount):
            if working_mess[i]==1:
                s_1_temp=np.bitwise_xor(s_1_temp, self.field_elements[(i)%self.field_elements_amount])
                s_3_temp=np.bitwise_xor(s_3_temp, self.field_elements[(i*3)%self.field_elements_amount])


        #0 error logic

        if np.array_equal(s_1_temp,self.field_element_0) and np.array_equal(s_3_temp,self.field_element_0):
            if return_full:
                return working_mess
            return (working_mess[16:], True)   


        #1 and 2 error logic
        #syndrome and sigma logic
        if np.array_equal(s_1_temp,self.field_element_0):
            if return_full:
                    return working_mess
            return working_mess[16:], False
            pass
        else:
            s_1_index=np.where(np.all(self.field_elements == s_1_temp, axis=1))[0][0]
            sigma_1=s_1_temp

        s_1__3_index=(s_1_index*3)%255


        if np.array_equal(s_3_temp,self.field_element_0):
            sigma_2=(2*s_1_index)%255
        else:
            s_3_index=np.where(np.all(self.field_elements == s_3_temp, axis=1))[0][0]

            ##this little block is the 1 error returner, its placed here due to some edge cases with the 0 element during 2 error calculation
            if s_1__3_index ==s_3_index:
                working_mess[s_1_index]^=1
                if return_full:
                    return working_mess
                return (working_mess[16:], True)

            numerator=np.bitwise_xor(self.field_elements[s_1__3_index],self.field_elements[s_3_index])
            numerator_index=np.where(np.all(self.field_elements == numerator, axis=1))[0][0]

            sigma_2=(numerator_index-s_1_index)%255
        
        #2 error return logic
        A_index=(sigma_2-(2*s_1_index))%255

        a_table_result=self.a_table[A_index]

        if len(a_table_result)==2:
            if parity_syn:
                return (working_mess[16:255], False)
            loc1=(a_table_result[0]+s_1_index)%255
            loc2=(a_table_result[1]+s_1_index)%255
            working_mess[loc1]^=1
            working_mess[loc2]^=1

            if return_full:
                    return working_mess
            return (working_mess[16:], True)
        
        if return_full:
                    return working_mess
        return (working_mess[16:], False)
    
    
    def random_message(self, length):
        #generates a message that consists of randomly chosen 1s and 0s of specified length. 
        return np.random.randint(0, 2, length, dtype=np.uint8)
    

    

###testing



def main():
    encoder=BCH_from_standard()

    print(encoder.encode_systematic(np.zeros((encoder.k),dtype=np.uint8)))

    # message=encoder.random_message(encoder.k)
    # message_encoded=encoder.encode_systematic(message)
    # test_1=np.array_equal(message, encoder.decode(message_encoded)[0])

    # message2=encoder.random_message(encoder.k)
    # message_encoded2=encoder.encode_systematic(message2)
    # message_encoded2[144]^=1
    # test_2=np.array_equal(message2, encoder.decode(message_encoded2)[0])


    # message3=encoder.random_message(encoder.k)
    # message_encoded3=encoder.encode_systematic(message3)
    # message_encoded3[77]^=1
    # message_encoded3[177]^=1
    # test_3=np.array_equal(message3, encoder.decode(message_encoded3)[0])


    # message4=encoder.random_message(encoder.k)
    # message_encoded4=encoder.encode_systematic(message4)
    # message_encoded4[77]^=1
    # message_encoded4[177]^=1
    # message_encoded4[100]^=1
    # test_4=not encoder.decode(message_encoded4)[1]


    # print(test_1,"0 error scenario works")
    # print(test_2,"1 error scenario works")
    # print(test_3,"2 error scenario works")
    # print(test_4,"3 error scenario works")


    #print(encoder.test_messages(100, 2))


    
if __name__ == "__main__":
    main()
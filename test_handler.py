from OpenroadFec_3 import BCH_from_standard
import numpy as np

class test_handler:
    def __init__(self):
        self.fec=BCH_from_standard()


    def random_message(self, length):
        #generates a message that consists of randomly chosen 1s and 0s of specified length. 
        return np.random.randint(0, 2, length, dtype=np.uint8)
    


    def full_pattern_testing(self):
        #this function runs about 2.700.000 tests btw, so dont run it, it takes like an hour, but it does confirm that it correctly decodes all
        #possible situations and therefore is fully standard compliant
        test_0=True
        test_1=True
        test_2=True
        test_3=True
        
        for i in range(self.fec.n):
            test_message1=self.random_message(self.fec.k)
            encoded_mess1=self.fec.encode_systematic(test_message1)

            mess_no_error, status_no_error=self.fec.decode(encoded_mess1)
            if (not np.array_equal(test_message1,mess_no_error)) or (not status_no_error):
                print(f"0-error failed at i={i}")
                return False

            test_message2=self.random_message(self.fec.k)
            encoded_mess2=self.fec.encode_systematic(test_message2)
        
            encoded_mess2[i]^=1
            mess_1_error, status_1_error=self.fec.decode(encoded_mess2)
            if (not np.array_equal(test_message2,mess_1_error)) or (not status_1_error) :
                print(f"1-error failed at i={i}")
                return False

            for j in range(i+1,self.fec.n):
                test_message3=self.random_message(self.fec.k)
                encoded_mess3=self.fec.encode_systematic(test_message3)

                encoded_mess3[i]^=1
                encoded_mess3[j]^=1

                mess_2_error, status_2_error=self.fec.decode(encoded_mess3)
                if (not np.array_equal(test_message3,mess_2_error)) or (not status_2_error):
                    print(f"2-error failed at i={i}")
                    return False
                for k in range(j+1, self.fec.n):
                    test_message4=self.random_message(self.fec.k)
                    encoded_mess4=self.fec.encode_systematic(test_message4)

                    encoded_mess4[i]^=1
                    encoded_mess4[j]^=1
                    encoded_mess4[k]^=1

                    mess_3_error, status_3_error=self.fec.decode(encoded_mess4)
                    if status_3_error:
                        print(f"3-error failed at i={i}")
                        return False
            print(f"progress at {(i+1)/256*100:.2f}%")
            print(f"no error test passed = {np.array_equal(test_message1,mess_no_error)}")
            print(f"1 error test passed = {np.array_equal(test_message2,mess_1_error)}")
            print(f"2 error test passed = {np.array_equal(test_message3,mess_2_error)}")
            print(f"3 error test passed = {not status_3_error}")

        return True


tester=test_handler()

print(tester.full_pattern_testing())
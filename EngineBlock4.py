from OpenroadFec_3 import BCH_from_standard
import numpy as np



class EngineBlock:
    def __init__(self):
        pass
        
        




encoder=BCH_from_standard()

message=encoder.random_message(encoder.k)
message_encoded=encoder.encode_systematic(message)
test_1=np.array_equal(message, encoder.decode(message_encoded))

message2=encoder.random_message(encoder.k)
message_encoded2=encoder.encode_systematic(message2)
message_encoded2[144]^=1
test_2=np.array_equal(message2, encoder.decode(message_encoded2))


message3=encoder.random_message(encoder.k)
message_encoded3=encoder.encode_systematic(message3)
message_encoded3[77]^=1
message_encoded3[177]^=1
test_3=np.array_equal(message3, encoder.decode(message_encoded3))

from OpenroadFec_3 import BCH_from_standard
import numpy as np


class BlockMemory:
    def __init__(self, B=16, rows=20, cols=8):
        self.B=B
        self.rows=rows
        self.cols=cols

        self.memory=np.ones((rows,cols,B,B),dtype=np.uint8)



    def write_block(self, big_row, big_col, block_data): #works
        block_data = np.asarray(block_data, dtype=np.uint8)

        if block_data.shape != (self.B, self.B):
            raise ValueError(f"block_data must have shape {(self.B, self.B)}")
        self.memory[big_row, big_col]=block_data

    def read_block(self, big_row, big_col): #works
        return self.memory[big_row,big_col]

    def read_block_row(self, big_row, big_col, row): #works
        return self.memory[big_row,big_col,row]
    
    def read_block_col(self, big_row, big_col, col):
        return self.memory[big_row,big_col,:,col]

    def read_big_row(self, big_row,row): #works
        return self.memory[big_row,:,row,:].reshape(-1)
    
    def shift_up(self, n=2):
        self.memory[:-n]=self.memory[n:]
        self.memory[-n:]=0
    
    def get_bit(self, big_row, big_col, row, col):
        return self.memory[big_row,big_col,row,col]

    
def main():
    memory=BlockMemory()
    np.set_printoptions(threshold=np.inf)
    test_block=np.ones((16,16),dtype=np.uint8)
    memory.write_block(0,0,test_block)
    print(memory.read_big_row(0,1)) 


if __name__ == "__main__":
    main()

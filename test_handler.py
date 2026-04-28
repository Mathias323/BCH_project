from OpenroadFec_3 import BCH_from_standard
from productversion6 import productioncode
import numpy as np
import matplotlib.pyplot as plt

class test_handler:
    def __init__(self):
        self.fec=BCH_from_standard()
        self.productcode=productioncode()

    def random_message(self, length):
        #generates a message that consists of randomly chosen 1s and 0s of specified length. 
        return np.random.randint(0, 2, length, dtype=np.uint8)
    


    def full_pattern_testing(self):
        #this function runs about 2.700.000 tests btw, so dont run it unless you really want to, it takes like an hour, but it does confirm that it correctly decodes all
        #possible situations and therefore is fully standard compliant
        print("hello?")
        
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
    

    def full_pattern_testing_ending(self):
        #this function runs about 2.700.000 tests btw, so dont run it unless you really want to, it takes like an hour, but it does confirm that it correctly decodes all
        #possible situations and therefore is fully standard compliant
        print("hello?")
        
        for i in range(self.fec.n):
            test_message1=self.random_message(self.fec.k)
            encoded_mess1=self.fec.encode_systematic_ending(test_message1)

            mess_no_error, status_no_error=self.fec.decode_ending(encoded_mess1)
            if (not np.array_equal(test_message1,mess_no_error)) or (not status_no_error):
                print(f"0-error failed at i={i}")
                return False

            test_message2=self.random_message(self.fec.k)
            encoded_mess2=self.fec.encode_systematic_ending(test_message2)
        
            encoded_mess2[i]^=1
            mess_1_error, status_1_error=self.fec.decode_ending(encoded_mess2)
            if (not np.array_equal(test_message2,mess_1_error)) or (not status_1_error) :
                print(f"1-error failed at i={i}")
                return False

            for j in range(i+1,self.fec.n):
                test_message3=self.random_message(self.fec.k)
                encoded_mess3=self.fec.encode_systematic_ending(test_message3)

                encoded_mess3[i]^=1
                encoded_mess3[j]^=1

                mess_2_error, status_2_error=self.fec.decode_ending(encoded_mess3)
                if (not np.array_equal(test_message3,mess_2_error)) or (not status_2_error):
                    print(f"2-error failed at i={i}")
                    return False
                for k in range(j+1, self.fec.n):
                    test_message4=self.random_message(self.fec.k)
                    encoded_mess4=self.fec.encode_systematic_ending(test_message4)

                    encoded_mess4[i]^=1
                    encoded_mess4[j]^=1
                    encoded_mess4[k]^=1

                    mess_3_error, status_3_error=self.fec.decode_ending(encoded_mess4)
                    if status_3_error:
                        print(f"3-error failed at i={i}")
                        return False
            print(f"progress at {(i+1)/256*100:.2f}%")
            print(f"no error test passed = {np.array_equal(test_message1,mess_no_error)}")
            print(f"1 error test passed = {np.array_equal(test_message2,mess_1_error)}")
            print(f"2 error test passed = {np.array_equal(test_message3,mess_2_error)}")
            print(f"3 error test passed = {not status_3_error}")

        return True
    
    def productioncode_block_test(self,errorpecentage,decode_iteraions):

        message=self.random_message(239*239)
        message=np.array(message)
        message=message.reshape(239,239)
        message_enc_block=self.productcode.encode(message)

        amt_errors=0
        errors=(np.random.random(message_enc_block.shape) < errorpecentage).astype(np.uint8)
        errorfilled_message=np.bitwise_xor(message_enc_block,errors)
        decoded=self.productcode.decode(errorfilled_message,decode_iteraions)

        amt_errors=np.sum(np.bitwise_xor(decoded,message))  
        print(amt_errors)
        return amt_errors
    
    
    def test_single_bch(self,errorpecentage):

        message=self.random_message(239)
        message=np.array(message)
        message_enc=self.fec.encode_systematic_ending(message)

        amt_errors=0

        errors=(np.random.random(message_enc.shape) < errorpecentage).astype(np.uint8)
        errorfilled_message=np.bitwise_xor(message_enc,errors)

        decoded=self.fec.decode_ending(errorfilled_message)[0]

        amt_errors=np.sum(np.bitwise_xor(decoded,message))  
        print(amt_errors)
        return amt_errors

    
    def pretty_graphs_n_stuff(self):
        x_axis=np.arange(0, 0.01, 0.001)
        y_multiple=[]

        for j in range(4):
            amt_iterations=[]
            for i in x_axis:
                amt_iterations.append(self.productioncode_block_test(i,j)/(239*239))
                print("iteration", j, i)
            y_multiple.append(amt_iterations)



        plt.figure(figsize=(8, 5))

        for i, y in enumerate(y_multiple):
            plt.plot(x_axis, y, marker='o', label=f"Iteration {i+1}")

        plt.xlabel("Channel error probability")
        plt.semilogy()
        plt.ylabel("Amount of message errors")
        plt.title("Product code performance")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
        
    def pretty_graphs_n_stuff_chatversion(self):
        message_len_product = 239 * 239
        message_len_bch = 239

        # Similar useful range to the example figure
        x_axis = np.logspace(-4, -1.7, 18)   # 1e-4 to about 0.02

        product_iterations = [1, 2, 3, 4, 5]

        # Product code is expensive
        product_trials_per_point = 10

        # Single BCH is cheap, so run more trials
        single_bch_trials_per_point = 500

        # For displaying zero-error points on log scale
        plot_floor = 1e-20

        # -------------------------
        # Uncoded channel reference
        # -------------------------
        uncoded_ber = x_axis.copy()

        # -------------------------
        # Single BCH curve
        # -------------------------
        single_bch_ber = []

        for p_idx, p in enumerate(x_axis):
            total_errors = 0
            total_bits = 0

            print(f"\nSingle BCH, p = {p:.3e} ({p_idx+1}/{len(x_axis)})")

            for trial in range(single_bch_trials_per_point):
                total_errors += self.test_single_bch(p)
                total_bits += message_len_bch

            ber = total_errors / total_bits
            single_bch_ber.append(ber)

            print(f"Single BCH average BER = {ber:.3e}")

        # -------------------------
        # Product code curves
        # -------------------------
        product_ber_curves = []

        for iterations in product_iterations:
            ber_list = []

            for p_idx, p in enumerate(x_axis):
                total_errors = 0
                total_bits = 0

                print(f"\nProduct code, iterations = {iterations}, p = {p:.3e} ({p_idx+1}/{len(x_axis)})")

                for trial in range(product_trials_per_point):
                    errors = self.productioncode_block_test(p, iterations)
                    total_errors += errors
                    total_bits += message_len_product

                    print(f"  trial {trial+1}/{product_trials_per_point}: errors = {errors}")

                ber = total_errors / total_bits
                ber_list.append(ber)

                print(f"Product average BER = {ber:.3e}")

            product_ber_curves.append(ber_list)

        # -------------------------
        # Plotting
        # -------------------------
        plt.figure(figsize=(12, 7))

        plt.loglog(
            x_axis,
            np.maximum(uncoded_ber, plot_floor),
            color="black",
            linewidth=2,
            label="Channel (no coding)"
        )

        plt.loglog(
            x_axis,
            np.maximum(single_bch_ber, plot_floor),
            color="black",
            linestyle="--",
            linewidth=2,
            label="Single BCH(256,239)"
        )

        colors = ["green", "orange", "blue", "purple", "red"]

        for iterations, ber_list, color in zip(product_iterations, product_ber_curves, colors):
            plt.loglog(
                x_axis,
                np.maximum(ber_list, plot_floor),
                color=color,
                linewidth=2,
                label=f"{iterations} iterations (row+col)"
            )

        # Optional OFEC-like target marker, like in your reference picture
        plt.scatter(
            [2e-2],
            [1e-15],
            color="green",
            marker="*",
            s=300,
            label="OFEC target marker"
        )

        plt.xlabel("Pre-FEC BER (p)", fontsize=13)
        plt.ylabel("Post-FEC BER", fontsize=13)
        plt.title("Product code performance: BCH(256,239) by iteration count", fontsize=15)

        plt.grid(True, which="both", alpha=0.35)

        plt.xlim(1e-4, 3e-2)
        plt.ylim(plot_floor, 1)

        plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
        plt.tight_layout()

        plt.savefig("product_code_bch_ber_plot.png", dpi=300, bbox_inches="tight")
        plt.show(block=True)

        input("Press Enter to close...")

tester=test_handler()

tester.pretty_graphs_n_stuff_chatversion()
from OpenroadFec_3 import BCH_from_standard
from productversion6 import productioncode
from EngineBlock4 import EngineBlock_encoder, EngineBlock_decoder

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

    
    def single_bch_ber(self, error_percentage, trials):
        total_errors = 0
        total_bits = 0

        for _ in range(trials):
            message = self.random_message(239)
            encoded = self.fec.encode_systematic_ending(message)

            error_mask = (np.random.random(encoded.shape) < error_percentage).astype(np.uint8)
            noisy_encoded = np.bitwise_xor(encoded, error_mask)

            decoded = self.fec.decode_ending(noisy_encoded)[0]

            total_errors += np.count_nonzero(decoded != message)
            total_bits += message.size

        return total_errors / total_bits


    def product_code_ber(self, error_percentage, iterations, trials):
        total_errors = 0
        total_bits = 0

        for _ in range(trials):
            message = self.random_message(239 * 239).reshape(239, 239)
            encoded = self.productcode.encode(message)

            error_mask = (np.random.random(encoded.shape) < error_percentage).astype(np.uint8)
            noisy_encoded = np.bitwise_xor(encoded, error_mask)

            decoded = self.productcode.decode(noisy_encoded, iterations)

            total_errors += np.count_nonzero(decoded != message)
            total_bits += message.size

        return total_errors / total_bits


    def engine4_middle_window_once(
        self,
        error_percentage,
        iterations=3,
        num_blocks=200,
        check_start=60,
        check_stop=160,
    ):
        encoder = EngineBlock_encoder()
        decoder = EngineBlock_decoder(iterations)

        inputs = [
            np.random.randint(0, 2, (32, 111), dtype=np.uint8)
            for _ in range(num_blocks)
        ]

        decoded_by_input_index = {}

        for input_index, input_block in enumerate(inputs):
            encoded = encoder.encode_block(input_block)

            noisy_encoded = encoded.copy()

            if error_percentage > 0:
                error_mask = np.random.random(noisy_encoded.shape) < error_percentage
                noisy_encoded[error_mask] ^= 1

            decoded, valid = decoder.decode_block(noisy_encoded)

            if valid:
                original_input_index = input_index - decoder.total_latency_blocks
                decoded_by_input_index[original_input_index] = decoded.copy()

        total_errors = 0
        total_bits = 0
        missing_indices = []

        for input_index in range(check_start, check_stop):
            if input_index not in decoded_by_input_index:
                missing_indices.append(input_index)
                continue

            total_errors += np.count_nonzero(
                decoded_by_input_index[input_index] != inputs[input_index]
            )
            total_bits += inputs[input_index].size

        if missing_indices:
            raise AssertionError(
                f"Missing decoded outputs for input indices: {missing_indices}"
            )

        return total_errors, total_bits


    def engine4_ber(
        self,
        error_percentage,
        iterations=3,
        trials=1,
        num_blocks=200,
        check_start=60,
        check_stop=160,
    ):
        total_errors = 0
        total_bits = 0

        for _ in range(trials):
            errors, bits = self.engine4_middle_window_once(
                error_percentage=error_percentage,
                iterations=iterations,
                num_blocks=num_blocks,
                check_start=check_start,
                check_stop=check_stop,
            )

            total_errors += errors
            total_bits += bits

        if total_bits == 0:
            return 1.0

        return total_errors / total_bits


    def validate_engine4_middle_window(self):
        print("\nValidating Engine4 middle-window alignment")

        for iterations in [1, 3]:
            errors, bits = self.engine4_middle_window_once(
                error_percentage=0.0,
                iterations=iterations,
                num_blocks=200,
                check_start=60,
                check_stop=160,
            )

            ber = errors / bits

            print(f"iterations={iterations}")
            print(f"  checked input indices: 60 to 159")
            print(f"  checked bits: {bits}")
            print(f"  errors: {errors}")
            print(f"  BER: {ber:.3e}")

            if errors != 0:
                raise AssertionError(
                    f"No-error Engine4 middle-window test failed for iterations={iterations}"
                )

        print("PASS: Engine4 no-error middle-window validation")


    def plot_clean_comparison(self):
        # Main knobs. Increase trials later when the code path is trusted.
        x_axis = np.logspace(-4, -1.7, 10)

        single_bch_trials = 300
        product_trials = 3
        engine_trials = 2

        product_iterations = [1, 3, 5]
        engine_iterations = [1, 3]

        # Engine4 is now tested in the steady middle of a rolling stream.
        engine_num_blocks = 200
        engine_check_start = 60
        engine_check_stop = 160

        plot_floor = 1e-20

        uncoded_ber = x_axis.copy()

        # First prove that the steady-state alignment works with no errors.
        self.validate_engine4_middle_window()

        # -------------------------
        # Single BCH curve
        # -------------------------
        single_bch_curve = []

        for p_idx, p in enumerate(x_axis):
            print(f"\nSingle BCH: p={p:.3e} ({p_idx + 1}/{len(x_axis)})")
            ber = self.single_bch_ber(p, single_bch_trials)
            single_bch_curve.append(ber)
            print(f"Single BCH BER = {ber:.3e}")

        # -------------------------
        # Product-code curves
        # -------------------------
        product_curves = {}

        for iterations in product_iterations:
            curve = []

            for p_idx, p in enumerate(x_axis):
                print(f"\nProduct code: iterations={iterations}, p={p:.3e} ({p_idx + 1}/{len(x_axis)})")
                ber = self.product_code_ber(p, iterations, product_trials)
                curve.append(ber)
                print(f"Product code BER = {ber:.3e}")

            product_curves[iterations] = curve

        # -------------------------
        # Engine4 curves
        # -------------------------
        engine_curves = {}

        for iterations in engine_iterations:
            curve = []

            for p_idx, p in enumerate(x_axis):
                print(f"\nEngine4 middle-window: iterations={iterations}, p={p:.3e} ({p_idx + 1}/{len(x_axis)})")
                ber = self.engine4_ber(
                    error_percentage=p,
                    iterations=iterations,
                    trials=engine_trials,
                    num_blocks=engine_num_blocks,
                    check_start=engine_check_start,
                    check_stop=engine_check_stop,
                )
                curve.append(ber)
                print(f"Engine4 BER = {ber:.3e}")

            engine_curves[iterations] = curve

        # -------------------------
        # Bookkeeping sanity check
        # -------------------------
        if 3 in product_curves and 3 in engine_curves:
            product_3 = np.array(product_curves[3])
            engine_3 = np.array(engine_curves[3])

            print("\nBookkeeping check:")
            print("Product 3 curve:", product_3)
            print("Engine4 3 curve:", engine_3)
            print("Exactly equal:", np.array_equal(product_3, engine_3))
            print("Numerically close:", np.allclose(product_3, engine_3))

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
            np.maximum(single_bch_curve, plot_floor),
            color="black",
            linestyle="--",
            linewidth=2,
            label="Single BCH(256,239)"
        )

        product_styles = {
            1: {"color": "green", "linestyle": "-"},
            3: {"color": "blue", "linestyle": "-"},
            5: {"color": "red", "linestyle": "-"},
        }

        for iterations in product_iterations:
            style = product_styles[iterations]
            plt.loglog(
                x_axis,
                np.maximum(product_curves[iterations], plot_floor),
                color=style["color"],
                linestyle=style["linestyle"],
                linewidth=2,
                label=f"Product code, {iterations} iterations"
            )

        engine_styles = {
            1: {"color": "orange", "linestyle": "-."},
            3: {"color": "magenta", "linestyle": "-."},
        }

        for iterations in engine_iterations:
            style = engine_styles[iterations]
            plt.loglog(
                x_axis,
                np.maximum(engine_curves[iterations], plot_floor),
                color=style["color"],
                linestyle=style["linestyle"],
                linewidth=2,
                label=f"Engine4 middle-window, {iterations} iterations"
            )

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
        plt.title("BCH(256,239) comparison: product code vs Engine4", fontsize=15)

        plt.grid(True, which="both", alpha=0.35)
        plt.xlim(1e-4, 3e-2)
        plt.ylim(plot_floor, 1)

        plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
        plt.tight_layout()

        plt.savefig("bch_engine4_comparison_plot.png", dpi=300, bbox_inches="tight")
        plt.show(block=True)

        input("Press Enter to close...")

        return {
            "x_axis": x_axis,
            "single_bch": single_bch_curve,
            "product": product_curves,
            "engine4": engine_curves,
        }


    # Keep the old call name working, but route it to the corrected version.
    def pretty_graphs_n_stuff_chatversion(self):
        return self.plot_clean_comparison()


if __name__ == "__main__":
    tester = test_handler()
    tester.plot_clean_comparison()

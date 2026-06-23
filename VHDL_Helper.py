from OpenroadFec_3 import BCH_from_standard
from EngineBlock4 import EngineBlock_encoder
import numpy as np



def calculate_parity_matrix():
    coder=BCH_from_standard()
    
    P=np.zeros((17,239),dtype=np.uint8)

    for i in range(239):
        individuel_contribution=np.zeros(239, dtype=np.uint8)
        individuel_contribution[i]^=1

        encoded= coder.encode_systematic_ending(individuel_contribution)
        print(len(encoded[239:256]))

        P[:,i]= encoded[239:256]

    
    with open("parity_matrix.vhd", "w", encoding="utf-8") as output_file:
        output_file.write(
            """type parity_matrix_t is array (0 to 16)
        of std_logic_vector(0 to 238);

        constant PARITY_MATRIX : parity_matrix_t := (
        """
        )
        for row_index, row in enumerate(P):
            bit_string = "".join(str(int(bit)) for bit in row)
            comma = "," if row_index < 16 else ""

            output_file.write(
                f'    {row_index} => "{bit_string}"{comma}\n'
            )

        output_file.write(");\n")

    test = np.random.randint(0, 2, 239, dtype=np.uint8)

    encoded = coder.encode_systematic_ending(test)
    matrix_parity = (P @ test) % 2
    expected_parity = encoded[239:256]

    print(np.array_equal(matrix_parity, expected_parity))


def generate_bch_test_vector(encoder):
    input_array = np.random.randint(0,2,239,dtype=np.uint8)

    encoded_array = encoder.encode_systematic_ending(input_array)
    output_array = encoded_array[128:256]

    input_string = "".join(str(int(bit)) for bit in input_array)
    output_string = "".join(str(int(bit)) for bit in output_array)

    print("Input string:")
    print(input_string)

    print("\nExpected output string:")
    print(output_string)

    return input_string, output_string

def generate_txt_files(encoder):
    input_vectors = np.random.randint(
        0, 2,
        size=(30, 3552),
        dtype=np.uint8
    )

    encoded_blocks = []
    output_vectors = []

    with open("openroad_input_vectors.txt", "w") as input_file, \
         open("openroad_output_vectors.txt", "w") as output_file:

        for vector in input_vectors:
            input_file.write("".join(str(bit) for bit in vector) + "\n")

            formatted_input = format_encoder_input(vector)
            encoded_block = encoder.encode_block(formatted_input)
            formatted_output = format_encoder_output(encoded_block)

            encoded_blocks.append(encoded_block)
            output_vectors.append(formatted_output)

            output_file.write("".join(str(bit) for bit in formatted_output) + "\n")

def format_encoder_output(encoded_block):
    output_vector = np.zeros(4096, dtype=np.uint8)

    for block_column_index in range(8):
        for block_row_index in range(2):
            for row_index in range(16):
                for column_index in range(16):
                    output_vector[
                        block_column_index * 512
                        + block_row_index * 256
                        + row_index * 16
                        + column_index
                    ] = encoded_block[
                        block_row_index,
                        block_column_index,
                        row_index,
                        column_index
                    ]
    return output_vector   

def format_encoder_input(input_vector):
    formatted_input = np.zeros((32, 111), dtype=np.uint8)

    input_index = 0

    for block_column_index in range(6):
        for block_row_index in range(2):
            for row_index in range(16):
                for column_index in range(16):

                    formatted_input[
                        block_row_index * 16 + row_index,
                        block_column_index * 16 + column_index
                    ] = input_vector[input_index]

                    input_index += 1

    for block_row_index in range(2):
        for row_index in range(16):
            for column_index in range(15):

                formatted_input[
                    block_row_index * 16 + row_index,
                    96 + column_index
                ] = input_vector[input_index]

                input_index += 1

    return formatted_input



def export_field_element_table(
    output_filename="field_element_table.vhd",
    entries_per_line=6
):
    bch = BCH_from_standard()

    entries = []

    for index, element in enumerate(bch.field_elements):
        bit_string = "".join(str(int(bit)) for bit in element)
        entries.append(f'{index} => "{bit_string}"')

    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(
            "type field_element_table_t is array (0 to 254) of "
            "std_logic_vector(0 to 7);\n\n"
        )

        file.write(
            "constant FIELD_ELEMENT_TABLE : field_element_table_t := (\n"
        )

        for start in range(0, len(entries), entries_per_line):
            line_entries = entries[start:start + entries_per_line]
            line = ", ".join(line_entries)

            if start + entries_per_line < len(entries):
                line += ","

            file.write(f"    {line}\n")

        file.write(");\n")


def export_reverse_field_element_table(
    field_elements,
    output_filename="reverse_field_element_table.vhd",
    entries_per_line=8
):
    reverse_table = [255] * 256

    for exponent, element in enumerate(field_elements):
        bit_string = "".join(str(int(bit)) for bit in element)
        element_value = int(bit_string, 2)
        reverse_table[element_value] = exponent

    entries = [
        f"{element_value} => {exponent}"
        for element_value, exponent in enumerate(reverse_table)
    ]

    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(
            "type reverse_field_element_table_t is array (0 to 255) "
            "of integer range 0 to 255;\n\n"
        )

        file.write(
            "constant REVERSE_FIELD_ELEMENT_TABLE : "
            "reverse_field_element_table_t := (\n"
        )

        for start in range(0, len(entries), entries_per_line):
            line_entries = entries[start:start + entries_per_line]
            line = ", ".join(line_entries)

            if start + entries_per_line < len(entries):
                line += ","

            file.write(f"    {line}\n")

        file.write(");\n")



from pathlib import Path


from pathlib import Path


def create_a_table_vhdl_txt(
    output_file: str = "A_table_constant.txt",
    entries_per_line: int = 8,
) -> Path:

    from OpenroadFec_3 import BCH_from_standard

    if entries_per_line < 1:
        raise ValueError("entries_per_line must be at least 1")

    bch = BCH_from_standard()
    a_table = bch.a_table

    if len(a_table) != 255:
        raise ValueError(
            f"Expected 255 A-table entries, got {len(a_table)}"
        )

    entries = []

    for a_index, roots in enumerate(a_table):
        if len(roots) == 2:
            root_1 = int(roots[0])
            root_2 = int(roots[1])

            if not 0 <= root_1 <= 254:
                raise ValueError(
                    f"Invalid first root {root_1} at index {a_index}"
                )

            if not 0 <= root_2 <= 254:
                raise ValueError(
                    f"Invalid second root {root_2} at index {a_index}"
                )

            value = f"{root_1:02X}{root_2:02X}"

        elif len(roots) == 0:
            value = "FFFF"

        else:
            raise ValueError(
                f"A-table entry {a_index} contains "
                f"{len(roots)} roots"
            )

        entries.append(f'{a_index} => x"{value}"')

    lines = [
        "type a_table_t is array (0 to 254) of "
        "std_logic_vector(15 downto 0);",
        "",
        "constant A_TABLE : a_table_t := (",
    ]

    for start in range(0, len(entries), entries_per_line):
        group = entries[start:start + entries_per_line]
        line = "    " + ", ".join(group)

        if start + entries_per_line < len(entries):
            line += ","

        lines.append(line)

    lines.append(");")
    lines.append("")

    output_path = Path(output_file)
    output_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Created VHDL A-table: {output_path.resolve()}")
    return output_path



def create_decoder_vectors(filename="decoder_vectors.txt"):
    import numpy as np
    from OpenroadFec_3 import BCH_from_standard

    bch = BCH_from_standard()
    message = np.random.default_rng(1).integers(0, 2, bch.k, dtype=np.uint8)
    clean = bch.encode_systematic_ending(message)

    errors = [
        [], [255],
        [17], [17, 255],
        [23, 197], [23, 197, 255],
        [11, 89, 203]
    ]

    # Python index 0 maps to VHDL bit 0, the leftmost literal bit.
    # Intended for std_logic_vector(0 to 255).
    def vhdl_hex(x):
        return f'x"{int("".join(map(str, x)), 2):064X}"'

    inputs, expected = [], []

    for err in errors:
        received = clean.copy()
        received[err] ^= 1

        inputs.append(vhdl_hex(received))
        expected.append(vhdl_hex(
            bch.decode_ending(received, return_full=True)
        ))

    with open(filename, "w") as f:
        f.write(
            "type codeword_array_t is array (0 to 6) of "
            "std_logic_vector(0 to 255);\n\n"
        )

        f.write("constant DECODER_INPUTS : codeword_array_t := (\n    ")
        f.write(",\n    ".join(inputs))
        f.write("\n);\n\n")

        f.write("constant DECODER_EXPECTED : codeword_array_t := (\n    ")
        f.write(",\n    ".join(expected))
        f.write("\n);\n")





def write_payload_vectors_txt(
    filename="payload_vectors.txt",
    num_blocks=300,
    payload_width=32 * 111,
    seed=12345,
):
    """
    Creates a text file for openroad_enc_dec_tb_simple.vhd.

    Each line contains one payload block:
        3552 bits as ASCII '0'/'1'

    Default:
        300 lines x 3552 bits
    """

    rng = np.random.default_rng(seed)

    with open(filename, "w", encoding="ascii") as f:
        for _ in range(num_blocks):
            payload = rng.integers(
                0,
                2,
                size=payload_width,
                dtype=np.uint8,
            )

            bit_string = "".join(str(int(bit)) for bit in payload)
            f.write(bit_string + "\n")




if __name__ == "__main__":
    write_payload_vectors_txt()



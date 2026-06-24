The relevant files in this project are the numbered files "Starter_FEC_1", "BCH_CODE_2", "OpenroadFec_3", "EngineBlock4", "BlockMemoryClass5" and "productversion6"
files 1 and 2 was made with the intention of learning and implemention broad theory, whereas 3 is made with the intent of making the specific required BCH for the OpenROADM standard,
file 4 and 5 implement the openROADM standard, with 5 being the memory class that implements the state array, and 4 handling the state array and doing the actual decoding and encoding.
file 6 implements the product code version as a comparison.
there are a couple test files. test_handler and test_handler_middle_window that tests the error correcting capabilities of the different files, and runs large simulations, which generates the plot pictures.
TheoryBrushup is a simply jupiter notebook that implements the guide example from Jakobs pdf.
VHDL_helper is for generating different files for the vhdl implementation, which is why there is a ton of txt and vhdl files.

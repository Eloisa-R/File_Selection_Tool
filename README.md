# File_Selection_Tool for Outsourcing

Tool that selects which product attribute files should be outsourced for translation. Each file has certain characteristics
(source language, number of values, merchant, etc.). They should be prioritised according to merchant and there should be
a limit on the total number of values outsourced and also on the total number of values per source language,
since the freelance translators have limited capacity.

The tool uses a csv file with the list of product attribute files and another one with the capacities per target language.
It outputs a txt file with the data of the files that should be outsourced. 

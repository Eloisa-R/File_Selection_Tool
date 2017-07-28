import sys
import csv
import itertools
import tkinter
from operator import attrgetter
from tkinter import messagebox, filedialog

csv_dict = {}
prio_dict = {}
target_retail_dict = {}
target_3P_dict = {}
ProductAttributeFiles_retail = []
total_values = []
retail_by_rank = []
final_retail_list = []
ProductAttributeFiles_3P = []
TP_by_rank = []
final_3P_list = []
total_values_retail = []
total_values_3P = []
id_list = []
ProductAttributeFiles_language_comb = []
dict_lan = {}
total_values_re_sel = []
total_values_3p_sel = []

# Each file of product attributes has a series of characteristics
# We'll want to prioritise them according to merchant type
# And limit the amount of files we select per source language,
# Since translators can only do certain languages


class ProductAttributeFile:
    _registry = []

    def __init__(
            self, name, url, source_locale, target_locale,
            source_MP, attribute, merchant, products, values, rank):
        self._registry.append(self)
        self.name = name
        self.url = url
        self.source_locale = source_locale
        self.target_locale = target_locale
        self.source_MP = source_MP
        self.attribute = attribute
        self.merchant = merchant
        self.products = products
        self.values = values
        self.rank = rank


# With the counter class we'll be able to create
# a counter per source language


class counter:
    _registry = []

    def __init__(self, name, source_locale, capacity):
        self.name = name
        self.source_locale = source_locale
        self.capacity = capacity
        self.count = 0


print("Please select a csv file with the ProductAttributeFile extract")
root = tkinter.Tk()
root.withdraw()
ProductAttributeFilefile = filedialog.askopenfilename(
    filetypes=[("Csv files", "*.csv")])

with open(ProductAttributeFilefile) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            csv_dict[row['ShortId']] = [row['IssueUrl'], row['Title']]
        except KeyError:
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showerror(title="Error",
                                 message="This file doesn't have the right \
                                 headers ('ShortId', 'IssueUrl', 'Title')")
            sys.exit()

for key, value in csv_dict.items():
    csv_value = value[1].split(' ')
    key = ProductAttributeFile(
        str(key), str(value[0]), str(csv_value[1])[1:3],
        str(csv_value[3])[1:3], str(csv_value[1])[4:6],
        str(csv_value[4]), str(csv_value[5]),
        str(csv_value[6]).replace("(", ""), int(csv_value[8]),
        int(str(csv_value[6]).replace("(", "")) / int(
            csv_value[8]))

# The user now selects a file with the capacities per target language
print("Please select a csv file with the MP data")
root = tkinter.Tk()
root.withdraw()
MPfile = filedialog.askopenfilename(filetypes=[("Csv files", "*.csv")])

with open(MPfile) as csvfile_2:
    data_reader = csv.DictReader(csvfile_2)
    for row in data_reader:
        try:
            target = str(row['Target']).lower()
            maximum_value = int(row['Maximum number of values']) + 200
            language_limits = row['Language limitations']
            prefill_attribute_list = row['Prefilled attributes']
        except KeyError:
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showerror(title="Error", message="This file doesn't have \
                the right headers ('Target', 'Maximum number of values', \
                'Language limitations', 'Prefilled attributes')")
            sys.exit()

language_limits_list = language_limits.split("/")

for element in language_limits_list:
    source_counter = str(element.split()[0])
    source_counter = counter(source_counter, str(
        element.split()[0]), int(element.split()[1]))
    dict_lan[str(element.split()[0]).lower()] = source_counter


def create_merchant_list(target_locale, merchant,
                         ProductAttributeFiles_merchant,
                         total_values_merchant):
    for ProductAttributeFileobject in ProductAttributeFile._registry:
        if ProductAttributeFileobject.target_locale == target_locale and (
                ProductAttributeFileobject.merchant == merchant):
            total_values_merchant.append(ProductAttributeFileobject.values)
            ProductAttributeFiles_merchant.append(
                ProductAttributeFileobject)


def select_by_rank(ordered_list_by_rank, ProductAttributeFiles_merchant,
                   maximum_value, final_merchant_list):
    ordered_list_by_rank = sorted(
        ProductAttributeFiles_merchant,
        key=attrgetter('rank'), reverse=True)
    counter = 0
    for item in ordered_list_by_rank:
        counter = counter + item.values
        if counter < maximum_value:
            final_merchant_list.append(item)

# for each object in the list ordered by rank, get the source and use it
# to retrieve the counter object for that source (stored in a dictionary)
# if the number of values doesn't overflow the maximum value,
# check if it overflows that source's capacity
# if it doesn't, add it to the final list, if it does, subtract the values
# from both counters and continue with the next ProductAttributeFile


def select_by_rank_language_limit(
    ordered_list_by_rank, ProductAttributeFiles_merchant,
    maximum_value, final_merchant_list,
        total_values_selection):
    ordered_list_by_rank = sorted(
        ProductAttributeFiles_merchant,
        key=attrgetter('rank'), reverse=True)
    general_counter = 0
    for item in ordered_list_by_rank:
        source_counter = dict_lan.get(item.source_locale)
        general_counter += item.values
        if general_counter < maximum_value:
            source_counter.count += item.values
            if source_counter.count <= source_counter.capacity:
                final_merchant_list.append(item)
            else:
                source_counter.count -= item.values
                general_counter -= item.values
                continue
    total_values_selection.append(general_counter)


create_merchant_list(target, '[RETAIL]',
                     ProductAttributeFiles_retail, total_values_retail)

select_by_rank_language_limit(
    retail_by_rank, ProductAttributeFiles_retail, maximum_value,
    final_retail_list, total_values_re_sel)
if int(total_values_re_sel[0]) < maximum_value:
    pending_values = maximum_value - int(total_values_re_sel[0])
    create_merchant_list(target, '[THIRD_PARTY]',
                         ProductAttributeFiles_3P, total_values_3P)
    select_by_rank_language_limit(
        TP_by_rank, ProductAttributeFiles_3P, pending_values,
        final_3P_list, total_values_3p_sel)
    final_list = itertools.chain(final_retail_list, final_3P_list)
else:
    final_list = final_retail_list

print("Please select a directory for the output file")
root = tkinter.Tk()
root.withdraw()
directorypath = filedialog.askdirectory()

outputfilepath = str(directorypath) + \
    "\selection_for_" + str(target) + ".txt"

filepath = open(outputfilepath, "w+")

filepath.write(
    "Batch	WorldServer project	Activity	Project		\
    products		GL	Language pair					Values\n")

for item in final_list:
    language_pair = str(item.source_MP) + "-" + str(item.target_locale)
    if item.attribute in prefill_attribute_list:
        attribute_value = "Prefilled file"
    else:
        attribute_value = "Non-prefilled filed"
    filepath.write(str(item.name) + "	" + str(item.url) +
                   "	" + str(attribute_value) +
                   "	Attribute Translation		" + str(item.products) +
                   "		" + str(item.attribute) + "	" +
                   str(language_pair).upper() + "					" +
                   str(item.values) + "\n")
    id_list.append(item.name)

filepath.close()

print("Output file is ready")

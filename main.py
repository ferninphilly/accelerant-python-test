# import pandas as pd
# from fuzzywuzzy import fuzz


# f = 'input.csv'

# # List of valid car names
# cars = ['Alligator', 'Bear', 'Cat', 'Dog', 'Elephant', 'Frog', 'Giraffe', 'Horse', 'Iguana', "Jaguar", "Kangaroo"] # ["Audi", "BMW", "Honda"]

# # Load CSV data into a DataFrame
# a = pd.read_csv(f)

# # Print the loaded CSV data
# print('Original CSV Data:')
# print(a)

# # Print each column and its new name if renamed
# for x in a.columns:
#     for valid_name in cars:
#         if x == valid_name:
#             print(f'{x} : Valid')
#         if fuzz.ratio(x.lower(), valid_name.lower()) >= 80:
#             print(f'{x} >> {valid_name}')

# #todo... write out new file

from CSVRewriter import CSVRewriter

if __name__ == "__main__":
    f = 'imput.csv'
    cars = ['Alligator', 'Bear', 'Cat', 'Dog', 'Elephant', 'Frog', 'Giraffe', 'Horse', 'Iguana', "Jaguar", "Kangaroo"]
    rewriter = CSVRewriter(f, cars)
    rewriter.to_csv()
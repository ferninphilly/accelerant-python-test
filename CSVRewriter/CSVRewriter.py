import pandas as pd
from pandas import DataFrame
from fuzzywuzzy import fuzz
import os

class CSVRewriter():
    def __init__(self, filename:str, correct_headers:list[str]):
        self.filename = filename
        self.correct_headers = correct_headers
        self.file_data = self.sanitize_csv_inputs()
        self.correct_headers = self.santize_headers_inputs()
               
    def sanitize_csv_inputs(self)->DataFrame:
        """Sanitizes the inputs and catches errors to put out user friendly messages

        Returns:
            DataFrame: The result of reading the CSV file
        """
        try:
            return pd.read_csv(self.filename, header=None)
        except FileNotFoundError:
            print(f"File '{self.filename}' not found. Check your csv directory input")
            os._exit(1)
        except ValueError:
            print(f"File '{self.filename}' is not a valid CSV file. {type(self.filename)} is not a valid type. Try a string.")
            os._exit(1)
        except Exception as e:
            print(f"An error occurred: {e}")
            os._exit(1)
            
    def santize_headers_inputs(self)-> list[str]:
        if not isinstance(self.correct_headers, list):
            print(f"Headers must be a list of strings. {type(self.correct_headers)} is not a valid type.")
            os._exit(1)
        headers_bool = [isinstance(x, str) for x in self.correct_headers]
        if False in headers_bool:
            print("One or more headers are not strings. Please correct and try again.")
            os._exit(1)
        return self.correct_headers
    
    def get_index_of_headers(self)->int:
        """We want to get the index of the row that contains the headers. A bit of guesswork here,
        but we have the most likely outcome. Finds the row with the most strings.

        Returns:
            int: The index of the headers row
        """
        #Let's find our headers row by searching for strings that don't match if upper and lower case
        boolean_lists = self.file_data.map(lambda x: x.lower() != x.upper() if isinstance(x,str) else x).values.tolist()
        #Now lets get our most likely header (the row with the most strings)
        indexlist = []
        for row in boolean_lists:
            indexlist.append(len([x for x in row if x is True]))
        if len(set(indexlist)) == 0:
            print("No headers found in the CSV file")
            return None
        return pd.Series(indexlist).idxmax()
    
        
    def get_and_clean_headers(self)->list[str]:
        """Gets the headers from the CSV file

        Returns:
            list[str]: A list of headers that has been cleaned up from excess quotes and symbols
        """
        headers_index = self.get_index_of_headers()
        if headers_index is None:
            return None
        headers_unclean = self.file_data.iloc[headers_index].values.tolist()
        headers_without_improper_types = []
        for x in headers_unclean:
            if isinstance(x, str):
                headers_without_improper_types.append(x.strip())
            else:
                headers_without_improper_types.append("Unknown")
        for idx, x in enumerate(headers_without_improper_types):
            #Let's get rid of anything with a comma in it from the previous run
            if x == "Unknown" and "," in headers_without_improper_types[idx-1]:
                del(headers_without_improper_types[idx])
        headers_correct_split = [x for xs in headers_without_improper_types for x in xs.split(",")]
        headers_without_excess_quotes = [x.replace('"', "") for x in headers_correct_split]
        return [x.replace('\\', "") for x in headers_without_excess_quotes]
        
    def match_columns(self)->DataFrame:
        """Matches the headers from the file to the correct headers. Uses fuzzy matching to find close matches.
        Prints out the results of the matching process.
        """
        headers_from_file = self.get_and_clean_headers()
        for idx, x in enumerate(headers_from_file):
            for valid_name in self.correct_headers:
                if x == valid_name:
                    print(f'{x} : Valid')
                    headers_from_file[idx] = valid_name
                    break
                if fuzz.ratio(x.lower(), valid_name.lower()) >= 80:
                    headers_from_file[idx] = valid_name
                    print(f'{x} >> {valid_name}')
                    break        
        return headers_from_file

    def rename_columns(self)->None:
        """Renames the columns of the DataFrame to the correct headers
        """
        headers_index = self.get_index_of_headers()
        if headers_index is None:
            raise ValueError("No headers found in the CSV file")
        corrected_headers = self.match_columns()
        updated_file_data = self.drop_rows([self.get_index_of_headers()])
        #Now let's get rid of empty rows
        updated_file_data.dropna(how='all', inplace=True)
        #Now let's rename the columns
        try:
            updated_file_data.columns = corrected_headers
        except ValueError:
            print("The number of columns in the CSV file does not match the number of headers provided. Please check your inputs.")
            os._exit(1)
        self.file_data = updated_file_data
    
    def drop_rows(self, rows_to_drop:list[int])->DataFrame:
        """Drops rows from the read csv frame based on inputs
        Returns:
            DataFrame: The dataframe without the rows we wanted dropped
        """
        for row in rows_to_drop:
            if row < 0 or row > len(self.file_data):
                print(f"Row {row} is out of bounds. Please check your inputs")
                break
            self.file_data.drop(self.file_data.index[row], inplace=True)
        return self.file_data
    
    def to_csv(self)->None:
        """Writes the updated DataFrame to a new CSV file
        """
        self.rename_columns()
        self.file_data.to_csv(f"{self.filename}_updated.csv", index=False)
        

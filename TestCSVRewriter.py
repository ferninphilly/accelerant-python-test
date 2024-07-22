import pytest
from pandas import DataFrame
from fuzzywuzzy import fuzz
from unittest.mock import MagicMock

# Assuming the class containing match_columns is named CSVRewriter
from CSVRewriter.CSVRewriter import CSVRewriter

def test_sanitize_inputs():
    filename = 1
    correct_headers = ["1", "2", "3"]
    with pytest.raises(ValueError, match=f"File '{filename}' is not a valid CSV file. {type(filename)} is not a valid type. Try a string."):
        CSVRewriter(filename, correct_headers)
    filename = "invalid_file.csv"
    with pytest.raises(FileNotFoundError, match=f"File '{filename}' not found. Check your csv directory input"):
        CSVRewriter(filename, correct_headers)
    filename = "imput.csv"
    correct_headers = 123
    with pytest.raises(TypeError, match=f"Headers must be a list of strings. {type(correct_headers)} is not a valid type."):
        CSVRewriter(filename, correct_headers)
    correct_headers = ["1", 2, "3"]
    with pytest.raises(ValueError, match="One or more headers are not strings. Please correct and try again."):
        CSVRewriter(filename, correct_headers)

def test_get_index_of_headers():
    csv_rewriter = CSVRewriter("imput.csv", ["1","2","3"])
    csv_rewriter.file_data = DataFrame([["a", "b", "b"], [4, 5, 6]])
    assert csv_rewriter.get_index_of_headers() == 0
    csv_rewriter.file_data = DataFrame([[1, 2, 3], ["a", "b","c"]])
    assert csv_rewriter.get_index_of_headers() == 1
    csv_rewriter.file_data = DataFrame([[1, 2, 3], [4, 5, 6]])
    assert csv_rewriter.get_index_of_headers() == None
    

def test_get_and_clean_headers():
    csv_rewriter = CSVRewriter("imput.csv", ["1", "2", "3"])
    csv_rewriter.file_data = DataFrame([["a", "b", "b"], [4, 5, 6]])
    assert csv_rewriter.get_and_clean_headers() == ["A", "B", "B"]
    csv_rewriter.file_data = DataFrame([[1, 2, 3], ["a", "b", "c"]])
    assert csv_rewriter.get_and_clean_headers() == ["A", "B", "C"]
    csv_rewriter.file_data = DataFrame([[1, 2, 3], [4, 5, 6]])
    assert csv_rewriter.get_and_clean_headers() == None
    
@pytest.mark.parametrize(
    "headers_from_file, correct_headers, expected_output, expected_prints",
    [
        # Happy path tests
        (["name", "age"], ["name", "age"], ["name", "age"], ["name : Valid", "age : Valid"]),
        (["Name", "Age"], ["name", "age"], ["name", "age"], ["Name >> name", "Age >> age"]),
        
        # Edge cases
        (["nme", "ag"], ["name", "age"], ["name", "age"], ["nme >> name", "ag >> age"]),
        ([""], ["name", "age"], [""], []),
        (["name", "age", "gender"], ["name", "age"], ["name", "age", "gender"], ["name : Valid", "age : Valid"]),
        
        # Error cases
        (["unknown"], ["name", "age"], ["unknown"], []),
        (["name", "unknown"], ["name", "age"], ["name", "unknown"], ["name : Valid"]),
    ],
    ids=[
        "exact_match",
        "case_insensitive_match",
        "fuzzy_match",
        "empty_header",
        "extra_header",
        "no_match",
        "partial_match"
    ]
)
def test_match_columns(headers_from_file, correct_headers, expected_output, expected_prints, capsys):
    
    # Arrange
    csv_rewriter = CSVRewriter("imput.csv", ["1","2","3"])
    csv_rewriter.get_and_clean_headers = MagicMock(return_value=headers_from_file)
    csv_rewriter.correct_headers = correct_headers

    # Act
    result = csv_rewriter.match_columns()

    # Assert
    assert result == expected_output
    captured = capsys.readouterr()
    for expected_print in expected_prints:
        assert expected_print in captured.out
        
def test_rename_columns():
    csv_rewriter = CSVRewriter("imput.csv", ["1", "2", "3"])
    csv_rewriter.file_data = DataFrame([["a", "b", "b"], [4, 5, 6]])
    csv_rewriter.match_columns = MagicMock(return_value=["A", "B", "B"])
    csv_rewriter.rename_columns()
    assert list(csv_rewriter.file_data.columns) == ["A", "B", "B"]
    
def test_drop_rows():
    csv_rewriter = CSVRewriter("imput.csv", ["1", "2", "3"])
    csv_rewriter.file_data = DataFrame([["a", "b", "b"], [4, 5, 6], ["a", "b", "b"]])
    file_data = csv_rewriter.drop_rows([1])
    assert len(file_data) == 2
    assert list(file_data.index) == [0, 2]
    
def test_to_csv():
    csv_rewriter = CSVRewriter("imput.csv", ["1", "2", "3"])
    csv_rewriter.file_data = DataFrame([["a", "b", "b"], [4, 5, 6], ["a", "b", "b"]])
    csv_rewriter.to_csv("test_output.csv")
    with open("test_output.csv", "r") as f:
        content = f.read()
    assert content == "A,B,B\n4,5,6\na,b,b\n"
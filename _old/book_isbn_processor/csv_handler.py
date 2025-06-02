import csv
import os


class CSVHandler:
    """CSV file handler for reading and writing book ISBN data."""

    def __init__(self, file_path: str):
        """
        Initialize the CSVHandler with the given file path.
        args:
            file_path (str): Path to the CSV file.
        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is empty or has no valid headers.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        self.file_path = file_path

    def read_csv(
        self,
        isbn_column_name: str | None = None,
        isbn_column_index: int | None = None,
        skip_header: bool = True,
        encoding: str = "utf-8",
    ) -> list[dict]:
        """
        Read the CSV file and return a list of dictionaries representing each row.
        args:
            isbn_column_name (str | None): Name of the column containing ISBNs.
            isbn_column_index (int | None): Index of the column containing ISBNs.
            skip_header (bool): Whether to skip the header row.
            encoding (str): Encoding of the CSV file.
        Returns:
            list[dict]: List of dictionaries where each dictionary represents a row in the CSV.
        Raises:
            ValueError: If both isbn_column_name and isbn_column_index are None.
        """
        isbns: list[str] = []

        if isbn_column_name is not None:
            skip_header = True

        try:
            with open(self)

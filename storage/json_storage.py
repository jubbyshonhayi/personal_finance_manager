import json
from pathlib import Path


class JsonStorage:
    """
    Handles reading and writing application data to JSON files.
    """

    def ensure_file_exists(self, file_path: str) -> None:
        """Ensure that the specified JSON file exists."""

        try:
            path = Path(file_path)
            
            if path.exists():
                return
            
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with path.open("w", encoding="utf-8") as file:
                json.dump([], file)

        except OSError as error:
            raise OSError(f"Unable to create or access '{file_path}'.") from error
        
        
    def load_data(self, file_path: str) -> list:
        """Loads and returns data from the specified JSON file."""

        try:
            self.ensure_file_exists(file_path)

            path = Path(file_path)

            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            return data

        except json.JSONDecodeError as error:
            raise ValueError(f"The JSON file '{file_path}' contains invalid data.") from error

        except OSError as error:
            raise OSError(f"Unable to read data from '{file_path}'.") from error
        

    def save_data(self, file_path: str, data: list) -> None:
        """Saves the provided data to the specified JSON file."""

        try:
            self.ensure_file_exists(file_path)
            path = Path(file_path)

            with path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

        except OSError as error:
            raise OSError(f"Unable to save data to '{file_path}'.") from error
        
    
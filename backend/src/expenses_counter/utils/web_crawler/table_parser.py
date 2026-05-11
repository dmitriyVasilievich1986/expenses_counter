"""Table parser for extracting and processing product data from HTML tables."""

__all__ = ("TableParser",)

from io import StringIO

import pandas as pd


class TableParser(pd.DataFrame):
    """Parser for HTML tables containing product information.

    Extends pandas DataFrame to parse HTML tables with Serbian column names
    and convert them to a standardized format with English column names
    and properly formatted numeric values.

    Attributes:
        Inherits all pandas DataFrame attributes with columns:
        - name (str): Product name
        - quantity (float): Product quantity
        - unit_price (float): Unit price with VAT

    """

    def __init__(self, html: str) -> None:
        """Initialize TableParser by parsing HTML and extracting the first table.

        Args:
            html: HTML string containing one or more tables

        Raises:
            ValueError: If no tables are found in the HTML

        """
        html_file_like = StringIO(html)
        dfs = pd.read_html(html_file_like)
        if len(dfs) == 0:
            raise ValueError("No tables found")

        df = dfs[0]
        df = self._rename_columns(df)
        df = self._convert_dataframe(df)
        super().__init__(df)  # type: ignore[call-arg]

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename Serbian column names to English equivalents.

        Maps Serbian table headers to standardized English column names:
        - "Назив" -> "name"
        - "Количина" -> "quantity"
        - "Јед. цена са ПДВ" -> "unit_price"

        Args:
            df: DataFrame with Serbian column names

        Returns:
            DataFrame with English column names

        """  # noqa: RUF002
        return df.rename(columns={"Назив": "name", "Количина": "quantity", "Јед. цена са ПДВ": "unit_price"})

    def _convert_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter columns and convert numeric values to proper float format.

        Selects only the name, quantity, and unit_price columns, then converts
        the quantity and unit_price values from Serbian number format to floats.

        Args:
            df: DataFrame with renamed columns

        Returns:
            DataFrame with filtered columns and converted numeric values

        """
        df = df[["name", "quantity", "unit_price"]].copy()
        df["quantity"] = [self.convert_float(x) for x in df["quantity"]]
        df["unit_price"] = [self.convert_float(x) for x in df["unit_price"]]
        return df

    @staticmethod
    def convert_float(value: str) -> float:
        """Convert Serbian number format to float.

        Serbian number format uses:
        - "." as thousands separator
        - "," as decimal separator

        This method converts the format by:
        1. Replacing "." with "_" (temporary placeholder)
        2. Replacing "," with "." (making it standard decimal)
        3. Converting to float
        4. If no decimal point exists, divides by 100 (assumes value is in cents)

        Args:
            value: String representation of a number in Serbian format

        Returns:
            Float representation of the number

        Examples:
            >>> TableParser.convert_float("1.234,56")
            1234.56
            >>> TableParser.convert_float("100")
            1.0
            >>> TableParser.convert_float("50,5")
            50.5

        """
        value = str(value).replace(".", "_").replace(",", ".")
        if "." in value:
            return float(value)
        return float(value) / 100

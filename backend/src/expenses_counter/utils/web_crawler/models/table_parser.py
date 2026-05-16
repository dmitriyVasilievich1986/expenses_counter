"""Table parser for extracting and processing product data from HTML tables."""

__all__ = ("TableParser",)

from io import StringIO

import pandas as pd


class TableParser(pd.DataFrame):
    """Line-item table parsed from the first ``<table>`` in receipt HTML."""

    def __init__(self, html: str) -> None:
        """Build a DataFrame from the first HTML table and normalize columns.

        Args:
            html (str): Raw HTML containing at least one product table.

        Raises:
            ValueError: If the HTML contains no parseable tables.

        """
        html_file_like = StringIO(html)
        dfs = pd.read_html(html_file_like)
        if len(dfs) == 0:
            raise ValueError("No tables found")

        df = dfs[0]
        df = self._convert_dataframe(df)
        super().__init__(df)  # type: ignore[call-arg]

    def _convert_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Keep name/quantity/price columns and parse numeric cells.

        Args:
            df (pd.DataFrame): First table returned by ``pandas.read_html``.

        Returns:
            pd.DataFrame: Subset with normalized ``Quantity`` and
                ``Gross Unit Price`` values.

        """
        df = df[["Name", "Quantity", "Gross Unit Price"]].copy()
        df["Quantity"] = [self.convert_float(x) for x in df["Quantity"]]
        df["Gross Unit Price"] = [self.convert_float(x) for x in df["Gross Unit Price"]]
        return df

    @staticmethod
    def convert_float(value: str) -> float:
        """Parse a receipt-style numeric string into a float.

        Commas are replaced with underscores (thousands). Strings without a
        decimal point are treated as whole minor units and divided by 100.

        Args:
            value (str): Cell text or value coerced via ``str``.

        Returns:
            float: Parsed amount.

        """
        value = str(value).replace(",", "_")
        if "." in value:
            return float(value)
        return float(value) / 100

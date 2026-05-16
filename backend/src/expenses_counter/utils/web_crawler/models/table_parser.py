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
        df = self._rename_columns(df)
        df = self._convert_dataframe(df)
        df = self._add_total_column(df)
        super().__init__(df)  # type: ignore[call-arg]

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map receipt-specific column labels to internal names.

        Keeps parsing stable when the source site renames header cells.

        Args:
            df (pd.DataFrame): Table as returned by ``read_html``.

        Returns:
            pd.DataFrame: Same rows with unified column names.

        """
        return df.rename(
            columns={
                "Name": "name",
                "Quantity": "quantity",
                "Gross Unit Price": "unit_price",
            }
        )

    def _convert_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Select product columns and coerce numeric cells to floats.

        Args:
            df (pd.DataFrame): Frame with ``name``, ``quantity``, and
                ``unit_price`` columns after renaming.

        Returns:
            pd.DataFrame: Subset of columns with ``quantity`` and
                ``unit_price`` parsed with ``convert_float``.

        """
        df = df[["name", "quantity", "unit_price"]].copy()
        df["quantity"] = [self.convert_float(x) for x in df["quantity"]]
        df["unit_price"] = [self.convert_float(x) for x in df["unit_price"]]
        return df

    def _add_total_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add a total column to the dataframe.

        Args:
            df (pd.DataFrame): Frame with ``quantity`` and ``unit_price`` columns.

        Returns:
            pd.DataFrame: Frame with a ``total`` column.

        """
        df["total"] = df["quantity"] * df["unit_price"]
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

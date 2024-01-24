import re

from app.entities.pdf_reader import PDFReader
from app.strategies.parser_strategy import ParserStrategy


class InterParser(ParserStrategy):
    def __init__(self) -> None:
        self.regex_pattern = (
            r"(^\d{2}\s[a-z]{3}\s\d{4})\s(.+?)\s((?:\+\s)?R\$\s\d*\,\d*$)"
        )

    def __format_date(self, date: str) -> str:
        date, month_abbreviation, year = date.split(" ")
        months_abbreviations = {
            "jan": "01",
            "fev": "02",
            "mar": "03",
            "abr": "04",
            "mai": "05",
            "jun": "06",
            "jul": "07",
            "ago": "08",
            "set": "09",
            "out": "10",
            "nov": "11",
            "dez": "12",
        }
        month = months_abbreviations[month_abbreviation]
        return f"{date}/{month}/{year}"

    def _is_transaction(self, line: str) -> bool:
        return (
            bool(re.match(self.regex_pattern, line))
            and "Pagamento On Line" not in line
        )

    def _parse_transaction(self, line: str) -> dict[str, str]:
        matches = re.search(self.regex_pattern, line)
        if not matches:
            return {}
        return {
            "Data": self.__format_date(matches.group(1)),
            "Descrição": matches.group(2).replace("\x00", ""),
            "Valor": matches.group(3).replace(" ", "").replace("R$", ""),
        }

    def parse_transactions(
        self, pdf_reader: PDFReader
    ) -> list[dict[str, str]]:
        pdf_pages = pdf_reader.get_pages()
        pdf_text = pdf_reader.extract_text(pdf_pages[1:-3])
        lines = pdf_text.splitlines()
        transaction_lines = list(filter(self._is_transaction, lines))
        transactions = list(map(self._parse_transaction, transaction_lines))
        return transactions

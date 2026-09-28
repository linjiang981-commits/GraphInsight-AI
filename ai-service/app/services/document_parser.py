from pathlib import Path

from pypdf import PdfReader
import re


class DocumentParser:

    def parse(
    self,
    file_path: str | Path
    ) -> str:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

        suffix = path.suffix.lower()

        if suffix in {".txt", ".md"}:
            text = self._parse_text(path)

        elif suffix == ".pdf":
            text = self._parse_pdf(path)

        else:
            raise ValueError(
                f"Unsupported file type: {suffix}"
            )

        return self._clean_text(text)

    def _parse_text(
        self,
        path: Path
    ) -> str:

        return path.read_text(
            encoding="utf-8"
        )

    def _parse_pdf(
        self,
        path: Path
    ) -> str:

        reader = PdfReader(path)

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text()

            if not text:
                continue

            pages.append(
                f"\n[Page {page_number}]\n{text}"
            )

        return "\n".join(pages)

    def _clean_text(
        self,
        text: str
    ) -> str:

        text = text.replace(
            "\r\n",
            "\n"
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        text = re.sub(
            r"\n{3,}",
         "\n\n",
            text
        )

        return text.strip()
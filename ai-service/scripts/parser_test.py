from pathlib import Path

from app.services.document_parser import (
    DocumentParser
)


parser = DocumentParser()


base_path = (
    Path(__file__).resolve()
    .parents[1]
    / "data"
    / "sample_docs"
)


files = [
    "tcp_troubleshooting.txt",
    "network_guide.md",
    "network_manual.pdf"
]


for file_name in files:

    file_path = base_path / file_name

    text = parser.parse(file_path)

    print(
        "\n============================"
    )

    print(
        "FILE:",
        file_name
    )

    print(
        "CHARACTERS:",
        len(text)
    )

    print(
        "\nCONTENT:\n"
    )

    print(text[:500])
import argparse

from chatbot.rag import PersonalDataRag


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest personal data and docs into Qdrant.")
    parser.add_argument("path", help="Path to a .pdf/.txt/.md file or a directory containing RAG files.")
    args = parser.parse_args()

    count = PersonalDataRag().ingest_path(args.path)
    print(f"Ingested {count} personal data chunks.")


if __name__ == "__main__":
    main()

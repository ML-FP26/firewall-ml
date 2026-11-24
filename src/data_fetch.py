"""Download the UCI Internet Firewall Data (id 542) into data/raw/firewall.csv."""

import argparse
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

UCI_ID = 542
ZIP_URL = "https://archive.ics.uci.edu/static/public/542/internet+firewall+data.zip"
RAW_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "firewall.csv"

# Original UCI headers, exactly as listed in docs/00-shared-contracts.md section 3.1.
EXPECTED_HEADERS = [
    "Source Port",
    "Destination Port",
    "NAT Source Port",
    "NAT Destination Port",
    "Action",
    "Bytes",
    "Bytes Sent",
    "Bytes Received",
    "Packets",
    "Elapsed Time (sec)",
    "pkts_sent",
    "pkts_received",
]
EXPECTED_ROWS = 65532


def download_table() -> pd.DataFrame:
    """Return the UCI table (features + target) with the original headers.

    Downloads UCI's static zip, because fetch_ucirepo(id=542) raises
    DatasetNotFoundError (see docs/CONTRACT_CHANGES.md, v1.1).
    """
    with urllib.request.urlopen(ZIP_URL, timeout=60) as response:
        payload = response.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        csv_names = [name for name in archive.namelist() if name.endswith(".csv")]
        if len(csv_names) != 1:
            raise ValueError(f"Expected exactly one csv in the zip, found {csv_names}.")
        return pd.read_csv(io.BytesIO(archive.read(csv_names[0])))


def check_headers(table: pd.DataFrame) -> None:
    """Raise ValueError if the table headers differ from the contract."""
    found = set(table.columns)
    expected = set(EXPECTED_HEADERS)
    if found != expected:
        raise ValueError(
            "Header mismatch with contract 3.1. "
            f"Missing: {sorted(expected - found)}. Unexpected: {sorted(found - expected)}."
        )


def fetch(force: bool = False) -> Path:
    """Download the raw table if needed and return the path to firewall.csv.

    An existing file is left untouched unless force is True.
    """
    if RAW_PATH.exists() and not force:
        print(f"{RAW_PATH} already exists, not overwriting (use --force).")
        return RAW_PATH

    table = download_table()
    check_headers(table)
    table = table[EXPECTED_HEADERS]

    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(RAW_PATH, index=False)

    print(f"Wrote {RAW_PATH}")
    print(f"Rows: {len(table)} (UCI listing says {EXPECTED_ROWS})")
    if len(table) != EXPECTED_ROWS:
        print(
            f"WARNING: row count {len(table)} differs from {EXPECTED_ROWS}. "
            "Tell the group before anyone builds on this file."
        )
    return RAW_PATH


def main() -> int:
    """Run the CLI and return the process exit code."""
    parser = argparse.ArgumentParser(description="Fetch the UCI firewall data.")
    parser.add_argument("--force", action="store_true", help="overwrite existing file")
    args = parser.parse_args()
    try:
        fetch(force=args.force)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

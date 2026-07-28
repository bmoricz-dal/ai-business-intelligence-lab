"""Download and verify the two official UKBDS 2026 ODS workbooks."""

from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIRECTORY = (
    ROOT / "data/raw/dsit/uk_business_data_survey/2026-06-18"
)

SOURCES = {
    "DSIT_UK_Business_Data_Survey_2026_tables.ods": {
        "url": (
            "https://assets.publishing.service.gov.uk/media/"
            "6a2a919de50716856ed4aec0/"
            "DSIT_UK_Business_Data_Survey_2026_tables.ods"
        ),
        "sha256": (
            "3ad453b41eebcc2af853d3410d649761de2c4421cbe164ebdb79ca8b6f6ae53c"
        ),
    },
    "DSIT_UK_Business_Data_Survey_2026_tables_with_confidence_limits.ods": {
        "url": (
            "https://assets.publishing.service.gov.uk/media/"
            "6a2a8b4115f2a70fac7e5d6a/"
            "DSIT_UK_Business_Data_Survey_2026_tables_with_confidence_limits.ods"
        ),
        "sha256": (
            "1eff1276a0073927169941664d623a42c815c619c3e1c6ca0ebf7502a9fce4ef"
        ),
    },
}


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def download() -> None:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for filename, metadata in SOURCES.items():
        destination = OUTPUT_DIRECTORY / filename
        if destination.exists():
            actual = hashlib.sha256(destination.read_bytes()).hexdigest()
            if actual == metadata["sha256"]:
                print(f"verified existing: {filename}")
                continue
            raise ValueError(f"Existing file has the wrong fingerprint: {filename}")

        with urlopen(metadata["url"], timeout=60) as response:
            content = response.read()
        actual = sha256_bytes(content)
        if actual != metadata["sha256"]:
            raise ValueError(
                f"Fingerprint mismatch for {filename}: "
                f"expected {metadata['sha256']}, got {actual}"
            )

        with tempfile.NamedTemporaryFile(
            dir=OUTPUT_DIRECTORY, delete=False
        ) as temporary:
            temporary.write(content)
            temporary_path = Path(temporary.name)
        temporary_path.replace(destination)
        print(f"downloaded and verified: {filename}")


if __name__ == "__main__":
    download()

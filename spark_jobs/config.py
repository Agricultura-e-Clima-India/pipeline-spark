from pathlib import Path
import os

# Base paths for the data lake style layout.
PROJECT_ROOT = Path(os.environ.get("PIPELINE_HOME", Path(__file__).resolve().parents[1]))
DATA_DIR = PROJECT_ROOT / "data"
BRONZE_PATH = DATA_DIR / "bronze" / "dados_brutos.parquet"
SILVER_PATH = DATA_DIR / "silver" / "dados_limpos.parquet"
GOLD_DIR = DATA_DIR / "gold"


def ensure_data_dirs() -> None:
    """Create the data directories used across the pipeline."""
    for path in (DATA_DIR, BRONZE_PATH.parent, SILVER_PATH.parent, GOLD_DIR):
        path.mkdir(parents=True, exist_ok=True)

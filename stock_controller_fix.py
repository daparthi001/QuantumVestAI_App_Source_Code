"""Apply hotfix to stock_controller."""
import fileinput
import sys

TARGET_FILE = "ai-stock-platform/ui/controllers/stock_controller.py"

for line in fileinput.input(TARGET_FILE, inplace=True):
    if line.strip().startswith("import os"):
        print(line, end="")
        print(
            "# Default model to use for forecasts. Can be overridden via the"
            "\n# MODEL_ENSEMBLE environment variable which is mounted through the"
            "\n# application's ConfigMap in Kubernetes."
            "\nMODEL_ENSEMBLE = os.getenv('MODEL_ENSEMBLE', 'ADVANCED')"
        )
    elif "Query(MODEL_ENSEMBLE)" in line and "MODEL_ENSEMBLE" not in line.split():
        print(line.replace("Query(MODEL_ENSEMBLE)", "Query(MODEL_ENSEMBLE)"), end="")
    else:
        print(line, end="")

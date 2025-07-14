import os

# Ensure MODEL_ENSEMBLE is defined with a sensible default
if "MODEL_ENSEMBLE" not in os.environ:
    os.environ["MODEL_ENSEMBLE"] = "ADVANCED"
    print("MODEL_ENSEMBLE not set. Defaulting to 'ADVANCED'")
else:
    print(f"MODEL_ENSEMBLE set to {os.environ['MODEL_ENSEMBLE']}")

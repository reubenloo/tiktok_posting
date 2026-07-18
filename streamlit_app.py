# Streamlit entrypoint. Execute app.py on every Streamlit script run.
# Importing it would cache its module body and produce an empty rerun/session.

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")

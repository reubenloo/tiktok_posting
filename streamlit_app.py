# Streamlit Community Cloud entrypoint.
# Keep the main app implementation in app.py so local ops can still run `streamlit run app.py`.

from app import *  # noqa: F401,F403

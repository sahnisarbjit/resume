# Sarbjit Singh — Resume
- `Resume - Sarbjit Singh.pdf` — resume for applications.
- `build_resume.py` — content and layout. Edit this, then regenerate the PDF.
- `fonts/` — Exo 2 and Montserrat files used by the PDF.
- `original/` — the earlier Word resume. The script does not read it.

## Python Setup
```bash
virtualenv .venv
source .venv/bin/activate
```

## Generate
Uses Exo 2 and Montserrat from `fonts/`.
```bash
pip install fpdf2
python3 build_resume.py
```

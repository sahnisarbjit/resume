# Sarbjit Singh — Resume
- `resume.yaml` — name, contact, and every section. Edit this.
- `Resume.pdf` — generated resume for applications.
- `build_resume.py` — layout only. Reads `resume.yaml` and writes the PDF.
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
pip install fpdf2 pyyaml
python3 build_resume.py
```

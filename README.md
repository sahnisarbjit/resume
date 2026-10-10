# Sarbjit Singh — Resume
- `resume.yaml` — name, contact, and every section. Edit this.
- `Resume - <name>.pdf` — generated resume. The name comes from `name` in `resume.yaml`.
- `build_resume.py` — layout only. Reads `resume.yaml` and writes the PDF.
- `requirements.txt` — Python packages needed by `build_resume.py`.
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
pip install -r requirements.txt
python3 build_resume.py
```

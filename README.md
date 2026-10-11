# Sarbjit Singh — Resume

**[Download the latest resume (PDF)](https://github.com/sahnisarbjit/resume/releases/latest/download/Resume-SarbjitSingh.pdf)** · [All releases](https://github.com/sahnisarbjit/resume/releases)

- `resume.yaml` — name, contact, and every section. Edit this.
- `Resume-<Name>.pdf` — generated resume. The name comes from `name` in `resume.yaml`, with spaces removed.
- `build_resume.py` — layout only. Reads `resume.yaml` and writes the PDF.
- `requirements.txt` — Python packages needed by `build_resume.py`.
- `fonts/` — Exo 2 and Montserrat files used by the PDF.

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

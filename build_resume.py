"""Build the ATS-safe resume as a single-column PDF.

Content lives in resume.yaml. Fonts are Exo 2 and Montserrat in fonts/.

    python3 build_resume.py
"""

from pathlib import Path

import yaml
from fpdf import FPDF

HERE = Path(__file__).parent
CONTENT = HERE / "resume.yaml"
OUTPUT = HERE / "Resume.pdf"

ACCENT = (1, 127, 124)
INK = (38, 38, 38)
BODY = (89, 89, 89)

FONT_FILES = {
    ("Exo2", ""): "Exo2-Regular.ttf",
    ("Exo2Medium", ""): "Exo2-Medium.ttf",
    ("Montserrat", ""): "Montserrat-Regular.ttf",
    ("Montserrat", "B"): "Montserrat-SemiBold.ttf",
    ("Montserrat", "I"): "Montserrat-Italic.ttf",
}


def font_dir() -> Path:
    folder = HERE / "fonts"
    missing = [name for name in FONT_FILES.values() if not (folder / name).exists()]
    if missing:
        raise SystemExit(f"Missing font files in {folder}: {', '.join(missing)}")
    return folder


class Resume(FPDF):
    def __init__(self):
        super().__init__(format="A4", unit="mm")
        self.set_auto_page_break(auto=True, margin=14)
        self.set_margins(20, 15, 20)
        fonts = font_dir()
        for (family, style), filename in FONT_FILES.items():
            self.add_font(family, style, str(fonts / filename))

    def _rule(self):
        y = self.get_y()
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.3)
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(2.2)

    def _flow(self, spans, line_h, left, size=10):
        """Draw styled spans as wrapping text. Each span is (text, style, color)."""
        max_x = self.w - self.r_margin
        tokens = []
        for text, style, color in spans:
            words = text.split(" ")
            for index, word in enumerate(words):
                if index == 0:
                    if word:
                        tokens.append((word, style, color))
                else:
                    tokens.append((" " + word, style, color))
        while tokens and tokens[-1][0].strip() == "":
            tokens.pop()
        if tokens:
            word, style, color = tokens[-1]
            tokens[-1] = (word.rstrip(), style, color)

        self.set_x(left)
        for word, style, color in tokens:
            self.set_font("Montserrat", style, size)
            width = self.get_string_width(word)
            if self.get_x() + width > max_x + 0.2 and self.get_x() > left + 0.5:
                self.ln(line_h)
                self.set_x(left)
                # The token carries the space that separated it from the previous
                # word. Drop it at the start of a new line so the paragraph aligns.
                word = word.lstrip()
                if not word:
                    continue
                width = self.get_string_width(word)
            self.set_text_color(*color)
            self.cell(width, line_h, word)
        self.ln(line_h)

    def section(self, title):
        self.ln(3.2)
        self.set_font("Montserrat", "B", 13)
        self.set_text_color(*ACCENT)
        self.cell(0, 6.5, title, new_x="LMARGIN", new_y="NEXT")
        self._rule()

    def body(self, text, style="", size=10, color=BODY, gap=1.2):
        self._flow([(text, style, color)], line_h=4.6, left=self.l_margin, size=size)
        self.ln(gap)

    def bullet(self, label, text):
        line_h = 4.6
        mark = 4.2
        left = self.l_margin + mark
        with self.unbreakable():
            self.set_font("Montserrat", "", 10)
            self.set_text_color(*BODY)
            self.cell(mark, line_h, "•")
            self._flow(
                [(f"{label}: ", "B", ACCENT), (text, "", BODY)],
                line_h=line_h,
                left=left,
            )
            self.ln(0.7)

    def job(self, role):
        with self.unbreakable():
            self.ln(1.4)
            title = role["title"]
            dates = role["dates"]
            self.set_font("Montserrat", "", 10)
            date_w = self.get_string_width(dates)
            self.set_font("Montserrat", "B", 12)
            self.set_text_color(*INK)
            self.cell(self.epw - date_w - 4, 5.6, title)
            self.set_font("Montserrat", "", 10)
            self.set_text_color(*BODY)
            self.cell(date_w + 4, 5.6, dates, align="R", new_x="LMARGIN", new_y="NEXT")
            self.set_font("Montserrat", "B", 10.5)
            self.set_text_color(*INK)
            self.multi_cell(0, 4.8, role["company"])
            if role.get("context"):
                self.body(role["context"], style="I", gap=0.4)
            else:
                self.ln(0.4)
        for label, text in role["bullets"]:
            self.bullet(label, text)


def plain(value: str) -> str:
    """Folded YAML keeps a trailing newline. Collapse it to a single line."""
    return " ".join(value.split())


def load_resume(path: Path) -> dict:
    data = yaml.safe_load(path.read_text())
    missing = [key for key in ("name", "tagline", "contact", "sections") if key not in data]
    if missing:
        raise SystemExit(f"{path.name} is missing: {', '.join(missing)}")
    contact = data["contact"]
    for key in ("location", "phone", "email"):
        if key not in contact:
            raise SystemExit(f"{path.name} contact is missing {key}")
    return data


def render_section(pdf: Resume, section: dict) -> None:
    heading = section.get("heading")
    if not heading:
        raise SystemExit("Each section needs a heading")
    pdf.section(heading)
    if "roles" in section:
        for role in section["roles"]:
            role = dict(role)
            if role.get("context"):
                role["context"] = plain(role["context"])
            role["bullets"] = [
                (item["label"], plain(item["text"])) for item in role.get("bullets", [])
            ]
            pdf.job(role)
    elif "bullets" in section:
        for item in section["bullets"]:
            pdf.bullet(item["label"], plain(item["text"]))
    elif "degree" in section:
        pdf._flow(
            [
                (section["degree"], "B", ACCENT),
                (f", {section['school']}  |  {section['dates']}", "", BODY),
            ],
            line_h=4.8,
            left=pdf.l_margin,
        )
    elif "body" in section:
        pdf.body(plain(section["body"]), gap=0.2)
    else:
        raise SystemExit(f"Section {heading!r} has no body, roles, bullets, or degree")


def build():
    resume = load_resume(CONTENT)
    contact = resume["contact"]
    pdf = Resume()
    pdf.set_title(f"Resume - {resume['name']}")
    pdf.set_author(resume["name"])
    pdf.add_page()

    pdf.set_font("Exo2Medium", "", 26)
    pdf.set_text_color(*INK)
    pdf.cell(0, 11, resume["name"], align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Exo2", "", 10)
    pdf.set_text_color(*BODY)
    pdf.multi_cell(0, 4.6, resume["tagline"], align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.6)

    line = f"{contact['location']}   ·   {contact['phone']}   ·   {contact['email']}"
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Montserrat", "", 10)
    pdf.cell(0, 5, line, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    for section in resume["sections"]:
        render_section(pdf, section)

    pdf.output(str(OUTPUT))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build()

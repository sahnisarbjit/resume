"""Build the ATS-safe resume as a single-column PDF.

Content lives in resume.yaml. Fonts are Exo 2 and Montserrat in fonts/.

    python3 build_resume.py
"""

from pathlib import Path

import yaml
from fpdf import FPDF

HERE = Path(__file__).parent
CONTENT = HERE / "resume.yaml"

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
        self.set_auto_page_break(auto=True, margin=15)
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

    def _lines(self, spans, left, size=10):
        """Wrap styled spans into lines of (word, style, color, link, width) tokens."""
        max_w = self.w - self.r_margin - left
        tokens = []
        for span in spans:
            text, style, color = span[:3]
            link = span[3] if len(span) > 3 else ""
            words = text.split(" ")
            for index, word in enumerate(words):
                if index == 0:
                    if word:
                        tokens.append((word, style, color, link))
                else:
                    tokens.append((" " + word, style, color, link))
        while tokens and tokens[-1][0].strip() == "":
            tokens.pop()
        if tokens:
            word, style, color, link = tokens[-1]
            tokens[-1] = (word.rstrip(), style, color, link)

        lines = [[]]
        used = 0.0
        for word, style, color, link in tokens:
            self.set_font("Montserrat", style, size)
            width = self.get_string_width(word)
            if used + width > max_w + 0.2 and used > 0.5:
                # The token carries the space that separated it from the previous
                # word. Drop it at the start of a new line so the paragraph aligns.
                word = word.lstrip()
                if not word:
                    continue
                width = self.get_string_width(word)
                lines.append([])
                used = 0.0
            lines[-1].append((word, style, color, link, width))
            used += width
        return lines

    def _flow_height(self, spans, line_h, left, size=10):
        return len(self._lines(spans, left, size)) * line_h

    def _flow(self, spans, line_h, left, size=10):
        """Draw styled spans as wrapping text. Each span is (text, style, color)
        with an optional fourth element: a URL the text links to."""
        for line in self._lines(spans, left, size):
            self.set_x(left)
            for word, style, color, link, width in line:
                self.set_font("Montserrat", style, size)
                self.set_text_color(*color)
                self.cell(width, line_h, word, link=link)
            self.ln(line_h)

    def _keep_together(self, height):
        """Start a new page unless the next `height` mm fit on this one."""
        if self.will_page_break(height):
            self.add_page()

    def section(self, title):
        self.ln(3.2)
        self.set_font("Montserrat", "B", 13)
        self.set_text_color(*ACCENT)
        self.cell(0, 6.5, title, new_x="LMARGIN", new_y="NEXT")
        self._rule()

    def body(self, text, style="", size=10, color=BODY, gap=1.2):
        self._flow([(text, style, color)], line_h=4.6, left=self.l_margin, size=size)
        self.ln(gap)

    BULLET_LINE_H = 4.6
    BULLET_MARK = 4.2

    def _bullet_spans(self, label, text, url=None):
        spans = [(f"{label}: ", "B", ACCENT), (text, "", BODY)]
        if url:
            spans.append((" " + url.split("://", 1)[-1].rstrip("/"), "", ACCENT, url))
        return spans

    def bullet_height(self, label, text, url=None):
        left = self.l_margin + self.BULLET_MARK
        spans = self._bullet_spans(label, text, url)
        return self._flow_height(spans, self.BULLET_LINE_H, left) + 0.7

    def bullet(self, label, text, url=None):
        line_h = self.BULLET_LINE_H
        mark = self.BULLET_MARK
        self._keep_together(self.bullet_height(label, text, url))
        self.set_font("Montserrat", "", 24)
        self.set_text_color(*BODY)
        self.cell(mark, line_h, "•")
        self._flow(self._bullet_spans(label, text, url), line_h=line_h, left=self.l_margin + mark)
        self.ln(0.7)

    def link_line(self, urls, separator, line_h=5):
        """Centered, individually clickable links. The visible text is the URL
        without its scheme so ATS parsers still read the full address."""
        urls = list(urls)
        labels = [url.split("://", 1)[-1].rstrip("/") for url in urls]
        self.set_font("Exo2", "", 10)
        self.set_text_color(*BODY)
        sep_w = self.get_string_width(separator)
        total = sum(self.get_string_width(label) for label in labels)
        total += sep_w * (len(labels) - 1)
        self.set_x(self.l_margin + (self.epw - total) / 2)
        for index, (url, label) in enumerate(zip(urls, labels)):
            if index:
                self.cell(sep_w, line_h, separator)
            self.cell(self.get_string_width(label), line_h, label, link=url)
        self.ln(line_h)

    def job(self, role):
        self.set_font("Montserrat", "B", 10)
        company_lines = len(self.multi_cell(0, 4.8, role["company"], dry_run=True, output="LINES"))
        header_h = 1.4 + 5.6 + company_lines * 4.8 + 0.4
        if role.get("context"):
            header_h += self._flow_height([(role["context"], "I", BODY)], 4.6, self.l_margin)
        if role["bullets"]:
            header_h += self.bullet_height(*role["bullets"][0])
        self._keep_together(header_h)

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
        self.set_font("Montserrat", "B", 10)
        self.set_text_color(*INK)
        self.multi_cell(0, 4.8, role["company"])
        if role.get("context"):
            self.body(role["context"], style="I", gap=0.4)
        else:
            self.ln(0.4)
        for label, text, url in role["bullets"]:
            self.bullet(label, text, url)


def plain(value: str) -> str:
    """Folded YAML keeps a trailing newline. Collapse it to a single line."""
    return " ".join(value.split())


def load_resume(path: Path) -> dict:
    data = yaml.safe_load(path.read_text())
    missing = [key for key in ("name", "tags", "contact", "sections") if key not in data]
    if missing:
        raise SystemExit(f"{path.name} is missing: {', '.join(missing)}")

    if not data["tags"]:
        raise SystemExit(f"{path.name} tags missing")

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
                (item["label"], plain(item["text"]), item.get("url"))
                for item in role.get("bullets", [])
            ]
            pdf.job(role)
    elif "bullets" in section:
        for item in section["bullets"]:
            pdf.bullet(item["label"], plain(item["text"]), item.get("url"))
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
    pdf.set_subject("Resume (CV)")
    pdf.add_page()

    pdf.set_font("Exo2Medium", "", 26)
    pdf.set_text_color(*INK)
    pdf.cell(0, 11, resume["name"], align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Exo2", "", 10)
    pdf.set_text_color(*BODY)
    pdf.multi_cell(0, 5, "  |  ".join(resume["tags"]), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.6)

    line = "    |    ".join([contact['location'], contact['phone'], contact['email']])
    pdf.set_font("Exo2", "", 10)
    pdf.cell(0, 5, line, align="C", new_x="LMARGIN", new_y="NEXT")
    if resume.get("links"):
        pdf.link_line(resume["links"].values(), separator="    |    ")
    pdf.ln(2)

    for section in resume["sections"]:
        render_section(pdf, section)

    name_fmt = "".join(word.capitalize() for word in resume['name'].split())
    output = HERE / f"Resume-{name_fmt}.pdf"
    pdf.output(str(output))
    print(f"Wrote {output}")


if __name__ == "__main__":
    build()

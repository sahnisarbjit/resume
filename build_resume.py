"""Build the ATS-safe resume as a single-column PDF.

Content lives in this file. Fonts are Exo 2 and Montserrat in fonts/.

    python3 build_resume.py
"""

from pathlib import Path

from fpdf import FPDF

HERE = Path(__file__).parent
OUTPUT = HERE / "Resume.pdf"

ACCENT = (1, 127, 124)
INK = (38, 38, 38)
BODY = (89, 89, 89)

PHONE = "+91 94640 62104"
EMAIL = "sarbjit212@gmail.com"
LOCATION = "Mohali, Punjab, India"

TAGLINE = (
    "Technology Leader & Former CTO  |  Engineering Leadership  |  "
    "Full-Stack & Cloud Architecture"
)

SUMMARY = (
    "Technology leader and former Chief Technology Officer with 13+ years of experience "
    "building and scaling high-traffic content, e-commerce and SaaS platforms. Now a "
    "Senior Consultant at Webedia; previously CTO of Local Verticals until its merger "
    "into Webedia, owning architecture, AWS infrastructure and product delivery across "
    "a portfolio of websites. Earlier, Staff Software Engineer at Replicon on "
    "the Polaris PSA/PPM suite (React, GraphQL, ASP.NET). Hands-on full-stack leader "
    "with a track record of cutting page load times by 60%, building serverless media "
    "pipelines, and shipping recommendation and experimentation systems that keep "
    "readers engaged."
)

EXPERIENCE = [
    {
        "title": "Senior Consultant",
        "company": "Webedia",
        "dates": "March 2025 – Present",
        "context": "Joined Webedia when Local Verticals merged into the group.",
        "bullets": [
            ("Platform continuity", "Continue to own the CMS, e-commerce platform and AWS infrastructure for the former Local Verticals sites within Webedia."),
            ("Technical advisory", "Handled architecture, performance and cloud infrastructure for the merged portfolio."),
        ],
    },
    {
        "title": "Chief Technology Officer",
        "company": "Local Verticals (formerly Agile Media Lab)",
        "dates": "February 2023 – March 2025",
        "context": (
            "Agile Media Lab split in two: Webedia acquired the larger business, and "
            "the remaining sites continued as Local Verticals, which later merged "
            "into Webedia."
        ),
        "bullets": [
            ("Technology leadership", "Owned technology strategy, architecture and engineering delivery for a portfolio of content and e-commerce websites, from roadmap to production."),
            ("Platform ownership", "Ran and evolved the in-house next-generation CMS and e-commerce platform that powered every site in the portfolio."),
            ("Cloud & reliability", "Managed AWS infrastructure (Lambda, S3, CloudFront) with Nginx and Varnish caching and Docker/Jenkins deployments, keeping sites fast and hosting costs low."),
            ("Social distribution", "Extended the automated social sharing service to publish articles to Facebook, X (Twitter) and Bluesky."),
            ("Team & process", "Led and mentored the engineering team; set coding standards, code review and release practices."),
        ],
    },
    {
        "title": "Staff Software Engineer",
        "company": "Replicon",
        "dates": "April 2022 – February 2023",
        "bullets": [
            ("Polaris PSA/PPM", "Built features for Replicon's professional services automation suite, which helps enterprises manage resources, tasks, finances and project planning, using React, GraphQL and ASP.NET."),
        ],
    },
    {
        "title": "Technical Lead",
        "company": "Agile Media Lab Pvt. Ltd. / Aristeia Services (business later acquired by Webedia)",
        "dates": "July 2013 – April 2022",
        "context": "Led engineering for a portfolio of high-traffic content and e-commerce websites.",
        "bullets": [
            ("In-house CMS", "Architected and built a next-generation CMS and e-commerce web application used across all company sites."),
            ("Performance", "Cut page load time by 60% with device-specific page load optimizations."),
            ("Microservices", "Decoupled the database layer into a RESTful microservice API using Domain-Driven Design so the platform could scale."),
            ("Image pipeline", "Built a serverless thumbnail generator on AWS Lambda, S3 and CloudFront."),
            ("Recommendations", "Built a TF-IDF content recommendation engine to surface related articles."),
            ("Experimentation", "Built A/B testing for article titles and comments to find the best-performing variants."),
            ("Affiliate e-commerce", "Automated affiliate link handling across e-commerce sites and integrated Amazon product search into the CMS."),
            ("Social automation", "Built a fully automated service that shares new blog articles to social networks."),
            ("Newsletters", "Built a custom newsletter service that tracks and delivers the latest blog activity to subscribers."),
            ("Mobile", "Shipped an Android app built with React Native."),
        ],
    },
]

OPEN_SOURCE = [
    ("Async Tracer", "Node.js library for tracing async functions, conforming to the OpenTracing standard."),
]

SKILLS = [
    ("Languages", "JavaScript, PHP, Python"),
    ("Frontend & Mobile", "React, Next.js, React Native"),
    ("Backend & APIs", "Node.js, Laravel, Symfony, ASP.NET, GraphQL, RESTful APIs, Microservices, Domain-Driven Design"),
    ("Cloud & DevOps", "AWS (Lambda, S3, CloudFront), Docker, Jenkins, Nginx, Apache, Varnish"),
    ("Data, CMS & Ad Tech", "MySQL, WordPress, Prebid.js"),
    ("Product Engineering", "Web performance optimization, A/B testing, recommendation systems (TF-IDF)"),
    ("Leadership", "Technology strategy, team leadership & mentoring, strategic planning & execution, risk management"),
]

EDUCATION = ("Bachelor's degree", "Punjab Engineering College (PEC), Chandigarh", "2008 – 2012")

INTERESTS = "Bike riding, 3D printing & CNC, UAVs (drones), electronics, cooking, singing"

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


def build():
    pdf = Resume()
    pdf.set_title("Resume - Sarbjit Singh")
    pdf.set_author("Sarbjit Singh")
    pdf.add_page()

    pdf.set_font("Exo2Medium", "", 26)
    pdf.set_text_color(*INK)
    pdf.cell(0, 11, "Sarbjit Singh", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Exo2", "", 10)
    pdf.set_text_color(*BODY)
    pdf.multi_cell(
        0, 4.6, TAGLINE, align="C", new_x="LMARGIN", new_y="NEXT"
    )
    pdf.ln(0.6)

    contact = f"{LOCATION}   ·   {PHONE}   ·   {EMAIL}"
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Montserrat", "", 10)
    pdf.cell(0, 5, contact, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.section("Summary")
    pdf.body(SUMMARY, gap=0.2)

    pdf.section("Work Experience")
    for role in EXPERIENCE:
        pdf.job(role)

    pdf.section("Open Source")
    for label, text in OPEN_SOURCE:
        pdf.bullet(label, text)

    pdf.section("Technical Skills")
    for label, text in SKILLS:
        pdf.bullet(label, text)

    pdf.section("Education")
    degree, school, years = EDUCATION
    pdf._flow(
        [(degree, "B", ACCENT), (f", {school}  |  {years}", "", BODY)],
        line_h=4.8,
        left=pdf.l_margin,
    )

    pdf.section("Interests")
    pdf.body(INTERESTS, gap=0)

    pdf.output(str(OUTPUT))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build()

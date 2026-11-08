# Large Language Models — course site

Lecture notes, slides and labs for the 60-hour course at the Instituto de Matemática, UFRJ.
Published at <https://mirandola.github.io/llm-course>.

## Layout

| Path | What |
|---|---|
| `index.qmd` | course page: syllabus, weekly schedule, assessment |
| `notes/` | lecture notes (`.qmd` → HTML); one file per lecture, e.g. `M1P1.qmd` |
| `labs/` | lab sources (`.qmd`) and the generated notebooks (`*_student.ipynb`, `*_solutions.ipynb`) |
| `slides/` | beamer sources (`.tex`) and compiled PDFs |
| `tools/make_lab_versions.py` | builds the two notebooks from a lab `.qmd` |
| `lecture-notes.scss`, `mathjax-config.html` | site theme and MathJax setup |

## Working locally

```bash
quarto preview                      # live preview of the site
quarto render                       # builds _site/
python tools/make_lab_versions.py labs/lab2.qmd M2P2_lab2   # regenerates the two notebooks
```

Slides are compiled with `pdflatex` (twice) and the PDF committed next to the source.

## Publishing

Every push to `main` runs `.github/workflows/publish.yml`, which renders the site and
deploys it to GitHub Pages (source: GitHub Actions).

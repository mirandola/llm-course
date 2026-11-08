"""Builds the student and solutions notebooks from the single Quarto source.

    python make_lab_versions.py M1P2_lab1.qmd

Produces, next to the source:
    M1P2_lab1_student.qmd    - solution regions replaced by a stub
    M1P2_lab1_student.ipynb  - same, as a Jupyter notebook (Colab-ready)
    M1P2_lab1_solutions.ipynb- the full source as a notebook

Solution regions are delimited inside code cells by the lines
    # --- SOLUTION START ---
    # --- SOLUTION END ---
and are replaced, in the student version, by `raise NotImplementedError("TODO")`
with the same indentation. Everything else is identical in both versions.
`quarto convert` would produce the same notebooks from the .qmd files; this script
exists so that the notebooks can be generated without Quarto installed.
"""
import json, re, sys, pathlib

SOL_START, SOL_END = "# --- SOLUTION START ---", "# --- SOLUTION END ---"


def strip_solutions(code):
    out, skipping, indent = [], False, ""
    for line in code.split("\n"):
        s = line.strip()
        if s == SOL_START:
            skipping, indent = True, line[: len(line) - len(line.lstrip())]
            out.append(f'{indent}raise NotImplementedError("TODO")')
        elif s == SOL_END:
            skipping = False
        elif not skipping:
            out.append(line)
    return "\n".join(out)


def split_cells(qmd):
    """Yields ('markdown', text) and ('code', text) in document order; drops the YAML header."""
    body = re.sub(r"\A---\n.*?\n---\n", "", qmd, count=1, flags=re.S)
    body = re.sub(r"<!--.*?-->\n?", "", body, flags=re.S)          # HTML comments
    pattern = re.compile(r"```\{python\}\n(.*?)```", re.S)
    pos = 0
    for m in pattern.finditer(body):
        md = body[pos:m.start()].strip("\n")
        if md.strip():
            yield "markdown", md
        yield "code", m.group(1).rstrip("\n")
        pos = m.end()
    tail = body[pos:].strip("\n")
    if tail.strip():
        yield "markdown", tail


def to_notebook(cells):
    nb_cells = []
    for kind, text in cells:
        if kind == "markdown":
            nb_cells.append({"cell_type": "markdown", "metadata": {}, "source": text})
        else:
            # Quarto cell options (#| label: ..., #| eval: false) become comments for Jupyter
            lines = text.split("\n")
            opts = [l for l in lines if l.startswith("#|")]
            code = "\n".join(l for l in lines if not l.startswith("#|")).lstrip("\n")
            if any("eval: false" in o for o in opts):
                code = "# (optional cell — uncomment to run)\n" + "\n".join("# " + l for l in code.split("\n"))
            nb_cells.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                             "outputs": [], "source": code})
    return {
        "cells": nb_cells,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                     "language_info": {"name": "python"}},
        "nbformat": 4, "nbformat_minor": 5,
    }


def main(src):
    src = pathlib.Path(src)
    qmd = src.read_text(encoding="utf-8")
    stem = src.stem

    student_qmd = re.sub(r"```\{python\}\n(.*?)```",
                         lambda m: "```{python}\n" + strip_solutions(m.group(1)) + "```",
                         qmd, flags=re.S)
    (src.parent / f"{stem}_student.qmd").write_text(student_qmd, encoding="utf-8")

    for name, text in [("solutions", qmd), ("student", student_qmd)]:
        nb = to_notebook(list(split_cells(text)))
        (src.parent / f"{stem}_{name}.ipynb").write_text(json.dumps(nb, indent=1, ensure_ascii=False),
                                                          encoding="utf-8")
        print(f"{stem}_{name}.ipynb: {len(nb['cells'])} cells")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "M1P2_lab1.qmd")

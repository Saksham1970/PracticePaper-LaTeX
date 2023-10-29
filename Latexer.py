# ----------------------------- CONFIG -----------------------------------------------------------


title = "ALGORITHM"  #! TITLE CHOSEN IN scrapper.py
skip_images = False  #! False IF DONT WANT OR ALREADY HAVE IMAGES
pdflatex = True  #! True IF YOU HAVE pdflatex

# ------------------------------- CODE -----------------------------------------------------------

# ? Imports
import os
import json
import requests
from PIL import Image
from io import BytesIO


# ? Load the Json file created by scrapper
with open(f"./{title}/{title}.json", "r") as f:
    final_details = json.load(f)

url = "https://practicepaper.in"


# ? Whole latex written in this string
latex = ""


latex += r"\documentclass{exam}" + "\n"
latex += r"\title{" + title + "}" + "\n"
latex += r"\date{}" + "\n"
latex += r"\usepackage{graphicx}" + "\n"
latex += r"\usepackage{amsmath}" + "\n"
latex += r"\usepackage{amssymb}" + "\n"
latex += r"\usepackage[T1]{fontenc}" + "\n"
latex += r"\newcommand\tab[1][1cm]{\hspace*{#1}}" + "\n"
latex += r"\begin{document}" + "\n"
latex += r"" + "\n"
latex += r"\maketitle" + "\n"


for topic in final_details:
    # ? Each topic has its own section
    latex += r"\section{" + topic + "}\n"

    # ? Questions
    latex += r"\begin{questions}" + "\n"

    # ? Question Text
    for question in final_details[topic]:
        latex += (
            f"\\question {question['text']} \\textbf" + "{[" + question["year"] + "]}\n"
        )

        # ? Download and insert image
        if question["image"]:
            if not skip_images:
                response = requests.get(url + question["image"])

                Image.open(BytesIO(response.content)).convert("RGB").save(
                    f"./{title}/" + question["number"] + ".jpg"
                )

            latex += f""" \\begin{'{figure}'}[!hb]
\\centering
\\includegraphics[width=0.5\linewidth,height=0.5\linewidth, keepaspectratio]{'{'+ question['number']+'.jpg' +'}'}
\\end{'{figure}'} \n"""

        # ? Answers
        latex += r"\begin{choices}" + "\n"
        for answer in question["answers"]:
            latex += r"\choice " + question["answers"][answer] + "\n\\newline\n"
        latex += r"\end{choices}" + "\n"

    latex += r"\end{questions}" + "\n"


# ? After all topics, a section for answers
latex += r"\section{" + "Answers" + "}\n"
for topic in final_details:
    latex += r"\subsection{" + topic + "}\n"
    latex += r"\begin{enumerate}" + "\n"
    for question in final_details[topic]:
        latex += r"\item " + f" {','.join(question['correct_ans'])}\n"
    latex += r"\end{enumerate}" + "\n"

latex += r"\end{document}" + "\n"

# ? Save the file in tex format
text_file = open(f"./{title}/{title}.tex", "w")
text_file.write(latex)
text_file.close()

# ? If pdflatex is available run its command to generate pdf
if pdflatex:
    cmd = r"pdflatex -quiet " + '"' + title + ".tex" + '"'
    os.chdir(f"./{title}")
    os.system(cmd)

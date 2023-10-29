# ----------------------------- CONFIG -----------------------------------------------------------

url = "https://practicepaper.in/gate-cse/algorithm"  #! URL OF THE TOPIC
title = "ALGORITHM"  #! TITLE YOU WANT TO SAVE AS


# ------------------------------- CODE -----------------------------------------------------------


# ? Imports
import requests
from bs4 import BeautifulSoup, Tag
import re
import json
import html
import os


current_page = 1

# ? list of dictionaries for the whole topic
total_total_details = []
while True:
    r = requests.get(f"{url}?page_no={current_page}")
    soup = BeautifulSoup(r.content, "html.parser")

    # ? list of dictionaries for a whole page
    total_details = []

    # ? Bloodline contains all the questions
    bloodline = soup.find("div", id="mtq_question_container-1")

    if not bloodline:
        break

    for ques in list(list(bloodline.children)[1].children):
        # ? If random Navigable String ignore
        if not isinstance(ques, Tag):
            continue

        # ? mtq_question is the class of questions
        if not ques.has_attr("class"):
            continue
        if ques.attrs["class"][0] != "mtq_question":
            continue

        # ? Dictionary that stores content
        ques_details = {
            "number": None,
            "text": None,
            "image": None,
            "answers": None,
            "correct_ans": None,
            "year": None,
            "topic": None,
        }

        for child in ques.children:
            if not isinstance(child, Tag):
                continue

            # ? Scraping year and topic
            if not child.has_attr("class"):
                if not ques_details["year"] and child.name == "a":
                    ques_details["year"] = child.text

                elif not ques_details["topic"] and child.name == "a":
                    ques_details["topic"] = (child.text).title()

                continue

            name = child.attrs["class"][0]

            if name == "mtq_question_heading_table":
                ques_details["number"] = child.text

            if name == "mtq_question_text":
                # ? Processing the question text

                # ? Inner HTML of the question text
                question_inner = child.encode_contents()

                # ? Removing tags and marking math part of the questions with $ math $
                question_inner = (
                    re.sub(
                        r"<.?span.*?>|\[.?latex\]",
                        r"$",
                        html.unescape(question_inner.decode("utf-8")),
                    )
                    .replace("<br/>", " \\newline ")
                    .replace("<noscript>", "")
                    .replace("</noscript>", "")
                    .replace("    ", r" \tab ")
                    .replace(r"\gt", ">")
                    .replace(r"\lt", "<")
                )

                # ? Processing the code part of the questions
                parts = re.split(r"<pre><code>|</code></pre>", question_inner)

                # ? Splitting into code and text part
                normal_text = parts[::2]
                code_text = parts[1::2]

                for i in range(len(code_text)):
                    code_text[i] = code_text[i].replace("\n", " \\newline ")

                for i in range(len(normal_text)):
                    normal_text[i] = normal_text[i].replace("\n", " ")

                # ? Merging them again
                question_inner = []
                for a, b in zip(normal_text, code_text):
                    question_inner.append(a)
                    question_inner.append(b)
                question_inner.append(normal_text[-1])

                question_inner = " \\newline ".join(question_inner)

                # ? Finding and storing the image url of the question image if available

                question_images = re.findall(r"<img.*?/>", question_inner)

                if question_images:
                    question_inner = re.sub(r"<img.*?/>", "", question_inner)

                    for image in question_images:
                        src_search = re.search(r"\/.*?\.jpg", image)
                        if src_search:
                            ques_details["image"] = src_search.group(0)
                            break

                # ? Splitting into code and math part
                parts = question_inner.split("$")
                normal_text = parts[::2]
                math_text = parts[1::2]

                # ? Doing some latex conversions
                for i in range(len(normal_text)):
                    normal_text[i] = (
                        normal_text[i]
                        .replace("_", r"\_")
                        .replace("{", r"\{")
                        .replace("}", r"\}")
                        .replace("%", r"\%")
                        .replace("#", r"\#")
                        .replace("&", r"\&")
                        .replace("^", r"\^{}")
                        .replace("\\left", "")
                        .replace("\\right", "")
                    )

                # ? Merging them back
                new_question = []
                for a, b in zip(normal_text, math_text):
                    new_question.append(a)
                    new_question.append(b)
                new_question.append(normal_text[-1])

                new_question = "$".join(new_question)

                ques_details["text"] = new_question

            if name == "mtq_answer_table":
                ans = {}
                corrects = []

                for grandchild in child.children:
                    if grandchild.name == "tr":
                        # ? ans_choice is a tag containing info about which choice this answer is
                        # ? ans_correct is a tag containing info if this choice is correct
                        # ? ans_value is a tag containing info about the write up of this choice
                        choice, ans_value = list(grandchild.children)
                        ans_choice, ans_correct = list(choice.children)
                        ans_value = list(ans_value.children)[0].encode_contents()

                        for choice in ans_choice:
                            # ? This is similar to question processing
                            ans_value = (
                                re.sub(
                                    r"<.?span.*?>",
                                    r"$",
                                    html.unescape(ans_value.decode("utf-8")),
                                )
                                .replace("<br/>", " \\newline ")
                                .replace("<noscript>", "")
                                .replace("</noscript>", "")
                                .replace(r"\gt", ">")
                                .replace(r"\lt", "<")
                                .replace("    ", r" \tab ")
                            )

                            parts = re.split(r"<pre><code>|</code></pre>", ans_value)
                            normal_text = parts[::2]
                            code_text = parts[1::2]

                            for i in range(len(code_text)):
                                code_text[i] = code_text[i].replace("\n", " \\newline ")

                            for i in range(len(normal_text)):
                                normal_text[i] = normal_text[i].replace("\n", " ")

                            ans_value = []
                            for a, b in zip(normal_text, code_text):
                                ans_value.append(a)
                                ans_value.append(b)
                            ans_value.append(normal_text[-1])

                            ans_value = " \\newline ".join(ans_value)

                            parts = ans_value.split("$")
                            normal_text = parts[::2]
                            math_text = parts[1::2]

                            for i in range(len(normal_text)):
                                normal_text[i] = (
                                    normal_text[i]
                                    .replace("_", r"\_")
                                    .replace("{", r"\{")
                                    .replace("}", r"\}")
                                    .replace("%", r"\%")
                                    .replace("#", r"\#")
                                    .replace("&", r"\&")
                                    .replace("^", r"\^{}")
                                )

                            new_answer = []
                            for a, b in zip(normal_text, math_text):
                                new_answer.append(a)
                                new_answer.append(b)
                            new_answer.append(normal_text[-1])

                            new_answer = "$".join(new_answer)

                            ans[ans_choice.text] = new_answer

                            if ans_correct.attrs["alt"] == "Correct":
                                corrects.append(ans_choice.text)

                ques_details["answers"] = ans
                ques_details["correct_ans"] = corrects

        total_details.append(ques_details)

    # ? Print Progress
    print("Current Page: ", current_page)
    total_total_details += total_details
    current_page += 1

# ? Print total questions to recheck if scrapped successfully
print("Total Questions Found: ", len(total_total_details))

# ? rearranging the questions topic wise in final details
final_details = {}

for i in total_total_details:
    if i["topic"] not in final_details:
        final_details[i["topic"]] = [i]
    else:
        final_details[i["topic"]] += [i]


# ? Saving the dictionary as json to ./title/title.json
save_dir = f"./{title}"
if not os.path.exists(save_dir):
    os.mkdir(save_dir)

with open(save_dir + f"/{title}.json", "w") as f:
    json.dump(final_details, f, indent=4)

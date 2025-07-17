#!/bin/python

from drafter import Div, LineBreak, Text, TextBox, route, Page, Button, start_server, __version__, deploy_site, get_main_server
from dataclasses import dataclass

from random import choice

@dataclass
class Term:
        term: str
        definition: str
        you_said: str = ""

@dataclass
class State:
        terms: list[Term]

@route
def index(state: State) -> Page:
        return Page(state, [
                "What do you want to do?",
                Button("Add/Edit Terms (Resets Progress)", edit_terms),
                Button("Study Terms", study),
                Button("Last Run Results", generate_report)
        ])

@route
def edit_terms(state: State) -> Page:
        term_entry_boxes: list[Div] = []
        for i, term in enumerate(state.terms):
                term_entry_boxes.append(term_entry_box(term, i))
        if not term_entry_boxes:
                term_entry_boxes.append(term_entry_box(Term("", ""), 0))

        return Page(state, [
                "Enter terms below:",
                "To delete a term, simply make the term or definition blank.",
                *term_entry_boxes,
                Button("+", save_entered_terms, ("add_term_entry_box", len(term_entry_boxes))),
                Button("Main Menu", save_entered_terms, ("index", len(term_entry_boxes)))
        ])

def term_entry_box(term: Term, key: int) -> Div:
        return Div(
                "Term: ", TextBox("term" + str(key), term.term), "    "
                "Definition: ", TextBox("definition" + str(key), term.definition)
        )

@route
def add_term_entry_box(state: State) -> Page:
        state.terms.append(Term("", ""))
        return edit_terms(state)

@route
def save_entered_terms(state: State, procede_to: str, entry_len: int, **kwargs: str) -> Page:
        state.terms.clear()
        for i in range(entry_len):
                term = kwargs.pop("term" + str(i))
                definition = kwargs.pop("definition" + str(i))
                if not term or not definition: continue
                state.terms.append(Term(term, definition))

        if procede_to == "add_term_entry_box":
                return add_term_entry_box(state)
        elif procede_to == "index":
                return index(state)
        return index(state)

@route
def study(state: State) -> Page:
        unvisited_terms: list[Term] = []
        for term in state.terms:
                if not term.you_said: unvisited_terms.append(term)
        if not unvisited_terms:
                return generate_report(state)
        rand_term = choice(unvisited_terms)
        return Page(state, [
                "Term: " + rand_term.term,
                Text("Definition:"), TextBox("term_answer"), LineBreak(),
                Button("Submit", store_answer, ("study",), kwargs={"term_name": rand_term.term}),
                Button("See Results Now", store_answer, ("generate_report",), kwargs={"term_name": rand_term.term})
        ])

@route
def store_answer(state: State, procede_to: str, term_name: str = "", term_answer: str = "") -> Page:
        term = None
        for t in state.terms:
                if t.term == term_name:
                        term = t
                        break
        if term:
                term.you_said = term_answer

        if procede_to == "generate_report":
                return generate_report(state)
        return study(state)

@route
def generate_report(state: State) -> Page:
        visited_terms: list[Term] = []
        for term in state.terms:
                if term.you_said: visited_terms.append(term)
        if not visited_terms:
                return Page(state, [
                        "You haven't studied any terms!",
                        Button("Return home", index)
                ])

        term_result_boxes: list[Div] = []
        results = 0
        for term in visited_terms:
                result_box, result = term_result_box(term)
                term_result_boxes.append(result_box)
                results += result
        
        return Page(state, [
                "Result: " + str(results / len(visited_terms) * 100) + "%",
                *term_result_boxes,
                Button("Return home", index),
                Button("⟳ Reset Progress and Return home ⟳", reset)
        ])

def term_result_box(term: Term) -> tuple[Div, bool]:
        result = term.definition == term.you_said
        if result: color = "color: green"
        else:      color = "color: red"
        return Div(
                "Term: " + term.term, LineBreak(),
                "You said: ", Text(term.you_said, style=color), LineBreak(),
                "Correct: " + term.definition, LineBreak(), LineBreak()
        ), result

@route
def reset(state: State) -> Page:
        for term in state.terms:
                term.you_said = ""
        return index(state)

print(__version__)

deploy_site()

get_main_server().configuration.cdn_skulpt = "https://codebodger.github.io/drafter/cdn/skulpt/skulpt.js"
get_main_server().configuration.cdn_skulpt_std = "https://codebodger.github.io/drafter/cdn/skulpt/skulpt-stdlib.js"
get_main_server().configuration.cdn_skulpt_drafter = "https://codebodger.github.io/drafter/cdn/skulpt/skulpt-drafter.js"
get_main_server().configuration.cdn_drafter_setup = "https://codebodger.github.io/drafter/cdn/skulpt/drafter-setup.js"

v = __version__.split(".")

if int(v[0]) == 2 and int(v[1]) == 0:
        start_server(State(list[Term]()))

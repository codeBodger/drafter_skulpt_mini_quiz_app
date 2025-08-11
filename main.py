#!/bin/python

from drafter import __version__
from drafter.components import BulletedList, Button, Div, LineBreak, Text, TextBox
from drafter.deploy import deploy_site
from drafter.page import Page, Redirect
from drafter.routes import route
from drafter.server import get_main_server, start_server
# from drafter.testing import assert_state_equal

from bakery import assert_equal, assert_state_equal

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
        term_entry_boxes = [] # type: list[Div] # type: ignore
        for i, term in enumerate(state.terms):
                term_entry_boxes.append(term_entry_box(term, i))
        if not term_entry_boxes:
                term_entry_boxes.append(term_entry_box(Term("", ""), 0))

        return Page(state, [
                "Enter terms below:",
                "To delete a term, simply make the term or definition blank.",
                BulletedList(term_entry_boxes, style="list-style: none;"),
                Button("+", save_entered_terms, ["add_term_entry_box", len(term_entry_boxes)]),
                Button("Main Menu", save_entered_terms, ["index", len(term_entry_boxes)])
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
def save_entered_terms(state: State, procede_to: str, entry_len: int, **kwargs: str) -> Redirect:
        state.terms.clear()
        for i in range(entry_len):
                term = kwargs.pop("term" + str(i))
                definition = kwargs.pop("definition" + str(i))
                if term and definition:
                        state.terms.append(Term(term, definition))

        if procede_to == "add_term_entry_box":
                return add_term_entry_box(state)
        elif procede_to == "index":
                return index(state)
        return index(state)

@route
def study(state: State) -> Page:
        unvisited_terms = [] # type: list[Term] # type: ignore
        for term in state.terms:
                if not term.you_said: unvisited_terms.append(term)
        if not unvisited_terms:
                return generate_report(state)
        rand_term = choice(unvisited_terms)
        return Page(state, [
                "Term: " + rand_term.term,
                Text("Definition:"), TextBox("term_answer"), LineBreak(),
                Button("Submit", store_answer, ["study", rand_term.term]),
                Button("See Results Now", store_answer, ["generate_report", rand_term.term])
        ])

@route
def store_answer(state: State, procede_to: str, term_name: str, term_answer: str = "") -> Redirect:
        term = None
        for t in state.terms:
                if t.term == term_name:
                        term = t
        if term:
                term.you_said = term_answer

        if procede_to == "generate_report":
                return generate_report(state)
        return study(state)

@route
def generate_report(state: State) -> Page:
        visited_terms = [] # type: list[Term] # type: ignore
        for term in state.terms:
                if term.you_said: visited_terms.append(term)
        if not visited_terms:
                return Page(state, [
                        "You haven't studied any terms!",
                        Button("Return home", index)
                ])

        term_result_boxes = [] # type: list[Div] # type: ignore
        results = 0
        for term in visited_terms:
                result = term.definition == term.you_said
                result_box = term_result_box(term, result)
                term_result_boxes.append(result_box)
                if result:
                        results = results + 1
        
        return Page(state, [
                "Result: " + str(results / len(visited_terms) * 100) + "%",
                BulletedList(term_result_boxes, style="list-style: none;"),
                Button("Return home", index),
                Button("⟳ Reset Progress and Return home ⟳", reset)
        ])

def term_result_box(term: Term, result: bool) -> Div:
        if result: color = "color: green"
        else:      color = "color: red"
        return Div(
                "Term: " + term.term, LineBreak(),
                "You said: ", Text(term.you_said, style=color), LineBreak(),
                "Correct: " + term.definition, LineBreak(), LineBreak()
        )

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
# get_main_server().configuration.cdn_skulpt = "http://localhost:8080/skulpt.js"
# get_main_server().configuration.cdn_skulpt_std = "http://localhost:8080/skulpt-stdlib.js"
# get_main_server().configuration.cdn_skulpt_drafter = "http://localhost:8080/skulpt-drafter.js"
# get_main_server().configuration.cdn_drafter_setup = "http://localhost:8080/drafter-setup.js"


print("Tests for `index`")
assert_state_equal(index(State([])), State([]))
assert_state_equal(
        index(State([Term("hello", "world"), Term("hallo", "welt")])),
        State([Term("hello", "world"), Term("hallo", "welt")])
)
assert_state_equal(
        index(State([Term("hello", "world", "wrld"), Term("hallo", "welt", you_said="wetl")])),
        State([Term("hello", "world", "wrld"), Term("hallo", "welt", you_said="wetl")])
)
assert_equal(
        index(State([])),
        Page(State([]), [
                "What do you want to do?",
                Button("Add/Edit Terms (Resets Progress)", edit_terms),
                Button("Study Terms", study),
                Button("Last Run Results", generate_report)
        ])
)


v = __version__.split(".")

if int(v[0]) == 2 and int(v[1]) == 0:
        start_server(State(list[Term]()))

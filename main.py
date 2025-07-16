#!/bin/python

from typing import Any
from drafter import Div, LineBreak, Text, TextBox, route, Page, Button, start_server, __version__, deploy_site, get_main_server
from dataclasses import dataclass

from random import choice

@dataclass
class Term:
        term: str
        definition: str
        visited: bool = False
        you_said: str = ""

@dataclass
class State:
        terms: list[Term]

@route
def index(state: State) -> Page:
        return Page(state, [
                "What do you want to do?",
                Button("Add Terms", add_terms),
                Button("Study", study)
        ])

@route
def add_terms(state: State) -> Page:
        term_entry_boxes = [term_entry_box(term, i) for i, term in enumerate(state.terms)]
        return Page(state, [
                "Enter terms below:",
                *term_entry_boxes,
                Button("+", add_term_entry_pannel),
                Button("Save", save_entered_terms)
        ])

def term_entry_box(term: Term, key: int) -> Div:
        return Div(
                "Term: ", TextBox(f"term{key}", term.term), "&nbsp;&nbsp;&nbsp; "
                "Definition: ", TextBox(f"definition{key}", term.definition)
        )

@route
def add_term_entry_pannel(state: State) -> Page:
        state.terms.append(Term("", ""))
        return add_terms(state)

@route
def save_entered_terms(state: State, *args: Any, **kwargs: str) -> Page:
        print(args, kwargs)
        state.terms.clear()
        while len(kwargs):
                val = kwargs.popitem()
                key = val[0]
                if key.startswith("term"):
                        term = val[1]
                        def_key = key.replace("term", "definition")
                        definition = kwargs.pop(def_key)
                elif key.startswith("definition"):
                        definition = val[1]
                        term_key = key.replace("definition", "term")
                        term = kwargs.pop(term_key)
                else: continue

                state.terms.append(Term(term, definition))
        return index(state)

@route
def study(state: State) -> Page:
        unvisited_terms: list[Term] = []
        for term in state.terms:
                if not term.visited: unvisited_terms.append(term)
        if not unvisited_terms:
                return generate_report(state)
        rand_term = choice(unvisited_terms)
        rand_term.visited = True
        return Page(state, [
                f"Term: {rand_term.term}",
                Text("Definition:"), TextBox("answer"), LineBreak(),
                Button("Submit", check_answer, kwargs={"term": rand_term.term})
        ])

@route
def check_answer(state: State, **kwargs: str) -> Page:
        term_name = kwargs.get("term", "")
        term = None
        for t in state.terms:
                if t.term == term_name:
                        term = t
                        break
        if not term: return study(state)

        term_answer = kwargs.get("answer", "")
        term.you_said = term_answer

        return study(state)

@route
def generate_report(state: State) -> Page:
        visited_terms: list[Term] = []
        for term in state.terms:
                if term.visited: visited_terms.append(term)
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
                f"Result: {results / len(visited_terms) * 100 :.4}%",
                *term_result_boxes, LineBreak(),
                Button("Return home", index),
                Button("⟳ Reset and Return home ⟳", reset)
        ])

def term_result_box(term: Term) -> tuple[Div, bool]:
        if term.definition == term.you_said:
                return Div(
                        f"Term: {term.term}", LineBreak(),
                        "You said: ", Text(term.you_said, style="color: green"), LineBreak(),
                        f"Correct: {term.definition}", LineBreak()
                ), True
        else:
                return Div(
                        f"Term: {term.term}", LineBreak(),
                        "You said: ", Text(term.you_said, style="color: red"), LineBreak(),
                        f"Correct: {term.definition}", LineBreak()
                ), False

@route
def reset(state: State) -> Page:
        raise NotImplementedError()

print(__version__)

deploy_site()

get_main_server().configuration.cdn_skulpt = "https://codebodger.github.io/drafter/cdn/skulpt/skulpt.js"
get_main_server().configuration.cdn_skulpt_std = "https://codebodger.github.io/drafter/cdn/skulpt/skulpt-stdlib.js"
get_main_server().configuration.cdn_skulpt_drafter = "https://codebodger.github.io/drafter/cdn/skulpt/skulpt-drafter.js"
get_main_server().configuration.cdn_drafter_setup = "https://codebodger.github.io/drafter/cdn/skulpt/drafter-setup.js"

v = __version__.split(".")

if int(v[0]) == 2 and int(v[1]) == 0:
        start_server(State(list[Term]()))

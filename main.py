#!/bin/python

from drafter import route, Page, Button, start_server, __version__, deploy_site, get_main_server
from dataclasses import dataclass

from random import randint

@dataclass
class Term:
        term: str
        definition: str

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
        raise NotImplementedError()

@route
def study(state: State) -> Page:
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

#!/bin/python

from drafter import route, Page, Button, start_server, __version__, deploy_site, get_main_server, Table
from dataclasses import dataclass

from random import randint

@dataclass
class State:
        counter: int

@route
def index(state: State) -> Page:
        return Page(state, [Table([
                ["Welcome to Drafter!",
                "Click the button below."],
                [Button("Increase the count", increment_counter, (randint(1,100),))],
        ])])

@route
def increment_counter(state: State, offset: int) -> Page:
        raise ValueError("aa")
        state.counter += offset
        return Page(state, [
                "You've clicked the button " + str(state.counter) + " times",
                Button("Click again", increment_counter, (randint(1,100),))
        ])

print(__version__)

deploy_site()

get_main_server().configuration.cdn_skulpt = "https://codebodger.github.io/drafter/cdn/skulpt/skulpt.js"
get_main_server().configuration.cdn_skulpt_std = "https://codebodger.github.io/drafter/cdn/skulpt/skulpt-stdlib.js"
get_main_server().configuration.cdn_skulpt_drafter = "https://codebodger.github.io/drafter/cdn/skulpt/skulpt-drafter.js"
get_main_server().configuration.cdn_drafter_setup = "https://codebodger.github.io/drafter/cdn/skulpt/drafter-setup.js"

v = __version__.split(".")

if int(v[0]) == 2 and int(v[1]) == 0:
        start_server(State(0))

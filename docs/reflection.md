# Reflection: AI Tool Usage During the Feature Extension Sprint

Over this sprint I used an AI coding assistant to build and extend a FastAPI + Vanilla JS Kanban tracker — from the initial board through due dates, real-time search, and tags. Working this way reshaped where my effort actually went: less time typing code, far more time specifying and verifying it.

## A helpful moment

The moment that impressed me most was not code generation but **live browser verification**. After implementing the due-date feature, the assistant did not stop at "tests pass": it restarted the server, seeded demo tasks with past, near, and future due dates, took screenshots, and clicked through its own UI — confirming the red "Overdue" badge, the orange "Due soon" state, and that a completed task with a past date stayed calm green instead of screaming urgency. When it later clicked the "api" tag chip and checked that search for "bug" matched a card by tag alone, it was validating acceptance criteria, not just compiling. That closed a gap I expected to own entirely: the boring, essential "does it actually work in the browser" pass.

## A hindering moment

The friction was **prompt effort**. To get precise output I had to write prompts that were practically mini-specs — context, objective, numbered requirements, even a response structure. When I invested that effort, the result was close to final. But it exposed the trade: a vague ask would have produced plausible code that drifted from what I meant, so the precision work never disappeared — it moved upstream into my prompts. Writing "state flow must strictly be unidirectional" still left edge cases (can a task skip To Do → Done?) that the AI resolved by its own interpretation, which I then had to review and accept.

## How my review changed the output

I refused to accept screenshots as proof and **tested the live board myself**. Mid-sprint I created my own task — an overdue item in In Progress — to see whether the red styling and the Overdue filter behaved with data the AI had not seeded. That task even surfaced in the assistant's later counter check ("1 of 6 tasks"), forcing it to reconcile its assumptions against state it did not create. My manual pass turned the AI's "verified" into my "accepted," and it is why the final behavior contract reflects tested reality rather than generated intent.

## Takeaway

My core lesson: **prompt quality equals output quality**. The code tracked the spec almost linearly — sharp requirements in, sharp implementation out; ambiguity in, assumptions out. The structured prompts were the real engineering artifact of this sprint. AI removed the mechanical cost of building, but it did not remove the thinking; it demanded the thinking earlier, in writing, where it belongs.

# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner organize pet care tasks, generate a daily plan, and catch simple scheduling conflicts.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## Features

- Add and manage owner, pet, and task information in the Streamlit app.
- Sort tasks by time so the daily plan is shown in chronological order.
- Filter tasks by pet, completion status, and date.
- Mark tasks complete and automatically create the next occurrence for daily or weekly tasks.
- Show lightweight conflict warnings when multiple tasks are scheduled at the same time.
- Generate a readable daily schedule summary using the scheduler logic.

## 📸 Demo

<a href="/course_images/ai110/Demo.png" target="_blank"><img src='/course_images/ai110/Demo.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Smarter Scheduling

PawPal+ now includes a few simple scheduling features to make the planner more useful:

- Tasks can be sorted by time so the daily plan is shown in a clear order.
- Tasks can be filtered by pet, completion status, and due date.
- Daily and weekly recurring tasks automatically create the next occurrence when completed.
- The scheduler returns lightweight conflict warnings when multiple tasks are scheduled for the same time.

## Testing PawPal+

Run the automated tests with:

```bash
python -m pytest
```

The test suite covers core scheduler behavior like task completion, adding tasks to pets, sorting tasks in time order, filtering by pet, creating the next daily occurrence for recurring tasks, detecting same-time conflicts, and a few simple edge cases such as empty schedules and non-recurring task completion.

Confidence Level: 4/5 stars. The main scheduling behaviors are covered and passing, but there is still room for more advanced tests around overlapping durations, invalid time inputs, and larger multi-pet schedules.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

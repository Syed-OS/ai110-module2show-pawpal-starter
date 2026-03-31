from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task


def get_owner() -> Owner:
    """Return the saved owner object from session state."""
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(
            name="Jordan",
            available_time=120,
            preferences="Start with the earliest tasks first.",
        )
    return st.session_state.owner


def find_pet(owner: Owner, pet_name: str) -> Pet | None:
    """Find a pet on the owner by name."""
    for pet in owner.pets:
        if pet.name == pet_name:
            return pet
    return None


def format_task_rows(owner: Owner) -> list[dict[str, str]]:
    """Build readable rows for the current task table."""
    rows: list[dict[str, str]] = []
    for pet in owner.pets:
        for task in pet.tasks:
            rows.append(
                {
                    "Pet": pet.name,
                    "Type": pet.pet_type,
                    "Task": task.description,
                    "Time": task.time,
                    "Frequency": task.frequency,
                    "Status": "Done" if task.completed else "To do",
                }
            )
    return rows


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

owner = get_owner()

st.title("🐾 PawPal+")
st.markdown("Plan pet care tasks and build a simple schedule for today.")

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** helps a busy pet owner stay on top of pet care.
You can save pet info, add tasks, and generate a schedule for the day.
"""
    )

st.divider()

st.subheader("Owner Profile")
with st.form("owner_form"):
    owner_name = st.text_input("Owner name", value=owner.name)
    available_time = st.number_input(
        "Available time today (minutes)",
        min_value=15,
        max_value=720,
        value=owner.available_time,
        step=15,
    )
    preferences = st.text_input("Preferences", value=owner.preferences)
    save_owner = st.form_submit_button("Save owner info")

if save_owner:
    owner.name = owner_name
    owner.available_time = int(available_time)
    owner.update_preferences(preferences)
    st.success("Owner info saved.")

st.divider()

st.subheader("Add a Pet")
with st.form("pet_form"):
    pet_name = st.text_input("Pet name")
    pet_type = st.selectbox("Species", ["Dog", "Cat", "Other"])
    pet_age = st.number_input("Pet age", min_value=0, max_value=40, value=1)
    pet_notes = st.text_input("Notes")
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    cleaned_name = pet_name.strip()
    if not cleaned_name:
        st.error("Enter a pet name before adding a pet.")
    elif find_pet(owner, cleaned_name) is not None:
        st.warning("That pet is already in PawPal+.")
    else:
        owner.add_pet(
            Pet(
                name=cleaned_name,
                pet_type=pet_type,
                age=int(pet_age),
                notes=pet_notes.strip(),
            )
        )
        st.success(f"{cleaned_name} was added.")

if owner.pets:
    st.write("Current pets:")
    st.table(
        [
            {
                "Name": pet.name,
                "Type": pet.pet_type,
                "Age": pet.age,
                "Notes": pet.notes or "-",
            }
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets added yet.")

st.divider()

st.subheader("Add a Task")
if owner.pets:
    with st.form("task_form"):
        selected_pet_name = st.selectbox(
            "Choose a pet",
            options=[pet.name for pet in owner.pets],
        )
        task_description = st.text_input("Task description", value="Morning walk")
        task_time = st.time_input("Task time", value=time(7, 30))
        task_frequency = st.selectbox(
            "Frequency",
            ["Daily", "Weekdays", "Weekends", "As needed"],
        )
        add_task = st.form_submit_button("Add task")

    if add_task:
        pet = find_pet(owner, selected_pet_name)
        if pet is None:
            st.error("Choose a valid pet before adding a task.")
        elif not task_description.strip():
            st.error("Enter a task description before adding a task.")
        else:
            pet.add_task(
                Task(
                    description=task_description.strip(),
                    time=task_time.strftime("%I:%M %p"),
                    frequency=task_frequency,
                )
            )
            st.success(f"Task added for {pet.name}.")
else:
    st.info("Add a pet first so you can assign tasks.")

task_rows = format_task_rows(owner)
if task_rows:
    st.write("Current tasks:")
    st.table(task_rows)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Today's Schedule")
st.caption("This schedule is generated from the pets and tasks currently saved in the app.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    schedule = scheduler.generate_plan()

    if not schedule:
        st.warning("There are no tasks to schedule yet.")
    else:
        st.table(
            [
                {
                    "Time": task.time,
                    "Pet": pet_name,
                    "Task": task.description,
                    "Frequency": task.frequency,
                    "Status": "Done" if task.completed else "To do",
                }
                for pet_name, task in schedule
            ]
        )
        st.markdown(scheduler.explain_plan())

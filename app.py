from datetime import date, time

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


def get_scheduler(owner: Owner) -> Scheduler:
    """Create a scheduler for the current owner."""
    return Scheduler(owner)


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
                    "Due date": str(task.due_date),
                    "Time": task.time,
                    "Frequency": task.frequency,
                    "Status": "Done" if task.completed else "To do",
                }
            )
    return rows


def format_schedule_rows(schedule: list[tuple[str, Task]]) -> list[dict[str, str]]:
    """Turn scheduled tasks into table rows for Streamlit."""
    return [
        {
            "Due date": str(task.due_date),
            "Time": task.time,
            "Pet": pet_name,
            "Task": task.description,
            "Frequency": task.frequency,
            "Status": "Done" if task.completed else "To do",
        }
        for pet_name, task in schedule
    ]


def get_completion_options(schedule: list[tuple[str, Task]]) -> list[str]:
    """Create readable labels for pending tasks that can be completed."""
    return [
        f"{pet_name} | {task.description} | {task.time} | {task.due_date}"
        for pet_name, task in schedule
    ]


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

owner = get_owner()
scheduler = get_scheduler(owner)

st.title("🐾 PawPal+")
st.markdown("Plan pet care tasks, sort them clearly, and spot schedule conflicts early.")

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** helps a busy pet owner stay on top of pet care.
You can save pet info, add tasks, generate a schedule, filter tasks, and check for conflicts.
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
        task_date = st.date_input("Due date", value=date.today())
        task_time = st.time_input("Task time", value=time(7, 30))
        task_frequency = st.selectbox(
            "Frequency",
            ["Daily", "Weekly", "As needed"],
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
                    due_date=task_date,
                )
            )
            st.success(f"Task added for {pet.name}.")
else:
    st.info("Add a pet first so you can assign tasks.")

task_rows = format_task_rows(owner)
if task_rows:
    st.write("All saved tasks:")
    st.table(task_rows)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Schedule View")
selected_date = st.date_input("View schedule for", value=date.today(), key="schedule_date")
pet_filter_options = ["All pets"] + [pet.name for pet in owner.pets]
selected_pet_filter = st.selectbox("Filter by pet", pet_filter_options)
selected_status_filter = st.selectbox("Filter by status", ["Pending", "Completed", "All"])

completed_filter_map = {
    "Pending": False,
    "Completed": True,
    "All": None,
}

filtered_schedule = scheduler.filter_tasks(
    pet_name=None if selected_pet_filter == "All pets" else selected_pet_filter,
    completed=completed_filter_map[selected_status_filter],
    on_date=selected_date,
)

if filtered_schedule:
    st.table(format_schedule_rows(filtered_schedule))
else:
    st.info("No tasks match the current filters.")

conflicts = scheduler.detect_conflicts(on_date=selected_date)
if conflicts:
    for conflict in conflicts:
        st.warning(
            f"Scheduling warning: {conflict} Consider moving one task so the day is easier to manage."
        )
else:
    st.success("No same-time conflicts were found for this day.")

st.caption("The schedule view uses the scheduler's sorting, filtering, and conflict detection methods.")

st.divider()

st.subheader("Complete a Task")
pending_schedule = scheduler.generate_plan(on_date=selected_date)
completion_options = get_completion_options(pending_schedule)

if completion_options:
    selected_completion_label = st.selectbox(
        "Choose a pending task to mark complete",
        completion_options,
    )
    if st.button("Mark selected task complete"):
        pet_name, task_description, task_time_text, due_date_text = selected_completion_label.split(
            " | "
        )
        completed_task = scheduler.mark_task_complete(
            pet_name=pet_name,
            task_description=task_description,
            on_date=date.fromisoformat(due_date_text),
            task_time=task_time_text,
        )
        if completed_task is None:
            st.error("That task could not be updated. Try refreshing the schedule view.")
        elif completed_task.frequency.lower() in {"daily", "weekly"}:
            st.success(
                f"Marked '{completed_task.description}' complete and created its next {completed_task.frequency.lower()} occurrence."
            )
        else:
            st.success(f"Marked '{completed_task.description}' complete.")
else:
    st.info("There are no pending tasks to complete for this date.")

st.divider()

st.subheader("Plan Summary")
schedule = scheduler.generate_plan(on_date=selected_date)

if not schedule:
    st.warning("There are no tasks to schedule for this day.")
else:
    st.table(format_schedule_rows(schedule))
    st.markdown(scheduler.explain_plan(on_date=selected_date))

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(title: str, schedule: list[tuple[str, Task]]) -> None:
    print(title)
    print("-" * 60)

    if not schedule:
        print("No tasks found.")
        print()
        return

    for index, (pet_name, task) in enumerate(schedule, start=1):
        status = "Done" if task.completed else "To do"
        print(
            f"{index}. {task.due_date} | {task.time} | {pet_name} | "
            f"{task.description} ({task.frequency}) [{status}]"
        )
    print()


def main() -> None:
    today = date.today()

    owner = Owner(
        name="Jordan",
        available_time=120,
        preferences="Start with the earliest pet care tasks first.",
    )

    dog = Pet(name="Mochi", pet_type="Dog", age=4, notes="Needs a long morning walk.")
    cat = Pet(name="Luna", pet_type="Cat", age=2, notes="Gets medicine with breakfast.")

    dog.add_task(Task(description="Dinner feeding", time="06:00 PM", frequency="Daily"))
    dog.add_task(Task(description="Morning walk", time="07:30 AM", frequency="Daily"))
    cat.add_task(Task(description="Medication", time="08:00 AM", frequency="Daily"))
    cat.add_task(Task(description="Play session", time="07:30 AM", frequency="Weekly"))

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)

    print_schedule("Today's Schedule", scheduler.generate_plan(on_date=today))
    print_schedule("Tasks for Mochi", scheduler.filter_tasks(pet_name="Mochi", on_date=today))

    print("Conflict Check Before Completing Tasks")
    print("-" * 60)
    initial_conflicts = scheduler.detect_conflicts(on_date=today)
    if initial_conflicts:
        for conflict in initial_conflicts:
            print(conflict)
    else:
        print("No conflicts found.")
    print()

    completed_task = scheduler.mark_task_complete(
        pet_name="Mochi",
        task_description="Morning walk",
        on_date=today,
        task_time="07:30 AM",
    )
    if completed_task is not None:
        print("Marked 'Morning walk' complete and created the next recurring task.\n")

    print_schedule("Completed Tasks", scheduler.filter_tasks(completed=True, on_date=today))
    print_schedule("Updated Schedule", scheduler.generate_plan(on_date=today))
    print_schedule(
        "Tomorrow's Tasks",
        scheduler.filter_tasks(on_date=today + timedelta(days=1)),
    )

    print("Conflict Check After Completing Morning Walk")
    print("-" * 60)
    conflicts = scheduler.detect_conflicts(on_date=today)
    if conflicts:
        for conflict in conflicts:
            print(conflict)
    else:
        print("No conflicts found.")
    print()

    print(scheduler.explain_plan(on_date=today))


if __name__ == "__main__":
    main()

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(schedule: list[tuple[str, Task]]) -> None:
    print("Today's Schedule")
    print("-" * 40)

    if not schedule:
        print("No tasks scheduled for today.")
        return

    for index, (pet_name, task) in enumerate(schedule, start=1):
        status = "Done" if task.completed else "To do"
        print(
            f"{index}. {task.time} | {pet_name} | {task.description} "
            f"({task.frequency}) [{status}]"
        )


def main() -> None:
    owner = Owner(
        name="Jordan",
        available_time=120,
        preferences="Start with the earliest pet care tasks first.",
    )

    dog = Pet(name="Mochi", pet_type="Dog", age=4, notes="Needs a long morning walk.")
    cat = Pet(name="Luna", pet_type="Cat", age=2, notes="Gets medicine with breakfast.")

    dog.add_task(Task(description="Morning walk", time="07:30 AM", frequency="Daily"))
    dog.add_task(Task(description="Dinner feeding", time="06:00 PM", frequency="Daily"))
    cat.add_task(Task(description="Medication", time="08:00 AM", frequency="Daily"))

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    schedule = scheduler.generate_plan()

    print_schedule(schedule)
    print()
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()

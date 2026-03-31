from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_updates_task_status() -> None:
    task = Task(description="Morning walk", time="07:30 AM", frequency="Daily")

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", pet_type="Dog", age=4)
    task = Task(description="Dinner feeding", time="06:00 PM", frequency="Daily")

    pet.add_task(task)

    assert len(pet.tasks) == 1


def test_generate_plan_sorts_tasks_by_time() -> None:
    owner = Owner(name="Jordan", available_time=120)
    pet = Pet(name="Mochi", pet_type="Dog", age=4)
    pet.add_task(Task(description="Dinner feeding", time="06:00 PM", frequency="Daily"))
    pet.add_task(Task(description="Morning walk", time="07:30 AM", frequency="Daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan(on_date=date.today())

    assert [task.description for _, task in plan] == ["Morning walk", "Dinner feeding"]


def test_filter_tasks_by_pet_name_returns_only_that_pets_tasks() -> None:
    owner = Owner(name="Jordan", available_time=120)
    dog = Pet(name="Mochi", pet_type="Dog", age=4)
    cat = Pet(name="Luna", pet_type="Cat", age=2)
    dog.add_task(Task(description="Morning walk", time="07:30 AM", frequency="Daily"))
    cat.add_task(Task(description="Medication", time="08:00 AM", frequency="Daily"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    tasks = scheduler.filter_tasks(pet_name="Luna", on_date=date.today())

    assert len(tasks) == 1
    assert tasks[0][0] == "Luna"
    assert tasks[0][1].description == "Medication"


def test_mark_task_complete_creates_next_daily_occurrence() -> None:
    today = date.today()
    owner = Owner(name="Jordan", available_time=120)
    pet = Pet(name="Mochi", pet_type="Dog", age=4)
    pet.add_task(
        Task(
            description="Morning walk",
            time="07:30 AM",
            frequency="Daily",
            due_date=today,
        )
    )
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    completed_task = scheduler.mark_task_complete("Mochi", "Morning walk", on_date=today)

    assert completed_task is not None
    assert completed_task.completed is True
    assert len(pet.tasks) == 2
    assert pet.tasks[1].due_date == today + timedelta(days=1)


def test_detect_conflicts_finds_same_time_tasks() -> None:
    owner = Owner(name="Jordan", available_time=120)
    dog = Pet(name="Mochi", pet_type="Dog", age=4)
    cat = Pet(name="Luna", pet_type="Cat", age=2)
    dog.add_task(Task(description="Morning walk", time="07:30 AM", frequency="Daily"))
    cat.add_task(Task(description="Medication", time="07:30 AM", frequency="Daily"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts(on_date=date.today())

    assert len(conflicts) == 1
    assert "07:30 AM" in conflicts[0]


def test_generate_plan_returns_empty_list_when_no_tasks_exist() -> None:
    owner = Owner(name="Jordan", available_time=120)
    owner.add_pet(Pet(name="Mochi", pet_type="Dog", age=4))

    scheduler = Scheduler(owner)

    assert scheduler.generate_plan(on_date=date.today()) == []


def test_mark_task_complete_does_not_duplicate_non_recurring_task() -> None:
    today = date.today()
    owner = Owner(name="Jordan", available_time=120)
    pet = Pet(name="Mochi", pet_type="Dog", age=4)
    pet.add_task(
        Task(
            description="Vet visit",
            time="02:00 PM",
            frequency="As needed",
            due_date=today,
        )
    )
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    completed_task = scheduler.mark_task_complete("Mochi", "Vet visit", on_date=today)

    assert completed_task is not None
    assert completed_task.completed is True
    assert len(pet.tasks) == 1

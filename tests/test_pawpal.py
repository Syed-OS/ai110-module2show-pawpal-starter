from pawpal_system import Pet, Task


def test_mark_complete_updates_task_status() -> None:
    task = Task(description="Morning walk", time="07:30 AM", frequency="Daily")

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", pet_type="Dog", age=4)
    task = Task(description="Dinner feeding", time="06:00 PM", frequency="Daily")

    pet.add_task(task)

    assert len(pet.tasks) == 1

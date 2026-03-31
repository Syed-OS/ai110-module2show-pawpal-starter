from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta


@dataclass
class Task:
    description: str
    time: str
    frequency: str
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark the task as not completed."""
        self.completed = False

    def update_task(
        self,
        description: str | None = None,
        time: str | None = None,
        frequency: str | None = None,
        due_date: date | None = None,
    ) -> None:
        """Update any provided task fields."""
        if description is not None:
            self.description = description
        if time is not None:
            self.time = time
        if frequency is not None:
            self.frequency = frequency
        if due_date is not None:
            self.due_date = due_date

    def sort_key(self) -> datetime:
        """Convert the task time into a sortable datetime value."""
        time_formats = ("%I:%M %p", "%H:%M")
        for time_format in time_formats:
            try:
                return datetime.strptime(self.time, time_format)
            except ValueError:
                continue
        raise ValueError(
            f"Unsupported time format for task '{self.description}': {self.time}"
        )

    def next_occurrence(self) -> Task | None:
        """Create the next instance of a recurring task."""
        frequency = self.frequency.strip().lower()
        if frequency == "daily":
            next_due_date = self.due_date + timedelta(days=1)
        elif frequency == "weekly":
            next_due_date = self.due_date + timedelta(days=7)
        else:
            return None

        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            due_date=next_due_date,
        )


@dataclass
class Pet:
    name: str
    pet_type: str
    age: int
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)


@dataclass
class Owner:
    name: str
    available_time: int
    preferences: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def update_preferences(self, preferences: str) -> None:
        """Replace the owner's scheduling preferences."""
        self.preferences = preferences

    def get_all_tasks(self) -> list[tuple[str, Task]]:
        """Collect tasks from every pet owned by this owner."""
        all_tasks: list[tuple[str, Task]] = []
        for pet in self.pets:
            for task in pet.get_tasks():
                all_tasks.append((pet.name, task))
        return all_tasks


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for a specific owner."""
        self.owner = owner

    def retrieve_tasks(
        self,
        include_completed: bool = False,
        on_date: date | None = None,
    ) -> list[tuple[str, Task]]:
        """Get tasks from the owner's pets with optional date and status filters."""
        tasks = self.owner.get_all_tasks()
        if not include_completed:
            tasks = [(pet_name, task) for pet_name, task in tasks if not task.completed]
        if on_date is not None:
            tasks = [(pet_name, task) for pet_name, task in tasks if task.due_date == on_date]
        return tasks

    def sort_by_time(
        self,
        tasks: list[tuple[str, Task]] | None = None,
    ) -> list[tuple[str, Task]]:
        """Sort a list of tasks by their time."""
        tasks_to_sort = tasks if tasks is not None else self.retrieve_tasks()
        return sorted(tasks_to_sort, key=lambda item: item[1].sort_key())

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        on_date: date | None = None,
    ) -> list[tuple[str, Task]]:
        """Filter tasks by pet name, completion state, and optional due date."""
        tasks = self.owner.get_all_tasks()

        if pet_name is not None:
            tasks = [
                (current_pet_name, task)
                for current_pet_name, task in tasks
                if current_pet_name.lower() == pet_name.lower()
            ]
        if completed is not None:
            tasks = [(current_pet_name, task) for current_pet_name, task in tasks if task.completed is completed]
        if on_date is not None:
            tasks = [(current_pet_name, task) for current_pet_name, task in tasks if task.due_date == on_date]

        return self.sort_by_time(tasks)

    def mark_task_complete(
        self,
        pet_name: str,
        task_description: str,
        on_date: date | None = None,
        task_time: str | None = None,
    ) -> Task | None:
        """Mark a task complete and create the next recurring task when needed."""
        target_date = on_date or date.today()

        for pet in self.owner.pets:
            if pet.name.lower() != pet_name.lower():
                continue

            for task in pet.tasks:
                if task.completed:
                    continue
                if task.description != task_description:
                    continue
                if task.due_date != target_date:
                    continue
                if task_time is not None and task.time != task_time:
                    continue

                task.mark_complete()
                next_task = task.next_occurrence()
                if next_task is not None:
                    pet.add_task(next_task)
                return task

        return None

    def detect_conflicts(
        self,
        on_date: date | None = None,
    ) -> list[str]:
        """Find simple same-time conflicts in the schedule."""
        target_date = on_date or date.today()
        schedule = self.generate_plan(on_date=target_date)

        tasks_by_time: dict[str, list[tuple[str, Task]]] = {}
        for pet_name, task in schedule:
            tasks_by_time.setdefault(task.time, []).append((pet_name, task))

        conflicts: list[str] = []
        for task_time, tasks_at_time in tasks_by_time.items():
            if len(tasks_at_time) < 2:
                continue

            task_summaries = [
                f"{pet_name} has '{task.description}'"
                for pet_name, task in tasks_at_time
            ]
            conflicts.append(
                f"Conflict at {task_time}: " + " and ".join(task_summaries) + "."
            )
        return conflicts

    def generate_plan(self, on_date: date | None = None) -> list[tuple[str, Task]]:
        """Build a daily plan by sorting pending tasks by time."""
        target_date = on_date or date.today()
        return self.sort_by_time(self.retrieve_tasks(on_date=target_date))

    def explain_plan(self, on_date: date | None = None) -> str:
        """Return a short explanation of the generated plan."""
        plan = self.generate_plan(on_date=on_date)
        if not plan:
            return "There are no pending tasks for today."

        lines = ["Today's plan is ordered by time so the owner can follow it more easily:"]
        for pet_name, task in plan:
            lines.append(
                f"- {task.time}: {task.description} for {pet_name} ({task.frequency})"
            )

        conflicts = self.detect_conflicts(on_date=on_date)
        if conflicts:
            lines.append("")
            lines.append("Possible conflicts:")
            lines.extend(f"- {conflict}" for conflict in conflicts)

        return "\n".join(lines)

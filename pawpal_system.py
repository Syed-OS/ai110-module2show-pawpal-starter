from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    description: str
    time: str
    frequency: str
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
    ) -> None:
        """Update any provided task fields."""
        if description is not None:
            self.description = description
        if time is not None:
            self.time = time
        if frequency is not None:
            self.frequency = frequency

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

    def retrieve_tasks(self, include_completed: bool = False) -> list[tuple[str, Task]]:
        """Get tasks from the owner's pets, optionally including completed ones."""
        tasks = self.owner.get_all_tasks()
        if include_completed:
            return tasks
        return [(pet_name, task) for pet_name, task in tasks if not task.completed]

    def generate_plan(self) -> list[tuple[str, Task]]:
        """Build a daily plan by sorting pending tasks by time."""
        return sorted(self.retrieve_tasks(), key=lambda item: item[1].sort_key())

    def explain_plan(self) -> str:
        """Return a short explanation of the generated plan."""
        plan = self.generate_plan()
        if not plan:
            return "There are no pending tasks for today."

        lines = ["Today's plan is ordered by time so the owner can follow it more easily:"]
        for pet_name, task in plan:
            lines.append(
                f"- {task.time}: {task.description} for {pet_name} ({task.frequency})"
            )
        return "\n".join(lines)

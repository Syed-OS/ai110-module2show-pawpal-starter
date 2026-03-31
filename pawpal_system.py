from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    duration: int
    priority: int
    category: str
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def update_task(
        self,
        title: str | None = None,
        duration: int | None = None,
        priority: int | None = None,
        category: str | None = None,
    ) -> None:
        pass


@dataclass
class Pet:
    name: str
    pet_type: str
    age: int
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass


@dataclass
class Owner:
    name: str
    available_time: int
    preferences: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def update_preferences(self, preferences: str) -> None:
        pass


class Scheduler:
    def __init__(self, tasks: list[Task], available_time: int) -> None:
        self.tasks = tasks
        self.available_time = available_time

    def generate_plan(self) -> list[Task]:
        pass

    def explain_plan(self) -> str:
        pass

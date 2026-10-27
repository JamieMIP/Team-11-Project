"""Run the task management feature on its own with sample data."""

from project_task.gui import TaskManagementApp
from project_task.sample_data import build_sample_data


def main() -> None:
    data = build_sample_data()
    app = TaskManagementApp(data["people"])
    app.mainloop()


if __name__ == "__main__":
    main()

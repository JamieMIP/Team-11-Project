from datetime import date, timedelta

from project_task import (
    Employee,
    Manager,
    Priority,
    Project,
    TaskError,
    TeamLeader,
)


def section(title: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


def attempt(description: str, action, *args) -> None:
    """Try an action that should be refused, and print why."""
    print(description)
    try:
        action(*args)
        print("   Allowed")
    except TaskError as error:
        print(f"   DENIED: {error}")


def show_task(task) -> None:
    who = task.assignee.name if task.assignee else "Unassigned"
    risk = "high-risk" if task.isHighRisk else "routine"
    print(f"   [{task.taskId}] {task.title} | {risk}, {task.priority.name} | "
          f"due {task.deadline} | {task.statusText()} | {who}")


def show_progress(project: Project) -> None:
    print(f"Project '{project.name}': {project.completedCount()}/{len(project.tasks)} "
          f"tasks complete ({project.showProgress():.0f}%)")


def main() -> None:
    Project.clearAll()
    today = date.today()

    section("1. Manager creates teams and appoints team leaders")
    maria = Manager("M01", "Maria", "maria@company.com")
    tom = TeamLeader("L01", "Tom", "tom@company.com")
    lisa = TeamLeader("L02", "Lisa", "lisa@company.com")
    alice = Employee("E01", "Alice", "alice@company.com")
    bob = Employee("E02", "Bob", "bob@company.com")
    chris = Employee("E03", "Chris", "chris@company.com")
    dana = Employee("E04", "Dana", "dana@company.com")

    frontend = maria.createTeam("Frontend")
    backend = maria.createTeam("Backend")
    qa = maria.createTeam("QA")
    maria.appointTeamLeader(frontend, tom)
    maria.appointTeamLeader(backend, tom)
    maria.appointTeamLeader(qa, lisa)
    print(
        f"Tom leads: {[t.name for t in tom.teamsLed]}  (one person, several teams)")
    maria.appointTeamLeader(backend, lisa)
    print(f"Backend leader changed to Lisa. Tom leads: {[t.name for t in tom.teamsLed]}, "
          f"Lisa leads: {[t.name for t in lisa.teamsLed]}  (one leader per team)")
    frontend.addMember(alice)
    frontend.addMember(bob)
    backend.addMember(chris)
    qa.addMember(dana)
    print("Members added: Alice and Bob -> Frontend, Chris -> Backend, Dana -> QA")
    print(f"Does a team leader have createTeam()? {hasattr(tom, 'createTeam')}  "
          "(only managers create teams)")

    section("2. Team leader creates tasks with priority and deadline")
    website = Project("Website Redesign")
    homepage = tom.createTask(
        website, "Design homepage", today + timedelta(days=5))
    payment = tom.createTask(website, "Build payment page", today + timedelta(days=7),
                             Priority.HIGH, isHighRisk=True)
    copy = tom.createTask(website, "Write page copy",
                          today - timedelta(days=3), Priority.LOW)
    footer = tom.createTask(website, "Update footer",
                            today + timedelta(days=20), Priority.LOW)
    navbar = tom.createTask(website, "Fix navbar", today - timedelta(days=2))
    tom.editTask(navbar, title="Fix mobile navbar")
    for task in website.tasks:
        show_task(task)
    show_progress(website)

    section("3. Only managers and team leaders can assign tasks")
    print(
        f"Does an employee have assignTask()? {hasattr(alice, 'assignTask')}")
    attempt("Tom tries to assign a task to Dana, who is in Lisa's team:",
            tom.assignTask, navbar, dana)

    section("4. Assigning tasks, with an overload warning")
    for task in (homepage, payment, copy, footer):
        overloaded = tom.assignTask(task, alice)
        warning = "  <- WARNING: potential overload (still assigned)" if overloaded else ""
        print(f"Tom assigned {task.taskId} to Alice{warning}")
    tom.assignTask(navbar, bob)
    print(f"Tom assigned {navbar.taskId} to Bob")

    section("5. Employees update their own tasks")
    alice.markProgressing(homepage)
    needs_approval = alice.markDone(homepage)
    print(f"Alice finished {homepage.taskId}. Needs approval? {needs_approval} -> "
          f"{homepage.statusText()}")
    attempt("Bob tries to mark Alice's task as done:", bob.markDone, copy)

    section("6. High-risk task: review, reopen, then approve")
    alice.markDone(payment)
    print(f"Alice finished {payment.taskId} -> {payment.statusText()}")
    print("Tom reviews it:\n   " + tom.reviewTask(payment).replace("\n", "\n   "))
    tom.reopenTask(payment)
    print(f"Tom finds a problem and reopens it -> {payment.statusText()}")
    alice.markDone(payment)
    tom.approveTask(payment)
    print(f"Alice fixes it, Tom approves -> {payment.statusText()}")
    show_progress(website)

    section("7. Priority changes within area of responsibility")
    tom.changePriority(copy, Priority.HIGH)
    print(f"Tom changed {copy.taskId} priority to {copy.priority.name}")
    attempt("Lisa tries to change a task in Tom's team:",
            lisa.changePriority, copy, Priority.LOW)

    section("8. Manager assigns tasks (kept separate on dashboards)")
    migrate = maria.createTask(website, "Migrate database", today + timedelta(days=30),
                               Priority.HIGH, isHighRisk=True)
    maria.assignTask(migrate, chris)
    audit = maria.createTask(
        website, "Accessibility audit", today + timedelta(days=25))
    maria.assignTask(audit, alice)
    groups = alice.dashboard.show()
    print("Alice's dashboard:")
    print("  Assigned by a manager:")
    for task in groups["manager"]:
        show_task(task)
    print("  Assigned by a team leader:")
    for task in groups["teamLeader"]:
        show_task(task)

    section("9. Overdue tasks stay open and are highlighted")
    for person in (alice, bob, tom, maria):
        overdue = person.dashboard.highlightOverdueTask()
        print(f"{person.name}'s dashboard ({person.role}): {len(overdue)} overdue")
        for task in overdue:
            show_task(task)
    alice.markProgressing(copy)
    print(
        f"Alice keeps working on {copy.taskId}, but it stays: {copy.statusText()}")

    section("10. Unfinished and overdue tasks, handled case by case")
    tom.changeDeadline(copy, today + timedelta(days=4))
    print(f"Tom extends the deadline of {copy.taskId} -> {copy.statusText()}")
    unfinished = frontend.removeMember(bob)
    print(f"Bob leaves Frontend. Unfinished tasks returned to Tom (not auto-reassigned): "
          f"{[t.taskId for t in unfinished]}")
    for task in unfinished:
        tom.reassignTask(task, alice)
        tom.changeDeadline(task, today + timedelta(days=3))
        print(
            f"Tom reassigns {task.taskId} to Alice with a new deadline -> {task.statusText()}")
    maria.reassignTask(migrate, dana)
    print(
        f"Maria reassigns {migrate.taskId} from Chris to Dana (across teams)")

    section("11. Finishing the work")
    for task in (copy, footer, navbar, audit):
        alice.markDone(task)
    dana.markDone(migrate)
    print(f"All tasks marked done. {migrate.taskId} is {migrate.statusText()}")
    show_progress(website)
    maria.approveTask(migrate)
    print(f"Maria approves {migrate.taskId}")
    show_progress(website)


if __name__ == "__main__":
    main()

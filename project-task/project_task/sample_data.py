from __future__ import annotations

from datetime import date, timedelta

from .models import Employee, Manager, Priority, Project, TeamLeader


def build_sample_data() -> dict:
    """Create sample people, teams, projects and tasks.
    Some deadlines are in the past so overdue highlighting can be seen straight away."""
    Project.clearAll()
    today = date.today()

    maria = Manager("M01", "Maria", "maria@company.com")
    tom = TeamLeader("L01", "Tom", "tom@company.com")
    lisa = TeamLeader("L02", "Lisa", "lisa@company.com")
    alice = Employee("E01", "Alice", "alice@company.com")
    bob = Employee("E02", "Bob", "bob@company.com")
    chris = Employee("E03", "Chris", "chris@company.com")
    dana = Employee("E04", "Dana", "dana@company.com")
    evan = Employee("E05", "Evan", "evan@company.com")

    # Teams: Lisa leads two teams to show one person can lead several.
    frontend = maria.createTeam("Frontend")
    backend = maria.createTeam("Backend")
    qa = maria.createTeam("QA")
    maria.appointTeamLeader(frontend, tom)
    maria.appointTeamLeader(backend, lisa)
    maria.appointTeamLeader(qa, lisa)
    frontend.addMember(alice)
    frontend.addMember(bob)
    backend.addMember(chris)
    qa.addMember(dana)

    website = Project("Website Redesign")
    mobile = Project("Mobile App")

    # Website tasks from Tom (team leader)
    homepage = tom.createTask(
        website, "Design homepage", today + timedelta(days=5))
    tom.assignTask(homepage, alice)
    alice.markProgressing(homepage)
    # routine: complete
    alice.markDone(homepage)

    payment = tom.createTask(website, "Build payment page", today + timedelta(days=7),
                             Priority.HIGH, isHighRisk=True)
    tom.assignTask(payment, alice)
    alice.markProgressing(payment)
    # awaiting approval
    alice.markDone(payment)

    copy = tom.createTask(website, "Write page copy",
                          today - timedelta(days=3), Priority.LOW)
    tom.assignTask(copy, alice)
    alice.markProgressing(copy)                                # overdue

    navbar = tom.createTask(website, "Fix mobile navbar",
                            today - timedelta(days=1))
    tom.assignTask(navbar, bob)                                # overdue

    footer = tom.createTask(website, "Update footer",
                            today + timedelta(days=14), Priority.LOW)
    tom.assignTask(footer, alice)

    error_page = tom.createTask(
        website, "Design 404 page", today + timedelta(days=9))
    # Alice: potential overload
    tom.assignTask(error_page, alice)

    # Tasks from Maria (manager), shown separately on dashboards
    audit = maria.createTask(
        website, "Accessibility audit", today + timedelta(days=21))
    maria.assignTask(audit, bob)

    migrate = maria.createTask(mobile, "Migrate user database", today + timedelta(days=30),
                               Priority.HIGH, isHighRisk=True)
    maria.assignTask(migrate, chris)

    # Mobile tasks from Lisa (team leader of Backend and QA)
    api = lisa.createTask(mobile, "Build login API",
                          today + timedelta(days=10), Priority.HIGH)
    lisa.assignTask(api, chris)
    chris.markProgressing(api)

    tests = lisa.createTask(mobile, "Write test plan",
                            today + timedelta(days=6))
    lisa.assignTask(tests, dana)

    return {
        "people": [maria, tom, lisa, alice, bob, chris, dana, evan],
        "projects": [website, mobile],
    }

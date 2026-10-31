"""Demo data for the Part 1 prototype (no database until Part 2).

Login IDs 0, 1 and 2 match the existing login screen and sample_data.py:
  0 = Alice (Manager), 1 = Dilip (Team Leader), 2 = Liam (Employee)

The data is set up to show off the client's requirements in the demo:
  * Dilip leads TWO teams (Team 1 and Team 2)
  * Liam is in TWO teams and is one task away from overload
  * Team 1 has TWO projects
  * Zoe is an intern with an access end date; Tom's access has ended
  * some tasks are overdue, one is high-risk and waiting for approval
  * "Staff Training Portal" has no team yet, for the suggestion demo:
      - Team 3 has a crunch THIS week, then is free
      - Team 4 is quiet this week, but has lots of work over the next 2 months
    So with a deadline 1 week away Team 4 is suggested, and with a
    deadline 3 months away Team 3 is suggested.
Deadlines are worked out from today so the demo always looks the same.
"""

from datetime import date, timedelta

from .models import Employee, Priority, Role, TaskStatus
from .service import OrganisationService


def _day(offset: int) -> date:
    return date.today() + timedelta(days=offset)


def build_demo_organisation() -> OrganisationService:
    service = OrganisationService()

    people = [
        Employee("a.vance@company.co.uk", "Alice", Role.MANAGER, login_id=0),
        Employee("m.sterling@company.co.uk", "Dilip", Role.TEAM_LEADER, login_id=1),
        Employee("l.chen@company.co.uk", "Liam", Role.EMPLOYEE, login_id=2),
        Employee("e.okafor@company.co.uk", "Emma", Role.TEAM_LEADER),
        Employee("p.shah@company.co.uk", "Priya", Role.EMPLOYEE),
        Employee("s.green@company.co.uk", "Sam", Role.EMPLOYEE),
        Employee("j.reid@company.co.uk", "Jordan", Role.TEAM_LEADER),
        Employee("k.ali@company.co.uk", "Kai", Role.EMPLOYEE),
        Employee("z.moore@company.co.uk", "Zoe (intern)", Role.EMPLOYEE, access_ends=_day(40)),
        Employee("t.hale@company.co.uk", "Tom (contractor)", Role.EMPLOYEE, access_ends=_day(-5)),
    ]
    for person in people:
        service.add_employee(person)

    alice, dilip, liam, emma, priya, sam, jordan, kai, zoe, _tom = (p.email for p in people)

    team1 = service.create_team(alice, "Team 1", dilip, [liam, sam])
    team2 = service.create_team(alice, "Team 2", dilip, [liam, priya])
    team3 = service.create_team(alice, "Team 3", jordan, [kai, zoe])
    team4 = service.create_team(alice, "Team 4", emma, [priya])

    def project(name, team, description, deadline):
        new = service.create_project(alice, name, description, deadline)
        if team is not None:
            service.assign_project(alice, new.id, team.id)
        return new

    def task(proj, title, who, days, priority=Priority.MEDIUM, progress=0,
             high_risk=False, description="", status=None):
        new = service.add_task(alice, proj.id, title, who, description,
                               _day(days), priority, high_risk)
        new.progress = progress
        if status is not None:
            new.status = status
        elif progress:
            new.status = TaskStatus.IN_PROGRESS
        return new

    sso = project("Cloud Auth & SSO Migration", team1,
                  "Move all staff logins to single sign-on.", _day(30))
    task(sso, "Configure passphrase validator", liam, -3, Priority.CRITICAL, 65, True,
         "Minimum length checks and a blocklist of common passwords.")
    task(sso, "Build multi-device session handler", liam, 6, Priority.HIGH, 40)
    task(sso, "Audit contractor offboarding script", sam, 12, Priority.MEDIUM, 100, True,
         "Check that removing a contractor ends their sessions.",
         status=TaskStatus.PENDING_APPROVAL)

    reset = project("Password Reset Portal", team1,
                    "Self-service password resets for staff.", _day(45))
    task(reset, "Design reset screens", liam, 10, Priority.MEDIUM, 20)
    task(reset, "Email verification step", sam, 15, Priority.HIGH)

    kb = project("Internal Knowledge Base & Forum", team2,
                 "Topics and posts for sharing technical and admin knowledge.", _day(40))
    task(kb, "Rich text and link support", liam, 2, Priority.HIGH, 80)
    task(kb, "Moderation tools", dilip, -10, Priority.MEDIUM, 0, True)
    task(kb, "Write posting guidelines", priya, 8, Priority.LOW, 50)

    # Team 3: a crunch this week, then free.
    audit = project("Q4 Security & Infrastructure Audit", team3,
                    "Review privileged accounts and network access.", _day(25))
    task(audit, "Patch VPN servers", kai, 6, Priority.CRITICAL, 0, True)
    task(audit, "Firewall rule review", jordan, 5, Priority.HIGH)
    task(audit, "Write up audit findings", zoe, 20, Priority.LOW)

    # Team 4: quiet this week, busy over the next two months.
    planning = project("Executive Resource Planning", team4,
                       "Forecast workload and training needs.", _day(80))
    task(planning, "Q1 department capacity forecast", emma, 40)
    task(planning, "Training needs survey", emma, 50, Priority.HIGH)
    task(planning, "Department budget review", emma, 60, Priority.CRITICAL)
    task(planning, "Leadership course outline", emma, 75)
    task(planning, "New starter handbook", priya, 70, Priority.HIGH)

    # Not assigned yet: ready for the "suggest a team" part of the demo.
    project("Staff Training Portal", None,
            "An online course library for new starters.", _day(90))

    return service


# One shared copy for the whole app, so every screen sees the same data.
organisation = build_demo_organisation()

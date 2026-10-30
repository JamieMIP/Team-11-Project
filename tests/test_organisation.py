"""Tests for the organisation package. Run with:  python -m pytest tests -v

Each test names the client rule (Q&A 16 Oct) or team decision it checks.
"""

from datetime import date, timedelta

import pytest

from organisation import (InvalidAction, Permission, PermissionDenied, Priority, Role,
                          TaskStatus, build_demo_organisation)
from organisation.models import ProjectTask

ALICE = "a.vance@company.co.uk"      # Manager
DILIP = "m.sterling@company.co.uk"   # Team Leader of Team 1 and Team 2
LIAM = "l.chen@company.co.uk"        # Employee in Team 1 and Team 2
PRIYA = "p.shah@company.co.uk"       # Employee in Team 2 and Team 4
JORDAN = "j.reid@company.co.uk"      # Team Leader of Team 3
ZOE = "z.moore@company.co.uk"        # Intern, access ends in 40 days
TOM = "t.hale@company.co.uk"         # Contractor, access already ended


def in_days(days):
    return date.today() + timedelta(days=days)


@pytest.fixture
def org():
    """A fresh copy of the demo data for every test."""
    return build_demo_organisation()


def team_named(org, name):
    return next(team for team in org.all_teams() if team.name == name)


def project_named(org, name):
    return next(project for project in org.all_projects() if project.name == name)


def new_team_project(org, team_name="Team 2", deadline_days=60):
    """A fresh project assigned to a team, for tests that add tasks."""
    project = org.create_project(ALICE, "Test project", deadline=in_days(deadline_days))
    org.assign_project(ALICE, project.id, team_named(org, team_name).id)
    return project


# ----- roles -----

def test_role_permissions():
    """Each role's abilities, matching the role table in the docs."""
    org = build_demo_organisation()
    assert not org.can(LIAM, Permission.VIEW_DASHBOARD)
    assert org.can(DILIP, Permission.MANAGE_TASKS)
    assert not org.can(DILIP, Permission.CREATE_TEAMS)
    assert all(org.can(ALICE, permission) for permission in Permission)


def test_manager_changes_roles_both_ways(org):                  # admin Q4
    org.change_role(ALICE, PRIYA, Role.TEAM_LEADER)
    org.change_role(ALICE, PRIYA, Role.EMPLOYEE)
    assert org.get_employee(PRIYA).role is Role.EMPLOYEE


def test_manager_cannot_change_own_role(org):
    with pytest.raises(InvalidAction):
        org.change_role(ALICE, ALICE, Role.EMPLOYEE)


def test_cannot_demote_someone_still_leading_a_team(org):
    with pytest.raises(InvalidAction):
        org.change_role(ALICE, DILIP, Role.EMPLOYEE)


def test_leader_cannot_change_roles(org):
    with pytest.raises(PermissionDenied):
        org.change_role(DILIP, LIAM, Role.TEAM_LEADER)


# ----- temporary staff (admin Q3) -----

def test_ended_access_blocks_new_work(org):
    assert not org.get_employee(TOM).is_active()
    with pytest.raises(InvalidAction):
        org.add_member(ALICE, team_named(org, "Team 1").id, TOM)


def test_ending_access_stops_new_tasks(org):
    project = project_named(org, "Q4 Security & Infrastructure Audit")
    org.add_task(ALICE, project.id, "Fine while active", ZOE)
    org.set_access_end(ALICE, ZOE, in_days(-1))
    with pytest.raises(InvalidAction):
        org.add_task(ALICE, project.id, "Too late", ZOE)


# ----- teams -----

def test_manager_creates_team_with_leader(org):                 # PM Q10
    team = org.create_team(ALICE, "Team 5", JORDAN, [PRIYA])
    assert team.leader_email == JORDAN
    assert PRIYA in team.everyone()


def test_team_must_have_a_leader(org):
    with pytest.raises(InvalidAction):
        org.create_team(ALICE, "Team 5", "")


def test_only_managers_create_teams(org):                       # PM Q10
    with pytest.raises(PermissionDenied):
        org.create_team(DILIP, "Dilip's team", DILIP)


def test_duplicate_team_name_rejected(org):
    with pytest.raises(InvalidAction):
        org.create_team(ALICE, "team 1", DILIP)


def test_one_person_can_lead_several_teams(org):                # PM Q9
    assert {team.name for team in org.teams_led_by(DILIP)} == {"Team 1", "Team 2"}


def test_each_team_has_only_one_leader(org):                    # PM Q9
    team = team_named(org, "Team 1")
    org.appoint_leader(ALICE, team.id, JORDAN)
    assert team.leader_email == JORDAN
    assert team not in org.teams_led_by(DILIP)


def test_appointing_an_employee_promotes_them(org):
    org.appoint_leader(ALICE, team_named(org, "Team 2").id, PRIYA)
    assert org.get_employee(PRIYA).role is Role.TEAM_LEADER


def test_leader_cannot_be_removed(org):
    team = team_named(org, "Team 1")
    with pytest.raises(InvalidAction):
        org.remove_member(ALICE, team.id, DILIP)


def test_employee_can_be_in_several_teams(org):
    assert {team.name for team in org.teams_for(LIAM)} == {"Team 1", "Team 2"}


def test_removing_member_returns_their_unfinished_tasks(org):   # PM Q8
    leftover = org.remove_member(ALICE, team_named(org, "Team 1").id, LIAM)
    assert leftover and all(task.assignee_email == LIAM for task in leftover)


# ----- projects -----

def test_team_can_hold_several_projects(org):
    assert len(org.projects_for_team(team_named(org, "Team 1").id)) == 2


def test_project_flow_create_assign_add_task(org):
    project = org.create_project(ALICE, "New intranet", deadline=in_days(60))
    with pytest.raises(InvalidAction):                  # no team yet
        org.add_task(ALICE, project.id, "Too early")
    best = org.suggest_teams(project.id)[0].team
    org.assign_project(ALICE, project.id, best.id)
    task = org.add_task(ALICE, project.id, "Wireframes", best.leader_email)
    assert task in project.tasks


def test_only_managers_create_projects(org):
    with pytest.raises(PermissionDenied):
        org.create_project(DILIP, "Dilip's project")


def test_project_cannot_change_team_once_it_has_tasks(org):
    project = project_named(org, "Password Reset Portal")
    with pytest.raises(InvalidAction):
        org.assign_project(ALICE, project.id, team_named(org, "Team 3").id)


def test_project_progress_is_average_of_tasks(org):             # PM Q1
    project = new_team_project(org)
    first = org.add_task(ALICE, project.id, "A", LIAM)
    org.add_task(ALICE, project.id, "B", LIAM)
    org.update_progress(LIAM, project.id, first.id, 50)
    assert project.progress() == 25


def test_task_deadline_cannot_be_after_project_deadline(org):
    project = new_team_project(org, deadline_days=10)
    with pytest.raises(InvalidAction):
        org.add_task(ALICE, project.id, "Late", LIAM, deadline=in_days(20))
    task = org.add_task(ALICE, project.id, "On time", LIAM, deadline=in_days(5))
    with pytest.raises(InvalidAction):
        org.edit_task(ALICE, project.id, task.id, deadline=in_days(20))


# ----- team suggestion: capacity before the deadline, weighted by priority -----

def test_remaining_work_uses_progress_and_priority():
    task = ProjectTask("X", "PRJ-0", ALICE, priority=Priority.HIGH, progress=40)
    assert task.remaining_work() == pytest.approx(0.9)      # 0.6 left x 1.5


def test_critical_task_counts_more_than_low(org):
    def team_load(priority):
        fresh = build_demo_organisation()
        team = fresh.create_team(ALICE, "Quiet team", JORDAN)
        project = fresh.create_project(ALICE, "P", deadline=in_days(30))
        fresh.assign_project(ALICE, project.id, team.id)
        busy_before = fresh.team_weekly_load(team, in_days(30))[0]
        fresh.add_task(ALICE, project.id, "T", JORDAN, deadline=in_days(10), priority=priority)
        return fresh.team_weekly_load(team, in_days(30))[0] - busy_before
    assert team_load(Priority.CRITICAL) == pytest.approx(4 * team_load(Priority.LOW))


def test_work_due_after_the_deadline_is_ignored(org):
    team4 = team_named(org, "Team 4")                   # all its work is 40+ days away
    assert org.team_weekly_load(team4, in_days(7)) == (0.0, 0)


def test_overdue_work_is_counted(org):
    team2 = team_named(org, "Team 2")                   # Dilip's moderation task is overdue
    _, counted = org.team_weekly_load(team2, in_days(1))
    assert counted >= 1


def test_short_deadline_suggests_team_4_long_deadline_suggests_team_3(org):
    project = project_named(org, "Staff Training Portal")
    org.set_project_deadline(ALICE, project.id, in_days(7))
    assert org.suggest_teams(project.id)[0].team.name == "Team 4"
    org.set_project_deadline(ALICE, project.id, in_days(90))
    assert org.suggest_teams(project.id)[0].team.name == "Team 3"


def test_suggestion_scores_are_sorted_best_first(org):
    project = project_named(org, "Staff Training Portal")
    scores = [row.score for row in org.suggest_teams(project.id)]
    assert scores == sorted(scores, reverse=True)
    assert all(0 <= score <= 100 for score in scores)


# ----- tasks and access levels -----

def test_leader_can_add_tasks_only_in_own_teams(org):           # PM Q4, Q5
    own = project_named(org, "Password Reset Portal")
    other = project_named(org, "Q4 Security & Infrastructure Audit")
    org.add_task(DILIP, own.id, "Fine", LIAM)
    with pytest.raises(PermissionDenied):
        org.add_task(DILIP, other.id, "Not my team")


def test_employee_cannot_assign_tasks(org):                     # PM Q4
    with pytest.raises(PermissionDenied):
        org.add_task(LIAM, project_named(org, "Password Reset Portal").id, "Nope")


def test_assignee_must_be_in_the_team(org):
    with pytest.raises(InvalidAction):
        org.add_task(ALICE, project_named(org, "Password Reset Portal").id, "X", JORDAN)


def test_employee_updates_only_own_tasks(org):                  # PM Q1
    project = project_named(org, "Cloud Auth & SSO Migration")
    mine = next(task for task in project.tasks if task.assignee_email == LIAM)
    not_mine = next(task for task in project.tasks if task.assignee_email != LIAM)
    org.update_progress(LIAM, project.id, mine.id, 70)
    with pytest.raises(PermissionDenied):
        org.update_progress(LIAM, project.id, not_mine.id, 70)


def test_routine_task_completed_without_approval(org):          # PM Q2
    project = new_team_project(org)
    task = org.add_task(ALICE, project.id, "Routine", LIAM)
    assert org.complete_task(LIAM, project.id, task.id).status is TaskStatus.DONE


def test_high_risk_task_needs_approval(org):                    # PM Q2
    project = new_team_project(org)
    task = org.add_task(ALICE, project.id, "Risky", LIAM, high_risk=True)
    assert org.complete_task(LIAM, project.id, task.id).status is TaskStatus.PENDING_APPROVAL
    assert org.complete_task(DILIP, project.id, task.id).status is TaskStatus.DONE


def test_leader_can_reopen_and_change_deadline(org):            # PM Q2, Q3
    project = new_team_project(org)
    task = org.add_task(DILIP, project.id, "Job", LIAM)
    org.complete_task(LIAM, project.id, task.id)
    org.reopen_task(DILIP, project.id, task.id)
    org.edit_task(DILIP, project.id, task.id, deadline=in_days(30), priority=Priority.HIGH)
    assert task.status is TaskStatus.IN_PROGRESS
    assert (task.deadline, task.priority) == (in_days(30), Priority.HIGH)


def test_employee_cannot_delete_tasks(org):
    project = project_named(org, "Password Reset Portal")
    with pytest.raises(PermissionDenied):
        org.delete_task(LIAM, project.id, project.tasks[0].id)


def test_my_tasks_spans_all_teams(org):
    projects = {project.name for project, _ in org.tasks_for_employee(LIAM)}
    assert "Internal Knowledge Base & Forum" in projects          # Team 2
    assert "Cloud Auth & SSO Migration" in projects               # Team 1


# ----- dashboard -----

def test_overload_is_flagged_not_blocked(org):                  # PM Q11
    project = project_named(org, "Password Reset Portal")
    assert not org.is_overloaded(LIAM)                          # 4 tasks
    org.add_task(ALICE, project.id, "One more", LIAM)           # still allowed
    assert org.is_overloaded(LIAM)                              # 5 tasks


def test_overdue_tasks_on_dashboard(org):                       # PM Q6
    overdue = org.overdue_tasks(ALICE)
    assert overdue and all(task.is_overdue() for _, task in overdue)


def test_leader_dashboard_only_shows_own_teams(org):            # data protection
    assert {team.name for team in org.dashboard_teams(DILIP)} == {"Team 1", "Team 2"}
    assert JORDAN not in {person.email for person in org.dashboard_people(DILIP)}


def test_employee_has_no_dashboard(org):
    with pytest.raises(PermissionDenied):
        org.dashboard_teams(LIAM)

"""Unit tests for the task management rules. Run with: python -m unittest"""

import unittest
from datetime import date, timedelta

from project_task.models import (
    Employee,
    InvalidAction,
    Manager,
    PermissionDenied,
    Priority,
    Project,
    TaskStatus,
    TeamLeader,
)

TODAY = date.today()


class TaskManagementTestCase(unittest.TestCase):
    def setUp(self):
        Project.clearAll()
        self.manager = Manager("M01", "Maria", "maria@company.com")
        self.leader = TeamLeader("L01", "Tom", "tom@company.com")
        self.other_leader = TeamLeader("L02", "Lisa", "lisa@company.com")
        self.alice = Employee("E01", "Alice", "alice@company.com")
        self.bob = Employee("E02", "Bob", "bob@company.com")
        self.dana = Employee("E03", "Dana", "dana@company.com")

        self.frontend = self.manager.createTeam("Frontend")
        self.qa = self.manager.createTeam("QA")
        self.manager.appointTeamLeader(self.frontend, self.leader)
        self.manager.appointTeamLeader(self.qa, self.other_leader)
        self.frontend.addMember(self.alice)
        self.frontend.addMember(self.bob)
        self.qa.addMember(self.dana)

        self.project = Project("Website")

    def make_task(self, days=5, high_risk=False, assignee=None, creator=None):
        creator = creator or self.leader
        task = creator.createTask(self.project, "Task", TODAY + timedelta(days=days),
                                  Priority.MEDIUM, high_risk)
        creator.assignTask(task, assignee or self.alice)
        return task


class TestEmployee(TaskManagementTestCase):
    def test_employee_updates_own_task_status(self):
        task = self.make_task()
        self.alice.markProgressing(task)
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)
        self.alice.markToDo(task)
        self.assertEqual(task.status, TaskStatus.TO_DO)

    def test_routine_task_completes_without_approval(self):
        task = self.make_task()
        needs_approval = self.alice.markDone(task)
        self.assertFalse(needs_approval)
        self.assertTrue(task.isComplete())

    def test_employee_cannot_update_someone_elses_task(self):
        task = self.make_task()
        with self.assertRaises(PermissionDenied):
            self.bob.markDone(task)

    def test_employee_cannot_assign_tasks(self):
        self.assertFalse(hasattr(self.alice, "assignTask"))


class TestApproval(TaskManagementTestCase):
    def test_high_risk_task_needs_approval(self):
        task = self.make_task(high_risk=True)
        self.assertTrue(self.alice.markDone(task))
        self.assertTrue(task.isAwaitingApproval())
        self.assertFalse(task.isComplete())
        self.leader.approveTask(task)
        self.assertTrue(task.isComplete())

    def test_reopen_returns_task_to_progress(self):
        task = self.make_task(high_risk=True)
        self.alice.markDone(task)
        self.leader.reopenTask(task)
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)
        self.assertFalse(task.isApproved)

    def test_routine_task_cannot_be_approved(self):
        task = self.make_task()
        self.alice.markDone(task)
        with self.assertRaises(InvalidAction):
            self.leader.approveTask(task)

    def test_approved_task_cannot_be_changed_by_employee(self):
        task = self.make_task(high_risk=True)
        self.alice.markDone(task)
        self.leader.approveTask(task)
        with self.assertRaises(InvalidAction):
            self.alice.markToDo(task)


class TestOverdue(TaskManagementTestCase):
    def test_overdue_task_stays_open_and_is_highlighted(self):
        task = self.make_task(days=-2)
        self.assertTrue(task.makeOverdue())
        self.assertNotEqual(task.status, TaskStatus.DONE)
        for person in (self.alice, self.leader, self.manager):
            self.assertIn(task, person.dashboard.highlightOverdueTask())

    def test_overdue_status_is_kept_while_working(self):
        task = self.make_task(days=-2)
        task.makeOverdue()
        self.alice.markProgressing(task)
        self.assertEqual(task.status, TaskStatus.OVERDUE)

    def test_new_deadline_clears_overdue(self):
        task = self.make_task(days=-2)
        task.makeOverdue()
        self.leader.changeDeadline(task, TODAY + timedelta(days=3))
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)


class TestAreaOfResponsibility(TaskManagementTestCase):
    def test_leader_cannot_assign_outside_their_teams(self):
        task = self.leader.createTask(self.project, "Task", TODAY)
        with self.assertRaises(PermissionDenied):
            self.leader.assignTask(task, self.dana)

    def test_leader_cannot_change_tasks_in_other_teams(self):
        task = self.make_task(assignee=self.dana, creator=self.other_leader)
        with self.assertRaises(PermissionDenied):
            self.leader.changePriority(task, Priority.HIGH)

    def test_leader_changes_priority_in_own_team(self):
        task = self.make_task()
        self.leader.changePriority(task, Priority.HIGH)
        self.assertEqual(task.priority, Priority.HIGH)

    def test_manager_can_reassign_across_teams(self):
        task = self.make_task()
        self.manager.reassignTask(task, self.dana)
        self.assertIs(task.assignee, self.dana)


class TestTeams(TaskManagementTestCase):
    def test_one_leader_can_lead_several_teams(self):
        self.manager.appointTeamLeader(self.qa, self.leader)
        self.assertEqual(len(self.leader.teamsLed), 2)

    def test_each_team_has_only_one_leader(self):
        self.manager.appointTeamLeader(self.qa, self.leader)
        self.assertIs(self.qa.leader, self.leader)
        self.assertNotIn(self.qa, self.other_leader.teamsLed)

    def test_leader_cannot_create_teams(self):
        self.assertFalse(hasattr(self.leader, "createTeam"))

    def test_removing_member_returns_unfinished_tasks(self):
        task = self.make_task()
        unfinished = self.frontend.removeMember(self.alice)
        self.assertEqual(unfinished, [task])
        self.assertIs(task.assignee, self.alice)   # not reassigned automatically


class TestDashboardAndProgress(TaskManagementTestCase):
    def test_overload_warns_but_does_not_block(self):
        for _ in range(3):
            self.make_task()
        task = self.leader.createTask(self.project, "Extra", TODAY)
        overloaded = self.leader.assignTask(task, self.alice)
        self.assertTrue(overloaded)
        self.assertIs(task.assignee, self.alice)

    def test_tasks_grouped_by_who_assigned_them(self):
        by_leader = self.make_task()
        by_manager = self.make_task(creator=self.manager)
        groups = self.alice.dashboard.show()
        self.assertEqual(groups["teamLeader"], [by_leader])
        self.assertEqual(groups["manager"], [by_manager])

    def test_project_progress(self):
        done = self.make_task()
        self.make_task()
        self.alice.markDone(done)
        self.assertEqual(self.project.showProgress(), 50.0)


if __name__ == "__main__":
    unittest.main()

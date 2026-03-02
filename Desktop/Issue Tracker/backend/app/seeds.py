from .database import SessionLocal
from .models import Project, User, Issue, Comment, PriorityEnum, StatusEnum
from datetime import datetime


def seed_data():
    db = SessionLocal()

    db.query(Comment).delete()
    db.query(Issue).delete()
    db.query(User).delete()
    db.query(Project).delete()
    db.commit()

    projects = [
        Project(name="Website Redesign"),
        Project(name="Mobile App"),
        Project(name="Internal CRM"),
        Project(name="Analytics Dashboard"),
    ]

    db.add_all(projects)
    db.commit()

    users = [
        User(name="Ayaan", email="ayaan@example.com"),
        User(name="Sarah", email="sarah@example.com"),
        User(name="Rahul", email="rahul@example.com"),
        User(name="Fatima", email="fatima@example.com"),
        User(name="David", email="david@example.com"),
    ]

    db.add_all(users)
    db.commit()

    for project in projects:
        db.refresh(project)

    for user in users:
        db.refresh(user)

    issues = [
        Issue(
            title="Login page crashes",
            description="App crashes when invalid credentials are entered.",
            project_id=projects[1].id,
            assignee_id=users[0].id,
            priority=PriorityEnum.high,
            status=StatusEnum.open,
        ),
        Issue(
            title="Dashboard not loading data",
            description="API response not showing on frontend.",
            project_id=projects[3].id,
            assignee_id=users[2].id,
            priority=PriorityEnum.critical,
            status=StatusEnum.in_progress,
        ),
        Issue(
            title="Button misaligned",
            description="Submit button is not centered.",
            project_id=projects[0].id,
            assignee_id=users[1].id,
            priority=PriorityEnum.low,
            status=StatusEnum.resolved,
        ),
        Issue(
            title="CRM export slow",
            description="Exporting CSV takes too long.",
            project_id=projects[2].id,
            assignee_id=users[3].id,
            priority=PriorityEnum.medium,
            status=StatusEnum.open,
        ),
    ]

    db.add_all(issues)
    db.commit()

    for issue in issues:
        db.refresh(issue)

    comments = [
        Comment(
            issue_id=issues[0].id,
            user_id=users[1].id,
            content="Investigating this issue."
        ),
        Comment(
            issue_id=issues[1].id,
            user_id=users[2].id,
            content="Working on API fix."
        ),
    ]

    db.add_all(comments)
    db.commit()

    db.close()

    print("Database seeded successfully!")


if __name__ == "__main__":
    seed_data()
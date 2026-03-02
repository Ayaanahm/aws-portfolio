import csv
from io import StringIO
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/issues", tags=["Issues"])


# ---------------------------
# ISSUE STATUS COUNTS
# ---------------------------
@router.get("/stats")
def get_issue_stats(db: Session = Depends(get_db)):
    results = (
        db.query(models.Issue.status, func.count(models.Issue.id))
        .group_by(models.Issue.status)
        .all()
    )

    stats = {status.value: count for status, count in results}

    for status in schemas.StatusEnum:
        if status.value not in stats:
            stats[status.value] = 0

    return stats


# ---------------------------
# EXPORT ISSUES AS CSV
# ---------------------------
@router.get("/export")
def export_issues(db: Session = Depends(get_db)):
    issues = db.query(models.Issue).all()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Title",
        "Description",
        "Project ID",
        "Assignee ID",
        "Priority",
        "Status",
        "Created At",
        "Updated At"
    ])

    for issue in issues:
        writer.writerow([
            issue.id,
            issue.title,
            issue.description,
            issue.project_id,
            issue.assignee_id,
            issue.priority.value,
            issue.status.value,
            issue.created_at,
            issue.updated_at
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=issues.csv"},
    )


# ---------------------------
# GET ALL ISSUES (WITH FILTERING + PAGINATION)
# ---------------------------
@router.get("/", response_model=schemas.IssueListResponse)
def get_issues(
    project_id: Optional[int] = None,
    priority: Optional[schemas.PriorityEnum] = None,
    status: Optional[schemas.StatusEnum] = None,
    assignee_id: Optional[int] = None,
    search: Optional[str] = Query(None, min_length=2),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: Optional[str] = None,
    order: Optional[str] = "asc",
    db: Session = Depends(get_db),
):
    query = db.query(models.Issue)

    if project_id:
        query = query.filter(models.Issue.project_id == project_id)

    if priority:
        query = query.filter(models.Issue.priority == priority)

    if status:
        query = query.filter(models.Issue.status == status)

    if assignee_id:
        query = query.filter(models.Issue.assignee_id == assignee_id)

    if search:
        query = query.filter(
            or_(
                models.Issue.title.ilike(f"%{search}%"),
                models.Issue.description.ilike(f"%{search}%"),
            )
        )
    if sort:
        if hasattr(models.Issue, sort):
            column = getattr(models.Issue, sort)
            if order == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
    total = query.count()
    issues = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": issues,
    }


# ---------------------------
# CREATE ISSUE
# ---------------------------
@router.post("/", response_model=schemas.IssueResponse, status_code=201)
def create_issue(issue: schemas.IssueCreate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == issue.project_id).first()
    if not project:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    user = db.query(models.User).filter(models.User.id == issue.assignee_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid assignee_id")

    new_issue = models.Issue(**issue.model_dump())

    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    return new_issue


# ---------------------------
# UPDATE ISSUE STATUS
# ---------------------------
@router.patch("/{issue_id}", response_model=schemas.IssueResponse)
def update_issue(issue_id: int, update: schemas.IssueUpdate, db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue.status = update.status

    db.commit()
    db.refresh(issue)

    return issue


# ---------------------------
# ADD COMMENT TO ISSUE
# ---------------------------
@router.post("/{issue_id}/comments", response_model=schemas.CommentResponse, status_code=201)
def add_comment(issue_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    user = db.query(models.User).filter(models.User.id == comment.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    new_comment = models.Comment(
        issue_id=issue_id,
        user_id=comment.user_id,
        content=comment.content,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


# ---------------------------
# GET ISSUE BY ID (KEEP LAST)
# ---------------------------
@router.get("/{issue_id}", response_model=schemas.IssueResponse)
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    return issue
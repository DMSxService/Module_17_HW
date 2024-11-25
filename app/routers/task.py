from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete
from slugify import slugify
from typing import Annotated
from app.backend.db_depends import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas import CreateTask, UpdateTask

router = APIRouter(prefix="/task", tags=["task"])


@router.get("/")
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    return tasks


@router.get("/task_id")
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found')
    return task


@router.post("/create")
async def create_task(db: Annotated[Session, Depends(get_db)], user_id: int, cr_task: CreateTask):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found')
    task_id = 1
    tasks = list(db.scalars(select(Task)).all())
    if len(tasks):
        last_element = tasks[-1]
        task_id = last_element.id + 1
    db.execute(insert(Task).values(
        id=task_id,
        title=cr_task.title,
        content=cr_task.content,
        priority=cr_task.priority,
        user_id=user_id,
        slug=slugify(cr_task.title)))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put("/update")
async def update_task(db: Annotated[Session, Depends(get_db)], task_id: int, up_task: UpdateTask):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found')

    db.execute(update(Task).where(Task.id == task_id).values(
        title=up_task.title,
        content=up_task.content,
        priority=up_task.priority
    ))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task update is successful'
    }


@router.delete("/delete")
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found')
    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task delete is successful'
    }

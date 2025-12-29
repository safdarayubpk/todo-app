"""
FastAPI CRUD Route Template
============================
Copy and customize this template for new resources.

Replace:
- {Resource} with your model name (e.g., Task)
- {resource} with lowercase name (e.g., task)
- {resources} with plural lowercase (e.g., tasks)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.auth import get_current_user
from app.models.user import User
from app.models.{resource} import {Resource}, {Resource}Create, {Resource}Read, {Resource}Update

router = APIRouter(prefix="/{resources}", tags=["{Resources}"])


@router.get("", response_model=list[{Resource}Read])
async def list_{resources}(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    List all {resources} for the current user.

    Returns:
        List of {resource} objects belonging to the authenticated user.
    """
    statement = select({Resource}).where({Resource}.user_id == current_user.id)
    result = await session.exec(statement)
    return result.all()


@router.get("/{id}", response_model={Resource}Read)
async def get_{resource}(
    id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get a specific {resource} by ID.

    Args:
        id: The {resource} ID.

    Returns:
        The {resource} object if found and owned by user.

    Raises:
        404: {Resource} not found.
        403: {Resource} belongs to another user.
    """
    {resource} = await session.get({Resource}, id)
    if not {resource}:
        raise HTTPException(status_code=404, detail="{Resource} not found")
    if {resource}.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return {resource}


@router.post("", response_model={Resource}Read, status_code=status.HTTP_201_CREATED)
async def create_{resource}(
    {resource}_in: {Resource}Create,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new {resource}.

    Args:
        {resource}_in: The {resource} data to create.

    Returns:
        The created {resource} object.
    """
    {resource} = {Resource}(**{resource}_in.model_dump(), user_id=current_user.id)
    session.add({resource})
    await session.commit()
    await session.refresh({resource})
    return {resource}


@router.put("/{id}", response_model={Resource}Read)
async def update_{resource}(
    id: int,
    {resource}_in: {Resource}Update,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Update a {resource}.

    Args:
        id: The {resource} ID.
        {resource}_in: The fields to update.

    Returns:
        The updated {resource} object.

    Raises:
        404: {Resource} not found.
        403: {Resource} belongs to another user.
    """
    {resource} = await session.get({Resource}, id)
    if not {resource}:
        raise HTTPException(status_code=404, detail="{Resource} not found")
    if {resource}.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = {resource}_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr({resource}, key, value)

    session.add({resource})
    await session.commit()
    await session.refresh({resource})
    return {resource}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{resource}(
    id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a {resource}.

    Args:
        id: The {resource} ID.

    Raises:
        404: {Resource} not found.
        403: {Resource} belongs to another user.
    """
    {resource} = await session.get({Resource}, id)
    if not {resource}:
        raise HTTPException(status_code=404, detail="{Resource} not found")
    if {resource}.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await session.delete({resource})
    await session.commit()

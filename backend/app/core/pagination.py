"""Pagination utility functions."""

from typing import List, TypeVar

T = TypeVar("T")


def create_pagination(
    items: List[T],
    total: int,
    page: int,
    page_size: int,
) -> dict:
    """Create a paginated response dictionary.
    
    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number (1-indexed)
        page_size: Number of items per page
    
    Returns:
        Dictionary with pagination metadata
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def calculate_skip(page: int, page_size: int) -> int:
    """Calculate skip value for database query.
    
    Args:
        page: Page number (1-indexed)
        page_size: Items per page
    
    Returns:
        Number of items to skip
    """
    return (page - 1) * page_size
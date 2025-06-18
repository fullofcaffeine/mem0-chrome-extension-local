import uuid, pytest

@pytest.fixture
def user_id():
    """Provide a unique user_id per test run."""
    return f"pytest-{uuid.uuid4().hex[:8]}" 

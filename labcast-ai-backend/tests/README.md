# LabCast AI Backend Tests

This directory contains the test suite for the LabCast AI Backend.

## Running the Tests

To run the full test suite, simply execute the following command from the root of the project:

```bash
pytest -v
```

All tests are designed to run against an **isolated, temporary in-memory SQLite database** (`sqlite:///:memory:`). This means you can run the test suite as often as you like without worrying about it wiping, modifying, or reading from your real development database (`labcast.db`).

## Test Coverage

* **`test_chatbot.py`**: Tests the RAG (Retrieval-Augmented Generation) pipeline. It verifies that the `InMemoryRetriever` isolates context properly so that querying one machine does not retrieve manual snippets from another machine.
* **`test_routers_machine.py`**: Tests the CRUD REST API endpoints for the machines (e.g., fetching configs, updating SOPs, and toggling emergency states).
* **`test_seed.py`**: Tests the database seeding script (`scripts/seed.py`) to ensure it correctly populates the database with the required demo machines (CNC01, LATHE02, LASER03) and their associated long-form manuals.

# pyorgtree

`pyorgtree` is a Python package designed for robust parsing, manipulation, and serialization of Org-mode files. It provides a programmatic interface to interact with Org-mode's hierarchical structure, allowing developers to read, modify, and write Org-mode content with ease.

## Features

*   **Org-mode File Parsing:** Reads and interprets Org-mode files, recognizing headings, levels, tags, and associated content.
*   **Tree Representation:** Represents the Org-mode file's structure as a navigable tree, where each heading corresponds to a node.
*   **Data Extraction:** Provides methods to extract various data points from Org-mode entries, including:
    *   Headers (title, level, tags)
    *   Raw content associated with a heading
    *   Scheduled and Deadline timestamps
    *   Properties drawers
*   **Tag-based Access:** Allows retrieval of Org-mode trees (subtrees) based on their assigned tags.
*   **File Writing:** Supports writing the in-memory Org-mode tree structure back to a `.org` file.
*   **Serialization:** Enables serialization and deserialization of Org-mode trees using Python's `pickle` module for persistent storage and quick loading.
*   **Hashed Tree Support:** Includes functionality for working with hashed Org-mode entries, facilitating unique identification and potential change tracking.

## Installation

You can install `pyorgtree` using pip:

```bash
pip install pyorgtree
```

## Usage

Here's a basic example of how to use `pyorgtree` to read an Org-mode file and access its content:

```python
from pyorgtree.pyorgtree import OrgTree

# Create a root OrgTree object
root_tree = OrgTree()

# Read an Org-mode file
# Assuming 'example.org' exists in the same directory or provide a full path
if root_tree.read_from_file('example.org', 0, 0):
    print("Successfully read example.org")

    # Iterate through the tree
    for node in root_tree:
        if node.get_header():
            print(f"Level: {node.get_header().get_level()}, Title: {node.get_header().get_title()}")
            if node.get_header().has_tags():
                print(f"Tags: {', '.join(node.get_header().get_tags())}")
            if node.has_schedule():
                print(f"Scheduled: {node.get_schedule().get_timestamp()}")
            if node.has_deadline():
                print(f"Deadline: {node.get_deadline().get_timestamp()}")
            if node.has_properties():
                print("Properties:")
                for key, value in node.get_properties().items():
                    print(f"  {key}: {value}")
            print(f"Content:\n{node.get_data()}")
            print("-" * 20)
else:
    print("Failed to read example.org")

# Example of writing to a file (assuming modifications were made to root_tree)
# root_tree.write_to_file('modified_example.org')
```

## Running Tests

To run the unit tests for `pyorgtree`, navigate to the root directory of the project and execute the following command using `pytest`:

```bash
pytest unittests/
```

This command will discover and run all tests located in the `unittests/` directory.

## Project Status

`pyorgtree` is currently NOT under active development. For bug reports, feature requests, or contributions, please visit the [Bug Tracker](https://github.com/andreimatveyeu/pyorgtree/issues).

## Feature Ideas

Here are some potential features that could enhance `pyorgtree`:

*   **Advanced Node Querying:** Implement a more sophisticated query language or API to filter and retrieve nodes based on multiple criteria, such as property values, TODO states, or date ranges for scheduled/deadline timestamps.
*   **TODO Keyword Management:** Add dedicated methods for managing TODO states, including cycling through predefined TODO sequences (e.g., `TODO` -> `IN-PROGRESS` -> `DONE`) and retrieving tasks by their current state.
*   **Export Capabilities:** Introduce functionality to export Org-mode trees or specific subtrees to common formats like Markdown, JSON, or even a simplified HTML representation. This would increase interoperability with other tools and workflows.
*   **Support for Org Tables:** Extend the parser to recognize and manipulate Org-mode tables, allowing for data extraction and modification within tabular structures.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

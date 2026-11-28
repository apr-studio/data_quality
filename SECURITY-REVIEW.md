# Security review

## Output path symlink redirection

- **Severity:** Medium
- **Location:** `infrastructure/paths.py`
- **Finding:** A symlink at an output directory or file path could redirect generated reports or logs outside the project root.
- **Resolution:** Output paths are checked after resolution to ensure they remain under the project root, and symlink output directories and target files are rejected.
- **Residual limitation:** The helper returns a `Path` for another component to open later. A local actor able to replace path components concurrently could still race between validation and file opening. Eliminating that race requires opening files relative to a verified directory handle in each output component.

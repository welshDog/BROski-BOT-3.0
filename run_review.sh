#!/bin/bash

# Create output directory if it doesn't exist
mkdir -p review_reports

# Run the code review using python3 instead of python
python3 utils/code_review_tool.py --dir . --output review_reports/full_review.md

echo "Review completed. See review_reports/full_review.md for results."

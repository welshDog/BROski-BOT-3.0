#!/bin/bash
# Run the final code review on key refactored modules

# Create output directory for reports
mkdir -p review_reports

echo "Running code review on key modules..."

# Check strategy base classes
python utils/code_review_tool.py --dir strategies/base.py --output review_reports/strategies_base_review.md

# Check UI components
python utils/code_review_tool.py --dir ui/components --output review_reports/ui_components_review.md

# Check data processors
python utils/code_review_tool.py --dir utils/dashboard --output review_reports/utils_dashboard_review.md

# Check indicator modules
python utils/code_review_tool.py --dir utils/indicators --output review_reports/indicators_review.md

# Generate a consolidated report
echo "Generating consolidated report..."
python utils/code_review_tool.py --dir . --output review_reports/full_review.md \
    --ignore-dirs tests venv .git .venv __pycache__ node_modules

echo "Code review complete. Reports saved to review_reports directory."

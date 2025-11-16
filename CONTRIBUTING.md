# Contributing to Customer Decay Analyzer

First off, thank you for considering contributing to Customer Decay Analyzer! It's people like you that make this project better for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to team.churnbusters@example.com.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

---

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates.

**When creating a bug report, include:**
- **Clear title**: Describe the issue in one sentence
- **Steps to reproduce**: Detailed steps to reproduce the behavior
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Screenshots**: If applicable
- **Environment**: OS, Python version, dependency versions
- **Error logs**: Full stack trace

**Example:**
```markdown
**Title**: Gemini API timeout on batch analysis

**Steps to Reproduce:**
1. Run `python scripts/batch_analyze.py`
2. Wait for 5 minutes
3. See timeout error

**Expected**: All customers analyzed
**Actual**: Timeout after 3 customers

**Environment**:
- OS: Ubuntu 22.04
- Python: 3.10.8
- google-generativeai: 0.3.1

**Error Log**:
```
TimeoutError: Gemini API request timed out after 60s
```
```

### 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues.

**When suggesting enhancements, include:**
- **Clear title**: Describe the enhancement
- **Use case**: Why is this enhancement needed?
- **Proposed solution**: How should it work?
- **Alternatives**: Other solutions you've considered
- **Impact**: Who benefits from this enhancement?

### 🔀 Pull Requests

**Good pull requests** (patches, improvements, new features) are fantastic! Please follow these guidelines:

1. **Discuss first**: For major changes, open an issue first
2. **Stay focused**: One feature/fix per pull request
3. **Follow conventions**: Match existing code style
4. **Add tests**: Ensure your code is tested
5. **Update docs**: Keep documentation in sync

---

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- Virtual environment tool (venv/virtualenv)
- API keys (Gemini, Qdrant)

### Setup Steps

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/Customer_decay.git
cd Customer_decay

# 2. Create a new branch for your feature
git checkout -b feature/your-feature-name

# 3. Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists

# 5. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 6. Generate test data
python scripts/generate_sample_data.py

# 7. Run tests to verify setup
python tests/test_pipeline.py
```

### Project Structure

```
customer-decay-backend/
├── models/           # AI/ML models
├── routes/           # Flask API endpoints
├── utils/            # Helper functions
├── scripts/          # Data generation & setup
├── tests/            # Test suite
├── data/             # CSV data files
├── app.py            # Flask application
└── requirements.txt  # Dependencies
```

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

#### General Rules

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Encoding**: UTF-8
- **Imports**: Grouped (stdlib, third-party, local)
- **Docstrings**: Google style

#### Naming Conventions

```python
# Classes: PascalCase
class CustomerAnalyzer:
    pass

# Functions/methods: snake_case
def calculate_risk_score():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3

# Private methods: _leading_underscore
def _internal_helper():
    pass

# Variables: snake_case
customer_data = {}
risk_score = 0.75
```

#### Type Hints

Use type hints for all function signatures:

```python
from typing import Dict, List, Optional

def analyze_customer(
    customer_data: Dict[str, Any],
    behaviors: pd.DataFrame
) -> Dict[str, Any]:
    """
    Analyze customer behavior and predict churn risk.
    
    Args:
        customer_data: Customer profile dictionary
        behaviors: DataFrame with behavior events
    
    Returns:
        Dict containing risk analysis results
    
    Raises:
        ValueError: If customer_data is missing required fields
    """
    pass
```

#### Docstrings

Use Google-style docstrings:

```python
def calculate_combined_risk_score(
    gemini_score: float,
    similar_customers: List[Dict[str, Any]]
) -> float:
    """
    Calculate combined risk score from Gemini and vector similarity.
    
    Combines Gemini AI analysis (60% weight) with vector similarity
    scores (40% weight) to produce final risk assessment. Recent
    churns (< 60 days) are weighted 1.5x higher.
    
    Args:
        gemini_score: Risk score from Gemini analysis (0-100)
        similar_customers: List of similar churned customers with
            similarity scores and churn dates
    
    Returns:
        Combined risk score (0-100) weighted by recency
    
    Example:
        >>> score = calculate_combined_risk_score(
        ...     gemini_score=65.0,
        ...     similar_customers=[
        ...         {"similarity": 0.89, "days_until_churned": 45},
        ...         {"similarity": 0.82, "days_until_churned": 38}
        ...     ]
        ... )
        >>> print(score)
        72.3
    """
    pass
```

#### Error Handling

Always use specific exceptions:

```python
# Bad
try:
    result = risky_operation()
except:
    pass

# Good
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid input: {e}")
    raise
except ConnectionError as e:
    logger.warning(f"API unavailable: {e}")
    return fallback_result()
```

#### Code Comments

```python
# Bad: Obvious comments
x = x + 1  # Increment x

# Good: Explain WHY, not WHAT
# Weight recent churns 1.5x higher to catch rapid decline patterns
if days_since_churn < 60:
    similarity_score *= 1.5
```

---

## Pull Request Process

### Before Submitting

1. **Run tests**: Ensure all tests pass
   ```bash
   python tests/test_pipeline.py
   pytest tests/ -v
   ```

2. **Check code style**: Use flake8 or black
   ```bash
   flake8 . --max-line-length=100
   black . --check
   ```

3. **Update documentation**: Reflect your changes in docs
   - README.md for user-facing changes
   - API_DOCS.md for API changes
   - Inline docstrings for code changes

4. **Update CHANGELOG**: Add entry to CHANGELOG.md (if exists)

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that breaks existing functionality)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review performed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
- [ ] All tests passing

## Screenshots (if applicable)
[Add screenshots here]

## Related Issues
Closes #123
```

### Review Process

1. **Automated checks**: CI/CD pipeline runs tests
2. **Code review**: At least one maintainer reviews
3. **Feedback**: Address review comments
4. **Approval**: Maintainer approves PR
5. **Merge**: Maintainer merges into main

### Commit Message Format

Use conventional commits:

```
type(scope): brief description

Longer description if needed

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, missing semicolons, etc.)
- `refactor`: Code restructuring without behavior change
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(models): add sentiment analysis to customer analyzer

Implemented NLP-based sentiment scoring for support tickets
using pre-trained model. Integrates with existing behavioral
metrics pipeline.

Closes #45

---

fix(api): handle empty behavior data gracefully

Return 404 with clear message when customer has no behavior
events instead of throwing 500 error.

Fixes #67

---

docs(readme): add installation troubleshooting section

Added common setup issues and solutions based on user feedback.
```

---

## Testing Guidelines

### Test Structure

```python
def test_gemini_analyzer_healthy_customer():
    """Test Gemini analyzer with healthy customer data."""
    # Arrange
    customer = create_healthy_customer()
    behaviors = create_healthy_behaviors()
    analyzer = CustomerAnalyzer()
    
    # Act
    result = analyzer.analyze_customer(customer, behaviors)
    
    # Assert
    assert result["churn_risk_score"] < 40
    assert result["risk_level"] == "low"
    assert "churn_risk_score" in result
```

### Test Coverage

Aim for **80%+ code coverage**:

```bash
# Run with coverage
pytest --cov=. tests/

# Generate HTML report
pytest --cov=. --cov-report=html tests/
```

### Types of Tests

1. **Unit Tests**: Test individual functions
   ```python
   def test_normalize_value():
       assert normalize_value(50, 0, 100) == 0.5
   ```

2. **Integration Tests**: Test component interactions
   ```python
   def test_risk_assessor_with_real_data():
       assessor = RiskAssessor()
       result = assessor.assess_customer(customer, behaviors)
       assert "churn_risk_score" in result
   ```

3. **API Tests**: Test Flask endpoints
   ```python
   def test_health_endpoint(client):
       response = client.get("/api/health")
       assert response.status_code == 200
   ```

### Running Tests

```bash
# All tests
python tests/test_pipeline.py

# Specific test
pytest tests/test_pipeline.py::test_gemini_analyzer -v

# With output
pytest tests/ -v -s

# Stop on first failure
pytest tests/ -x
```

---

## Documentation

### Inline Documentation

Every module, class, and function must have docstrings:

```python
"""
Module for customer behavior analysis using Gemini AI.

This module provides the CustomerAnalyzer class which interfaces
with Google's Gemini API to analyze customer behavioral patterns
and predict churn risk.
"""

class CustomerAnalyzer:
    """
    Analyzes customer behavior using Gemini AI.
    
    Attributes:
        api_key (str): Gemini API key
        model_name (str): Gemini model version
        max_retries (int): Maximum API retry attempts
    """
    pass
```

### README Updates

When adding features, update:
- Feature list
- Installation steps (if needed)
- Usage examples
- API documentation

### Changelog

Document all changes in CHANGELOG.md:

```markdown
## [1.1.0] - 2025-01-20

### Added
- Sentiment analysis for support tickets
- Email notification system for critical customers
- Redis caching layer for API responses

### Changed
- Improved Gemini prompt engineering for better accuracy
- Updated vector dimensions from 10 to 768

### Fixed
- Timeout handling in batch analysis
- Edge case in normalize_value function

### Deprecated
- Old CustomerAnalyzer v1 API (use v2)
```

---

## Questions?

If you have questions or need help:

1. **Check documentation**: README.md, API_DOCS.md
2. **Search issues**: Someone may have asked already
3. **Ask in discussions**: GitHub Discussions
4. **Contact team**: team.churnbusters@example.com

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Invited to team meetings (if significant contributions)

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing! 🎉**

Every contribution, no matter how small, makes this project better for everyone.

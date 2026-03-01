# 🤝 Contributing to FakePhoto.ai

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/fakephoto-ai.git
   cd fakephoto-ai
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install development dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## 🌿 Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Urgent production fixes

## 📝 Making Changes

1. **Create a new branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Run tests** to ensure nothing breaks:
   ```bash
   pytest
   ```

4. **Format your code**:
   ```bash
   black src/
   isort src/
   ```

5. **Check types**:
   ```bash
   mypy src/
   ```

6. **Commit your changes** with a clear message:
   ```bash
   git commit -m "feat: add video frame extraction"
   ```

## 🎯 Coding Standards

- **Python 3.11+** syntax
- **Type hints** for all functions
- **Docstrings** for all public APIs
- **Black** formatting (88 char line length)
- **Maximum cyclomatic complexity**: 10

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

## 🧪 Testing

- Write tests for new functionality
- Maintain >80% code coverage
- Run tests before committing:
  ```bash
  pytest --cov=fakephoto --cov-report=html
  ```

## 📋 Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure CI passes** (tests, linting, type checking)
4. **Request review** from maintainers
5. **Address review comments**
6. **Merge** once approved

## 🐛 Reporting Bugs

Use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md) and include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details

## 💡 Suggesting Features

Use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md) and describe:
- Problem you're solving
- Proposed solution
- Alternative approaches
- Use cases

## 📞 Questions?

- Open a [Discussion](https://github.com/josecookai/fakephoto-ai/discussions)
- Join our community

## 🙏 Recognition

Contributors will be recognized in our README!

Thank you for making FakePhoto.ai better! 🎉
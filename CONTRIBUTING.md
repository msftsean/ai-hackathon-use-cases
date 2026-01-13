# Contributing to NY State AI Hackathon - AI Accelerators

Thank you for your interest in contributing to the NY State AI Hackathon accelerators! This document provides guidelines for contributing to this project.

## 📋 Table of Contents

- [Getting Access](#getting-access)
- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Testing Requirements](#testing-requirements)

---

## 🔐 Getting Access

### For Microsoft Enterprise Account Users

If you have a Microsoft enterprise account (e.g., @microsoft.com email), you can access this repository by:

1. **Ensure your GitHub account is linked to your Microsoft identity**:
   - Go to [GitHub Settings > Emails](https://github.com/settings/emails)
   - Add your Microsoft enterprise email if not already added
   - Verify the email address

2. **Request Collaborator Access**:
   - Contact the repository owner (@msftsean) via:
     - GitHub: Open an issue with the "access request" label
     - Teams: Send a direct message
     - Email: Provide your GitHub username and Microsoft email
   
3. **Join the Organization** (if applicable):
   - If this repository is part of a GitHub organization, request to be added as a member
   - Organization members automatically get access to internal repositories

4. **Two-Factor Authentication (2FA)**:
   - Ensure 2FA is enabled on your GitHub account
   - Microsoft enterprise policies may require this for access

### For External Contributors

External contributors can:
- Fork the repository
- Submit pull requests from their fork
- Participate in discussions and issue tracking

---

## 📜 Code of Conduct

This project adheres to professional standards expected in government technology projects:

- **Be respectful** and inclusive in all communications
- **Follow security best practices** - never commit secrets or sensitive data
- **Maintain confidentiality** - do not share information outside approved channels
- **Focus on constructive feedback** in code reviews and discussions

---

## 🤝 How to Contribute

### Ways to Contribute

1. **Report Bugs**: Open an issue with detailed reproduction steps
2. **Suggest Features**: Open an issue describing the feature and use case
3. **Improve Documentation**: Submit PRs for documentation updates
4. **Fix Issues**: Pick up issues labeled "good first issue" or "help wanted"
5. **Add Tests**: Improve test coverage
6. **Security Fixes**: Report security vulnerabilities privately (see SECURITY.md)

### Before You Start

1. Check existing issues and pull requests to avoid duplication
2. For major changes, open an issue first to discuss the approach
3. Review the [Architecture Documentation](./README.md) to understand the project structure

---

## 🛠️ Development Setup

### Python Accelerators (1-5)

```bash
# Clone the repository
git clone https://github.com/msftsean/ai-hackathon-use-cases.git
cd ai-hackathon-use-cases

# Navigate to an accelerator
cd Constituent-Services-Agent  # or any other Python accelerator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run the accelerator
python demo.py
```

### .NET Accelerator (6)

```bash
# Navigate to .NET accelerator
cd DotNet-Virtual-Citizen-Assistant

# Restore dependencies
dotnet restore

# Build
dotnet build

# Run tests
dotnet test

# Run the application
dotnet run --project VirtualCitizenAgent
```

---

## 📝 Coding Standards

### Python Code (Accelerators 1-5)

- Follow **PEP 8** style guidelines
- Use **type hints** for all function parameters and return types
- Include **docstrings** for all public functions and classes
- Use **async/await** for I/O operations
- Keep functions focused and small (< 50 lines preferred)

Example:
```python
from typing import List, Optional
from pydantic import BaseModel

async def process_document(
    document_id: str,
    validate: bool = True
) -> Optional[ProcessingResult]:
    """
    Process a document and extract information.
    
    Args:
        document_id: Unique identifier for the document
        validate: Whether to validate extracted data
        
    Returns:
        ProcessingResult if successful, None if processing fails
    """
    # Implementation
    pass
```

### .NET Code (Accelerator 6)

- Follow **.NET coding conventions**
- Use **nullable reference types**
- Include **XML documentation comments** for public APIs
- Use **dependency injection** for services
- Keep methods focused (< 50 lines preferred)

Example:
```csharp
/// <summary>
/// Searches documents using semantic search.
/// </summary>
/// <param name="query">The search query.</param>
/// <param name="maxResults">Maximum number of results to return.</param>
/// <param name="cancellationToken">Cancellation token.</param>
/// <returns>List of search results.</returns>
public async Task<List<SearchResult>> SearchAsync(
    string query,
    int maxResults = 10,
    CancellationToken cancellationToken = default)
{
    // Implementation
}
```

### General Guidelines

- **Security First**: Never commit API keys, credentials, or sensitive data
- **Responsible AI**: Include citations, confidence scores, and human-in-the-loop workflows
- **Accessibility**: Follow WCAG 2.1 AA guidelines for UI components
- **Testing**: Write unit tests for all new functionality
- **Documentation**: Update relevant documentation with your changes

---

## 🔄 Pull Request Process

1. **Create a Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # OR
   git checkout -b fix/issue-number-description
   ```

2. **Make Your Changes**:
   - Follow coding standards
   - Add/update tests
   - Update documentation
   - Run linters and tests locally

3. **Commit Your Changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```
   
   Use conventional commit format:
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation changes
   - `test:` - Test additions/changes
   - `refactor:` - Code refactoring
   - `style:` - Code style changes
   - `chore:` - Build/tooling changes

4. **Push to GitHub**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**:
   - Use a clear, descriptive title
   - Reference any related issues (e.g., "Fixes #123")
   - Provide a detailed description of changes
   - Include screenshots for UI changes
   - List any breaking changes

6. **Code Review**:
   - Address reviewer feedback promptly
   - Keep discussions professional and constructive
   - Update your PR based on feedback

7. **Merge**:
   - Once approved, your PR will be merged by a maintainer
   - Delete your feature branch after merge

---

## 🧪 Testing Requirements

### Python Projects

All new features must include:
- **Unit tests** for individual functions/classes
- **Integration tests** for API endpoints (if applicable)
- **Mock services** for external dependencies

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agent.py -v
```

### .NET Project

All new features must include:
- **Unit tests** using xUnit
- **Integration tests** for API endpoints
- **Mock services** using Moq

```bash
# Run all tests
dotnet test

# Run with coverage
dotnet test /p:CollectCoverage=true

# Run specific test class
dotnet test --filter FullyQualifiedName~SearchServiceTests
```

### Test Coverage Requirements

- Minimum **80% code coverage** for new code
- All public APIs must have tests
- Edge cases and error conditions must be tested

---

## 🔒 Security Considerations

### Required Security Practices

1. **Never commit secrets**:
   - Use `.env` files (add to `.gitignore`)
   - Use Azure Key Vault for production
   - Use environment variables for configuration

2. **Input Validation**:
   - Validate all user inputs
   - Sanitize data before processing
   - Use Pydantic models (Python) or validation attributes (.NET)

3. **Authentication & Authorization**:
   - Use Azure Entra ID for authentication
   - Implement role-based access control (RBAC)
   - Never hardcode credentials

4. **PII Handling**:
   - Detect and mask PII in logs
   - Follow data retention policies (30 days for conversations)
   - Implement proper data encryption

### Reporting Security Vulnerabilities

**Do not open public issues for security vulnerabilities.**

Instead:
1. Email the maintainers privately
2. Or use GitHub's private security advisory feature
3. Provide detailed information about the vulnerability
4. Allow time for a fix before public disclosure

---

## 📚 Additional Resources

- [README.md](./README.md) - Project overview and documentation
- [QUICKSTART.md](./docs/QUICKSTART.md) - Quick start guide
- [COLLABORATION.md](./COLLABORATION.md) - Detailed collaboration guide
- [Architecture Documentation](./README.md#technical-architecture) - System architecture
- [Azure AI Foundry Docs](https://learn.microsoft.com/azure/ai-foundry/)
- [Semantic Kernel Docs](https://learn.microsoft.com/semantic-kernel/)
- [NY State ITS AI Policy](https://its.ny.gov/ai)

---

## 📞 Getting Help

- **Questions**: Open a discussion in GitHub Discussions
- **Bug Reports**: Open an issue with the "bug" label
- **Feature Requests**: Open an issue with the "enhancement" label
- **Security Issues**: Contact maintainers privately

---

## 🏛️ Government Compliance

This project follows:
- **NY LOADinG Act**: Transparent, auditable AI decisions
- **NY RAISE Act**: Accountability for automated decisions
- **WCAG 2.1 AA**: Accessibility standards
- **Azure GCC**: Government Community Cloud compatibility

All contributions must maintain compliance with these requirements.

---

**Thank you for contributing to better government services through AI!** 🏛️ 🗽

# Collaboration Guide - NY State AI Hackathon Repository

This guide provides detailed instructions for team members, especially those with Microsoft enterprise accounts, to access and collaborate on this repository.

## 📋 Table of Contents

- [For Microsoft Enterprise Users](#for-microsoft-enterprise-users)
- [Repository Access Levels](#repository-access-levels)
- [Setting Up Your Environment](#setting-up-your-environment)
- [Collaboration Workflow](#collaboration-workflow)
- [Troubleshooting Access Issues](#troubleshooting-access-issues)
- [Team Communication](#team-communication)

---

## 🏢 For Microsoft Enterprise Users

### Overview

If you have a Microsoft enterprise account (e.g., @microsoft.com, @msft.com, or other Microsoft-federated email), you should be able to access this repository without any special configuration. However, there are a few requirements and best practices to ensure smooth collaboration.

### Prerequisites

1. **GitHub Account Linked to Microsoft Identity**
   - Your GitHub account should be linked to your Microsoft enterprise email
   - This enables seamless authentication and access to Microsoft-related repositories

2. **Two-Factor Authentication (2FA)**
   - 2FA is **required** for accessing repositories with Microsoft enterprise policies
   - Enable 2FA in your [GitHub Security Settings](https://github.com/settings/security)

3. **SSO Authentication** (if applicable)
   - Some Microsoft organizations require SAML Single Sign-On (SSO)
   - You may need to authorize your SSH keys or personal access tokens with SSO

### Step-by-Step Access Setup

#### Step 1: Verify Your GitHub Account

1. Go to [GitHub Settings > Emails](https://github.com/settings/emails)
2. Ensure your Microsoft enterprise email is added and verified
3. You can set it as your primary email or keep it as a secondary email

#### Step 2: Enable Two-Factor Authentication

1. Go to [GitHub Settings > Security](https://github.com/settings/security)
2. Click "Enable two-factor authentication"
3. Choose your preferred 2FA method:
   - **Authenticator App** (recommended): Microsoft Authenticator, Google Authenticator
   - **SMS**: Receive codes via text message
   - **Security Keys**: Hardware security keys (FIDO2)

#### Step 3: Request Repository Access

**Option A: Direct Collaborator Access**

1. Contact the repository owner (@msftsean) with:
   - Your GitHub username
   - Your Microsoft enterprise email
   - Your role/team affiliation
   - Reason for access (e.g., "Working on Accelerator 3 - Emergency Response")

2. Provide your access via:
   - GitHub Issue: Open an issue with the label "access-request"
   - Microsoft Teams: Direct message
   - Email: Contact the team lead

**Option B: Organization Membership**

If this repository is part of a GitHub organization:

1. Request to be added to the organization
2. Once added, you'll automatically have access to:
   - Organization repositories
   - Team discussions
   - Project boards

#### Step 4: Authorize SSO (If Required)

If the repository requires SAML SSO:

1. When cloning or accessing the repository, you'll see an SSO authorization prompt
2. Click "Authorize" to link your GitHub account with your Microsoft identity
3. Complete the Microsoft login flow
4. You may need to authorize your SSH keys:
   ```bash
   # For SSH keys, enable SSO on each key
   # Go to: Settings > SSH and GPG keys
   # Click "Enable SSO" next to each key
   ```

#### Step 5: Configure Git Authentication

**For HTTPS (Recommended)**

```bash
# Use GitHub Personal Access Token (PAT)
# Create a PAT: Settings > Developer settings > Personal access tokens > Tokens (classic)

# Clone with HTTPS
git clone https://github.com/msftsean/ai-hackathon-use-cases.git

# Or configure credential helper
git config --global credential.helper store
```

**For SSH**

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your.email@microsoft.com"

# Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Add public key to GitHub: Settings > SSH and GPG keys > New SSH key
cat ~/.ssh/id_ed25519.pub

# Clone with SSH
git clone git@github.com:msftsean/ai-hackathon-use-cases.git
```

---

## 🔐 Repository Access Levels

### Access Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Read** | View code, issues, pull requests | External reviewers, auditors |
| **Triage** | Manage issues and pull requests | Project coordinators |
| **Write** | Push to branches, create PRs | Active developers |
| **Maintain** | Manage repository settings | Team leads |
| **Admin** | Full control | Repository owners |

### Requesting Different Access Levels

1. **Read Access**: Default for public repositories
2. **Write Access**: Required for pushing branches
   - Request from repository owner
   - Provide justification (e.g., "Working on Document Eligibility Agent")
3. **Admin Access**: Reserved for repository maintainers

---

## 🛠️ Setting Up Your Environment

### Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/msftsean/ai-hackathon-use-cases.git
cd ai-hackathon-use-cases

# 2. Configure your Git identity
git config user.name "Your Name"
git config user.email "your.email@microsoft.com"

# 3. Set up your development environment
# For Python accelerators (1-5)
cd Constituent-Services-Agent
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR venv\Scripts\activate  # Windows
pip install -r requirements.txt

# For .NET accelerator (6)
cd DotNet-Virtual-Citizen-Assistant
dotnet restore
```

### Configuring Azure Services (Optional)

```bash
# Create .env file in accelerator directory
cat > .env << EOF
USE_MOCK_SERVICES=false
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
EOF

# Ensure .env is in .gitignore (it should be already)
```

---

## 🤝 Collaboration Workflow

### Working on Features

```bash
# 1. Create a feature branch
git checkout -b feature/your-feature-name

# 2. Make your changes
# ... edit files ...

# 3. Run tests
pytest tests/ -v  # Python
# OR
dotnet test  # .NET

# 4. Commit your changes
git add .
git commit -m "feat: add new feature"

# 5. Push to GitHub
git push origin feature/your-feature-name

# 6. Open a Pull Request on GitHub
# Go to: https://github.com/msftsean/ai-hackathon-use-cases/pulls
# Click "New pull request"
```

### Code Review Process

1. **Submit PR**: Open pull request with clear description
2. **Automated Checks**: CI/CD runs tests automatically
3. **Peer Review**: Team members review your code
4. **Address Feedback**: Make requested changes
5. **Approval**: Get approval from required reviewers
6. **Merge**: Maintainer merges your PR

### Branch Protection Rules

This repository may have branch protection rules:
- **main** branch: Requires pull request reviews before merging
- **CI checks**: All tests must pass before merge
- **Code owners**: Specific files require approval from code owners

---

## 🔧 Troubleshooting Access Issues

### Common Issues and Solutions

#### Issue 1: "Repository not found" or "Permission denied"

**Possible Causes:**
- You don't have access to the repository
- Your SSH key or PAT is not configured correctly
- SSO authorization is required but not completed

**Solutions:**
1. Verify you have been granted access by the repository owner
2. Check if 2FA is enabled on your GitHub account
3. For SSH: Ensure your SSH key is added to GitHub and SSO-enabled
4. For HTTPS: Use a Personal Access Token instead of password
5. Try accessing via GitHub web interface first to trigger SSO flow

#### Issue 2: "fatal: unable to access" when using HTTPS

**Solution:**
```bash
# Use Personal Access Token (PAT)
# Create PAT: Settings > Developer settings > Personal access tokens
# Use PAT as password when prompted

# Or configure credential helper
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=3600'
```

#### Issue 3: SSH Key Not Working After SSO

**Solution:**
1. Go to [GitHub Settings > SSH and GPG keys](https://github.com/settings/keys)
2. Find your SSH key
3. Click "Configure SSO" or "Enable SSO"
4. Authorize the key for the organization

#### Issue 4: "You need to authorize your personal access token"

**Solution:**
1. Go to [Personal Access Tokens](https://github.com/settings/tokens)
2. Click on your token
3. Click "Configure SSO"
4. Authorize for the required organization

#### Issue 5: Cannot Push to Branch

**Possible Causes:**
- You only have Read access (need Write access)
- Branch protection rules prevent direct pushes
- You're trying to push to main/master directly

**Solutions:**
1. Request Write access from repository owner
2. Create a feature branch instead: `git checkout -b feature/my-feature`
3. Use pull requests to merge changes

### Getting Additional Help

If you continue to experience access issues:

1. **Check Repository Settings**: Ensure the repository visibility matches your expectations (public vs. private)
2. **Contact Repository Owner**: Reach out to @msftsean with:
   - Your GitHub username
   - Description of the issue
   - Screenshots of error messages
   - Steps you've already tried
3. **Microsoft IT Support**: For enterprise account issues, contact your Microsoft IT support
4. **GitHub Support**: For GitHub-specific issues, contact [GitHub Support](https://support.github.com)

---

## 💬 Team Communication

### Communication Channels

1. **GitHub Issues**: For bug reports, feature requests, and task tracking
2. **GitHub Discussions**: For questions, ideas, and general discussion
3. **Pull Request Comments**: For code-specific discussions
4. **Microsoft Teams**: For real-time team communication (if applicable)
5. **Email**: For sensitive or private matters

### Best Practices

- **Use GitHub for code-related discussions**: Keep context with the code
- **Tag relevant team members**: Use @mentions to notify specific people
- **Be specific**: Provide detailed information and context
- **Be responsive**: Reply to comments and feedback in a timely manner
- **Be professional**: Maintain a respectful and constructive tone

---

## 📚 Additional Resources

### Documentation

- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines
- [README.md](./README.md) - Project overview
- [QUICKSTART.md](./docs/QUICKSTART.md) - Quick start guide

### GitHub Documentation

- [About authentication with SAML SSO](https://docs.github.com/en/authentication/authenticating-with-saml-single-sign-on/about-authentication-with-saml-single-sign-on)
- [Authorizing a personal access token for use with SAML SSO](https://docs.github.com/en/authentication/authenticating-with-saml-single-sign-on/authorizing-a-personal-access-token-for-use-with-saml-single-sign-on)
- [Managing access to your organization's repositories](https://docs.github.com/en/organizations/managing-access-to-your-organizations-repositories)

### Microsoft Resources

- [Microsoft GitHub Documentation](https://docs.opensource.microsoft.com/github/)
- [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)

---

## 📞 Contact Information

- **Repository Owner**: @msftsean
- **Project**: NY State AI Hackathon - AI Accelerators for Government Services
- **Repository**: [github.com/msftsean/ai-hackathon-use-cases](https://github.com/msftsean/ai-hackathon-use-cases)

---

**Welcome to the team! We're excited to build responsible AI solutions for NY State government together.** 🏛️ 🗽

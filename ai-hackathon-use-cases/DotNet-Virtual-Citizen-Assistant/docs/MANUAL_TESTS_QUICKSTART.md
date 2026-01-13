# Manual Integration Tests - Quick Setup Guide

This guide provides a fast setup path for running the 3 manual integration tests that require Azure OpenAI credentials.

## 🎯 Quick Overview

**Manual Tests**: 3 integration tests requiring real Azure OpenAI service  
**Purpose**: Validate real AI functionality, query enhancement, and plugin integration  
**Time**: ~5 minutes setup, ~30 seconds execution  

## 🚀 Fast Setup (5 Steps)

### Step 1: Azure OpenAI Service
- Create Azure OpenAI resource in Azure portal
- Deploy GPT-4 or GPT-3.5-turbo model
- Copy: Endpoint, Deployment Name, API Key

### Step 2: Create .env File
Create `.env` in project root:
```bash
OPENAI__ENDPOINT=https://your-resource.openai.azure.com/
OPENAI__DEPLOYMENTNAME=gpt-4
OPENAI__APIKEY=your-api-key-here
```

### Step 3: Enable Tests
Edit `VirtualCitizenAgent.Tests/Integration/RealOpenAIIntegrationTests.cs`:

**Find and replace (3 times):**
```csharp
[Fact(Skip = "Requires real OpenAI credentials - enable manually for integration testing")]
```
**With:**
```csharp
[Fact]
```

### Step 4: Run Tests
```bash
cd VirtualCitizenAgent.Tests
dotnet test --verbosity normal
```

### Step 5: Verify Results
Look for:
- ✅ `OpenAI_WithRealCredentials_ShouldGenerateResponse` - Basic connectivity
- ✅ `OpenAI_QueryEnhancement_ShouldImproveSearchTerms` - Query enhancement  
- ✅ `OpenAI_WithKernelFunctions_ShouldInvokePluginFunctions` - Plugin functions

## 📋 Alternative Configuration Methods

### Option A: User Secrets (Secure)
```bash
cd VirtualCitizenAgent.Tests
dotnet user-secrets set "OpenAI:Endpoint" "https://your-resource.openai.azure.com/"
dotnet user-secrets set "OpenAI:DeploymentName" "gpt-4"
dotnet user-secrets set "OpenAI:ApiKey" "your-api-key-here"
```

### Option B: Environment Variables (CI/CD)
```bash
export OPENAI__ENDPOINT="https://your-resource.openai.azure.com/"
export OPENAI__DEPLOYMENTNAME="gpt-4"
export OPENAI__APIKEY="your-api-key-here"
```

## 🔍 Test Details

### Test 1: Basic Connectivity
**Method**: `OpenAI_WithRealCredentials_ShouldGenerateResponse`  
**Purpose**: Validates Azure OpenAI service connection and response generation  
**Expected**: AI response to "Hello, I need help with NYC services"

### Test 2: Query Enhancement
**Method**: `OpenAI_QueryEnhancement_ShouldImproveSearchTerms`  
**Purpose**: Tests AI-powered search term optimization  
**Expected**: Enhanced terms like "sanitation", "waste", "collection" for garbage query

### Test 3: Plugin Integration  
**Method**: `OpenAI_WithKernelFunctions_ShouldInvokePluginFunctions`  
**Purpose**: Validates Semantic Kernel plugin function execution  
**Expected**: Successful plugin function invocation with valid response

## 🐛 Troubleshooting

### "OpenAI configuration not available"
**Solution**: Check .env file path and environment variable names (use double underscores: `OPENAI__ENDPOINT`)

### "Skip Exception" during test
**Solution**: Verify Azure OpenAI credentials are correctly configured and accessible

### Network timeout
**Solution**: Check Azure OpenAI service availability and network connectivity

### Build errors
**Solution**: Run `dotnet build VirtualCitizenAgent.Tests` first to identify compilation issues

## ✅ Success Indicators

### Console Output
```
📁 Loaded .env file from: /path/to/.env
🔌 Testing real Azure OpenAI connection...
🔧 Configuring Azure OpenAI: Endpoint=https://..., Deployment=gpt-4
✅ Azure OpenAI Response: [AI response text]
```

### Test Results
```
Test Run Successful.
Total tests: 101
     Passed: 101  ← All tests including manual ones
     Failed: 0
    Skipped: 0    ← No skipped tests when manual tests enabled
```

## 🔄 Disable Manual Tests

To disable manual tests after validation:
```csharp
[Fact(Skip = "Requires real OpenAI credentials - enable manually for integration testing")]
```

## 📞 Need Help?

1. **Review**: Full documentation in `docs/TESTING.md`
2. **Debug**: Run with `--verbosity diagnostic` for detailed output
3. **Issues**: Check GitHub issues for common problems
4. **Support**: Create issue with environment details and error messages

---

**Total Setup Time**: ~5 minutes  
**Test Execution Time**: ~30 seconds  
**Confidence Level**: Production-ready AI integration validation
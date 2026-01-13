# Virtual Citizen Assistant - Setup and Fix Guide

This guide explains how to set up and run the Virtual Citizen Assistant after fixing the pydantic compatibility issues.

## 🔧 Fixes Applied

The main issue was that the original `semantic-kernel==0.9.1b1` was incompatible with pydantic v2. The error `cannot import name 'url' from 'pydantic.networks'` occurred because:

1. The old semantic-kernel version expected pydantic v1 API
2. Pydantic v2 moved and renamed the `url` function
3. The plugin decorators used the old API syntax

### Key Changes Made:

1. **Updated semantic-kernel**: `0.9.1b1` → `1.37.0`
2. **Updated dependencies** to compatible versions
3. **Fixed plugin decorators**: Updated from `@sk_function` to `@kernel_function`
4. **Fixed import syntax**: Updated to use new semantic-kernel imports
5. **Added pydantic v2 compatibility**: All imports now work with pydantic 2.x

## 📦 Installation

1. **Navigate to the project directory:**
   ```bash
   cd /workspaces/ai-hackathon-use-cases/Virtual-Citizen-Assistant
   ```

2. **Install the updated requirements:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the compatibility test:**
   ```bash
   python test_setup.py
   ```

   You should see:
   ```
   🎉 ALL TESTS PASSED! The Virtual Citizen Assistant is ready to use.
   ```

## 🔍 What Was Fixed

### 1. Requirements.txt Updates
```txt
# OLD (broken)
semantic-kernel==0.9.1b1
openai==1.3.7

# NEW (working)
semantic-kernel==1.37.0
openai>=1.98.0
```

### 2. Plugin Decorator Changes
```python
# OLD (broken with new SK)
from semantic_kernel.plugin_definition import sk_function, sk_function_context_parameter

@sk_function(description="...", name="...")
@sk_function_context_parameter(name="query", description="...")
def search_city_services(self, query: str) -> str:

# NEW (working)
from semantic_kernel.functions import kernel_function
from typing import Annotated

@kernel_function(description="...", name="...")
def search_city_services(
    self, 
    query: Annotated[str, "The search query about city services"]
) -> str:
```

### 3. Kernel Initialization Updates
```python
# OLD API
import semantic_kernel as sk
kernel = sk.Kernel()

# NEW API
from semantic_kernel import Kernel
kernel = Kernel()
```

## 🚀 Usage

### Environment Variables
Create a `.env` file with:
```env
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_SEARCH_ENDPOINT=your_search_endpoint
AZURE_SEARCH_KEY=your_search_key
AZURE_SEARCH_INDEX=your_search_index
```

### Running the Assistant
```bash
python src/main.py
```

### Testing the Plugin
```bash
python -c "from src.plugins.document_retrieval_plugin import DocumentRetrievalPlugin; print('Plugin works!')"
```

## 📁 File Structure
```
Virtual-Citizen-Assistant/
├── requirements.txt              # ✅ Updated with compatible versions
├── test_setup.py                # ✅ New compatibility test
├── src/
│   ├── main.py                  # ✅ Updated main application
│   ├── plugins/
│   │   └── document_retrieval_plugin.py  # ✅ Fixed plugin with new API
│   ├── config/
│   │   └── settings.py
│   └── models/
│       └── citizen_query.py
└── assets/
    └── ...
```

## 🐛 Troubleshooting

### Common Issues:

1. **"cannot import name 'url' from 'pydantic.networks'"**
   - ✅ **Fixed**: Updated to semantic-kernel 1.37.0

2. **"No module named 'semantic_kernel.plugin_definition'"**
   - ✅ **Fixed**: Updated imports to use `semantic_kernel.functions`

3. **OpenAI version conflicts**
   - ✅ **Fixed**: Updated to compatible versions

### Verification Commands:
```bash
# Check semantic-kernel version
python -c "import semantic_kernel; print('SK version:', semantic_kernel.__version__)"

# Check pydantic compatibility
python -c "from pydantic import networks; print('Pydantic networks OK')"

# Test plugin import
python -c "from src.plugins.document_retrieval_plugin import DocumentRetrievalPlugin; print('Plugin OK')"
```

## 📋 Version Compatibility Matrix

| Component | Old Version | New Version | Status |
|-----------|-------------|-------------|---------|
| semantic-kernel | 0.9.1b1 | 1.37.0 | ✅ Fixed |
| pydantic | 2.11.9 | 2.11.9 | ✅ Compatible |
| openai | 1.3.7 | 2.0.1+ | ✅ Updated |
| azure-search-documents | 11.4.0 | 11.5.3 | ✅ Updated |

## 🎉 Success Indicators

When everything is working correctly, you should see:
- ✅ No import errors
- ✅ Plugin loads successfully  
- ✅ Kernel functions are recognized
- ✅ All compatibility tests pass

The Virtual Citizen Assistant is now ready for hackathon use!
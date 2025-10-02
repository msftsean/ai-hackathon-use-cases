"""
Setup and Configuration Tests
Tests for application setup, dependencies, and configuration.
"""
import pytest
import sys
import os
from pathlib import Path
import importlib


class TestSetupAndConfiguration:
    """Test application setup and configuration."""
    
    def test_python_version(self):
        """Test Python version compatibility."""
        assert sys.version_info >= (3, 8), "Python 3.8+ required"
    
    def test_project_structure(self):
        """Test project directory structure exists."""
        project_root = Path(__file__).parent.parent
        
        # Test main directories exist
        assert (project_root / "src").exists()
        assert (project_root / "src" / "models").exists()
        assert (project_root / "src" / "services").exists()
        assert (project_root / "src" / "orchestration").exists()
        assert (project_root / "tests").exists()
        
        # Test key files exist
        assert (project_root / "requirements.txt").exists()
        assert (project_root / "README.md").exists()
    
    def test_package_imports(self):
        """Test that all main packages can be imported."""
        # Test model imports
        from src.models.emergency_models import (
            EmergencyScenario, EmergencyResponsePlan, EmergencyType, SeverityLevel
        )
        
        # Test service imports
        from src.services.weather_service import WeatherService
        
        # Test orchestration imports
        from src.orchestration.emergency_coordinator import EmergencyResponseCoordinator
        
        # Verify classes can be instantiated
        assert EmergencyType.HURRICANE is not None
        assert SeverityLevel.HIGH is not None
        assert WeatherService() is not None
        assert EmergencyResponseCoordinator() is not None
    
    def test_enum_completeness(self):
        """Test that enums have expected values."""
        from src.models.emergency_models import EmergencyType, SeverityLevel, CoordinationStatus
        
        # Test EmergencyType has all expected values
        expected_emergency_types = [
            "hurricane", "winter_storm", "flood", "fire", "public_health",
            "infrastructure_failure", "security_incident", "earthquake"
        ]
        
        for emergency_type in expected_emergency_types:
            assert any(et.value == emergency_type for et in EmergencyType)
        
        # Test SeverityLevel has sequential values
        assert SeverityLevel.LOW.value == 1
        assert SeverityLevel.MODERATE.value == 2
        assert SeverityLevel.HIGH.value == 3
        assert SeverityLevel.SEVERE.value == 4
        assert SeverityLevel.CATASTROPHIC.value == 5
        
        # Test CoordinationStatus values
        expected_statuses = ["pending", "in_progress", "completed", "failed"]
        for status in expected_statuses:
            assert any(cs.value == status for cs in CoordinationStatus)
    
    def test_requirements_file_format(self):
        """Test requirements.txt file format and key dependencies."""
        requirements_path = Path(__file__).parent.parent / "requirements.txt"
        
        with open(requirements_path, 'r') as f:
            requirements = f.read()
        
        # Test key dependencies are present
        key_dependencies = [
            "semantic-kernel",
            "azure-search-documents",
            "azure-identity",
            "openai",
            "pytest",
            "aiohttp",
            "pydantic"
        ]
        
        for dependency in key_dependencies:
            assert dependency in requirements, f"Missing dependency: {dependency}"
        
        # Test that we're using modern semantic-kernel (not broken 0.9.1b1)
        assert "semantic-kernel==1.37.0" in requirements
        
        # Test pytest dependencies for testing
        assert "pytest-asyncio" in requirements
        assert "pytest-mock" in requirements
    
    def test_model_validation_setup(self):
        """Test that Pydantic model validation is working."""
        from src.models.emergency_models import EmergencyScenario, EmergencyType, SeverityLevel
        from pydantic import ValidationError
        
        # Valid scenario should work
        valid_scenario = EmergencyScenario(
            scenario_id="test",
            incident_type=EmergencyType.FIRE,
            severity_level=SeverityLevel.MODERATE,
            location="Test Location",
            affected_area_radius=5.0,
            estimated_population_affected=1000
        )
        assert valid_scenario.affected_area_radius == 5.0
        
        # Invalid scenarios should raise ValidationError
        with pytest.raises(ValidationError):
            EmergencyScenario(
                scenario_id="test",
                incident_type=EmergencyType.FIRE,
                severity_level=SeverityLevel.MODERATE,
                location="Test Location",
                affected_area_radius=-1.0,  # Invalid negative radius
                estimated_population_affected=1000
            )
    
    def test_async_support_setup(self):
        """Test that async functionality is properly set up."""
        import asyncio
        from src.services.weather_service import WeatherService
        
        # Test that async context manager works
        async def test_async():
            async with WeatherService() as service:
                # Should not raise an exception
                assert service is not None
                return True
        
        # Run the async test
        result = asyncio.run(test_async())
        assert result is True
    
    def test_logging_setup(self):
        """Test that logging is properly configured."""
        import logging
        from src.orchestration.emergency_coordinator import EmergencyResponseCoordinator
        
        coordinator = EmergencyResponseCoordinator()
        assert coordinator.logger is not None
        assert isinstance(coordinator.logger, logging.Logger)
    
    def test_semantic_kernel_setup(self):
        """Test that Semantic Kernel is properly initialized."""
        from src.orchestration.emergency_coordinator import EmergencyResponseCoordinator
        from semantic_kernel import Kernel
        
        coordinator = EmergencyResponseCoordinator()
        assert coordinator.kernel is not None
        assert isinstance(coordinator.kernel, Kernel)
    
    def test_data_models_inheritance(self):
        """Test that data models have proper inheritance."""
        from src.models.emergency_models import EmergencyScenario, EmergencyResponsePlan
        from pydantic import BaseModel
        
        # EmergencyScenario should inherit from BaseModel for validation
        assert issubclass(EmergencyScenario, BaseModel)
        assert issubclass(EmergencyResponsePlan, BaseModel)
    
    def test_file_permissions_and_structure(self):
        """Test file permissions and module structure."""
        src_path = Path(__file__).parent.parent / "src"
        
        # Test __init__.py files exist for proper module structure
        assert (src_path / "__init__.py").exists()
        assert (src_path / "models" / "__init__.py").exists()
        assert (src_path / "services" / "__init__.py").exists()
        assert (src_path / "orchestration" / "__init__.py").exists()
        
        # Test main module files exist
        assert (src_path / "main.py").exists()
        assert (src_path / "models" / "emergency_models.py").exists()
        assert (src_path / "services" / "weather_service.py").exists()
        assert (src_path / "orchestration" / "emergency_coordinator.py").exists()


class TestDependencyCompatibility:
    """Test dependency compatibility and versions."""
    
    def test_semantic_kernel_version(self):
        """Test Semantic Kernel version and compatibility."""
        try:
            import semantic_kernel as sk
            from semantic_kernel.functions import kernel_function
            
            # Test that we can create a kernel
            kernel = sk.Kernel()
            assert kernel is not None
            
            # Test that modern kernel_function decorator exists
            assert kernel_function is not None
            
        except ImportError as e:
            pytest.fail(f"Semantic Kernel import failed: {e}")
    
    def test_pydantic_version(self):
        """Test Pydantic v2 compatibility."""
        try:
            from pydantic import BaseModel, field_validator
            import pydantic
            
            # Test that we're using Pydantic v2
            version = pydantic.__version__
            major_version = int(version.split('.')[0])
            assert major_version >= 2, f"Pydantic v2+ required, got {version}"
            
            # Test basic model functionality
            class TestModel(BaseModel):
                test_field: str
                
                @field_validator('test_field')
                @classmethod
                def validate_test_field(cls, v):
                    return v
            
            model = TestModel(test_field="test")
            assert model.test_field == "test"
            
        except ImportError as e:
            pytest.fail(f"Pydantic import failed: {e}")
    
    def test_azure_dependencies(self):
        """Test Azure SDK dependencies."""
        try:
            import azure.identity
            import azure.search.documents
            
            # Test basic Azure Identity functionality
            from azure.identity import DefaultAzureCredential
            # Should not raise an exception
            credential = DefaultAzureCredential()
            assert credential is not None
            
        except ImportError as e:
            pytest.fail(f"Azure SDK import failed: {e}")
    
    def test_async_dependencies(self):
        """Test async-related dependencies."""
        try:
            import aiohttp
            import asyncio
            
            # Test basic aiohttp functionality
            assert aiohttp.ClientSession is not None
            
            # Test asyncio functionality
            assert asyncio.run is not None
            assert asyncio.gather is not None
            
        except ImportError as e:
            pytest.fail(f"Async dependency import failed: {e}")
    
    def test_testing_dependencies(self):
        """Test testing framework dependencies."""
        try:
            import pytest
            import pytest_asyncio
            import pytest_mock
            
            # Test pytest version is recent enough
            pytest_version = pytest.__version__
            major, minor = map(int, pytest_version.split('.')[:2])
            assert major >= 8 or (major == 7 and minor >= 0), f"Pytest 7.0+ required, got {pytest_version}"
            
        except ImportError as e:
            pytest.fail(f"Testing dependency import failed: {e}")


class TestConfigurationValidation:
    """Test configuration and environment setup."""
    
    def test_environment_variable_handling(self):
        """Test environment variable handling."""
        from src.services.weather_service import WeatherService
        import os
        
        # Test with no environment variable (should use None)
        original_key = os.environ.get("OPENWEATHER_API_KEY")
        if "OPENWEATHER_API_KEY" in os.environ:
            del os.environ["OPENWEATHER_API_KEY"]
        
        service = WeatherService()
        assert service.api_key is None
        
        # Test with environment variable
        os.environ["OPENWEATHER_API_KEY"] = "test_key"
        service = WeatherService()
        assert service.api_key == "test_key"
        
        # Restore original state
        if original_key:
            os.environ["OPENWEATHER_API_KEY"] = original_key
        elif "OPENWEATHER_API_KEY" in os.environ:
            del os.environ["OPENWEATHER_API_KEY"]
    
    def test_default_configuration_values(self):
        """Test default configuration values are reasonable."""
        from src.services.weather_service import WeatherService
        
        service = WeatherService()
        assert service.base_url == "https://api.openweathermap.org/data/2.5"
        assert service.session is None  # Should be None until context manager
    
    def test_mock_data_fallbacks(self):
        """Test that mock data fallbacks work when APIs unavailable."""
        from src.services.weather_service import WeatherService
        from src.models.emergency_models import WeatherCondition
        import asyncio
        
        async def test_mock_fallback():
            service = WeatherService()  # No API key
            condition = await service.get_current_conditions(40.7128, -74.0060)
            
            assert isinstance(condition, WeatherCondition)
            assert condition.temperature > 0
            assert condition.humidity >= 0
            assert condition.conditions != ""
            
            return True
        
        result = asyncio.run(test_mock_fallback())
        assert result is True
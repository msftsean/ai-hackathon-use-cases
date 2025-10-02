using Microsoft.Extensions.Logging;
using Moq;

namespace VirtualCitizenAgent.Tests;

/// <summary>
/// Test utilities and helpers
/// </summary>
public static class TestHelpers
{
    /// <summary>
    /// Creates a mock logger for testing
    /// </summary>
    public static Mock<ILogger<T>> CreateMockLogger<T>()
    {
        return new Mock<ILogger<T>>();
    }

    /// <summary>
    /// Verifies that a logger was called with specific log level
    /// </summary>
    public static void VerifyLogLevel<T>(Mock<ILogger<T>> mockLogger, LogLevel expectedLevel, Times times)
    {
        mockLogger.Verify(
            x => x.Log(
                expectedLevel,
                It.IsAny<EventId>(),
                It.IsAny<It.IsAnyType>(),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            times);
    }

    /// <summary>
    /// Verifies that a logger was called with specific message content
    /// </summary>
    public static void VerifyLogMessage<T>(Mock<ILogger<T>> mockLogger, string expectedMessage, Times times)
    {
        mockLogger.Verify(
            x => x.Log(
                It.IsAny<LogLevel>(),
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains(expectedMessage)),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            times);
    }
}
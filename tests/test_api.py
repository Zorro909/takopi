"""Tests for takopi.api public API exports."""

from __future__ import annotations


def test_api_version_constant() -> None:
    """TAKOPI_PLUGIN_API_VERSION constant is defined."""
    from takopi.api import TAKOPI_PLUGIN_API_VERSION

    assert isinstance(TAKOPI_PLUGIN_API_VERSION, int)
    assert TAKOPI_PLUGIN_API_VERSION > 0


def test_all_exports_importable() -> None:
    """All __all__ exports are importable."""
    import takopi.api

    for name in takopi.api.__all__:
        assert hasattr(takopi.api, name), f"{name} not exported"


def test_core_classes_exported() -> None:
    """Core plugin API classes are exported."""
    from takopi.api import (
        Action,
        ActionEvent,
        BaseRunner,
        CompletedEvent,
        ConfigError,
        CommandBackend,
        CommandContext,
        CommandExecutor,
        CommandResult,
        EngineBackend,
        EngineConfig,
        EngineId,
        ExecBridgeConfig,
        EventFactory,
        IncomingMessage,
        JsonlSubprocessRunner,
        MessageRef,
        DirectiveError,
        Presenter,
        RenderedMessage,
        ResumeToken,
        RunMode,
        RunRequest,
        RunResult,
        ResolvedMessage,
        ResolvedRunner,
        RunContext,
        Runner,
        RunnerUnavailableError,
        RunningTask,
        RunningTasks,
        SendOptions,
        SetupIssue,
        SetupResult,
        StartedEvent,
        Transport,
        TransportBackend,
        TransportRuntime,
        handle_message,
    )

    # Just verify they're importable - actual functionality tested elsewhere
    assert Action is not None
    assert ActionEvent is not None
    assert BaseRunner is not None
    assert CompletedEvent is not None
    assert ConfigError is not None
    assert CommandBackend is not None
    assert CommandContext is not None
    assert CommandExecutor is not None
    assert CommandResult is not None
    assert EngineBackend is not None
    assert EngineConfig is not None
    assert EngineId is not None
    assert ExecBridgeConfig is not None
    assert EventFactory is not None
    assert IncomingMessage is not None
    assert JsonlSubprocessRunner is not None
    assert MessageRef is not None
    assert DirectiveError is not None
    assert Presenter is not None
    assert RenderedMessage is not None
    assert ResumeToken is not None
    assert RunMode is not None
    assert RunRequest is not None
    assert RunResult is not None
    assert ResolvedMessage is not None
    assert ResolvedRunner is not None
    assert RunContext is not None
    assert Runner is not None
    assert RunnerUnavailableError is not None
    assert RunningTask is not None
    assert RunningTasks is not None
    assert SendOptions is not None
    assert SetupIssue is not None
    assert SetupResult is not None
    assert StartedEvent is not None
    assert Transport is not None
    assert TransportBackend is not None
    assert TransportRuntime is not None
    assert handle_message is not None

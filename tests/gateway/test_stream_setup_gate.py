"""Tests for gateway stream-consumer eligibility."""

from __future__ import annotations

from gateway.run import _adapter_can_use_stream_consumer


class EditableAdapter:
    SUPPORTS_MESSAGE_EDITING = True


class NonEditableDraftAdapter:
    SUPPORTS_MESSAGE_EDITING = False

    def __init__(self, supports: bool = True):
        self.supports = supports
        self.calls = []

    def supports_draft_streaming(self, *, chat_type=None, metadata=None):
        self.calls.append({"chat_type": chat_type, "metadata": metadata})
        return self.supports


def test_editable_adapter_can_use_stream_consumer_without_draft_probe():
    allowed, supports_edit = _adapter_can_use_stream_consumer(EditableAdapter())

    assert allowed is True
    assert supports_edit is True


def test_non_editable_adapter_can_stream_when_draft_supported():
    adapter = NonEditableDraftAdapter(supports=True)
    metadata = {"thread": "abc"}

    allowed, supports_edit = _adapter_can_use_stream_consumer(
        adapter,
        chat_type="dm",
        metadata=metadata,
        transport="auto",
    )

    assert allowed is True
    assert supports_edit is False
    assert adapter.calls == [{"chat_type": "dm", "metadata": metadata}]


def test_non_editable_adapter_without_draft_support_is_blocked():
    adapter = NonEditableDraftAdapter(supports=False)

    allowed, supports_edit = _adapter_can_use_stream_consumer(
        adapter,
        chat_type="dm",
        transport="auto",
    )

    assert allowed is False
    assert supports_edit is False


def test_non_editable_adapter_is_blocked_when_transport_forces_edit():
    adapter = NonEditableDraftAdapter(supports=True)

    allowed, supports_edit = _adapter_can_use_stream_consumer(
        adapter,
        chat_type="dm",
        transport="edit",
    )

    assert allowed is False
    assert supports_edit is False
    assert adapter.calls == []

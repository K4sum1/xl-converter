from unittest.mock import patch
import requests

import pytest
from PySide2.QtCore import QObject, Slot

from core.update_checker import (
    Worker,
    Runner,
    SIMULATE_SERVER_JSON
)
from data.constants import VERSION, UPDATE_CHECKER_VER_FILE_URL

class SignalCatcher(QObject):
    def __init__(self):
        super().__init__()
        self.signal_emitted = False
        self.error_messages = []

    @Slot()
    def on_signal(self):
        self.signal_emitted = True

    @Slot(str)
    def on_error(self, message):
        self.signal_emitted = True
        self.error_messages.append(message)

class StatusCodeErrorCatcher(QObject):
    def __init__(self):
        super().__init__()
        self.signal_emitted = False
        self.status_code = None

    @Slot(int)
    def on_signal(self, code):
        self.signal_emitted = True
        self.status_code = code


class MiscErrorCatcher(QObject):
    def __init__(self):
        super().__init__()
        self.signal_emitted = False
        self.error_message = None

    @Slot(str)
    def on_signal(self, message):
        self.signal_emitted = True
        self.error_message = message

class JsonCatcher(QObject):
    def __init__(self):
        super().__init__()
        self.signal_emitted = False
        self.json_data = None

    @Slot(dict)
    def on_signal(self, data):
        self.signal_emitted = True
        self.json_data = data

class FinishedCatcher(QObject):
    def __init__(self):
        super().__init__()
        self.signal_emitted = False

    @Slot()
    def on_signal(self):
        self.signal_emitted = True

@pytest.fixture
def worker():
    return Worker()

@pytest.fixture
def runner():
    r = Runner()
    yield r
    r.handleFinish()

def test_worker_simulate_server(worker):
    with patch("core.update_checker.SIMULATE_SERVER", True):
        json_catcher = JsonCatcher()
        finished_catcher = FinishedCatcher()
        worker.json.connect(json_catcher.on_signal)
        worker.finished.connect(finished_catcher.on_signal)

        worker.run()
    
        try:
            assert json_catcher.json_data == SIMULATE_SERVER_JSON
        except:
            pytest.fail("QSignalSpy instance error")
        assert json_catcher.signal_emitted
        assert finished_catcher.signal_emitted

def test_worker_connection_success(worker, requests_mock):
    tmp = {"latest_version": VERSION}
    requests_mock.get(UPDATE_CHECKER_VER_FILE_URL, json=tmp, status_code=200)
    json_catcher = JsonCatcher()
    finished_catcher = FinishedCatcher()
    worker.json.connect(json_catcher.on_signal)
    worker.finished.connect(finished_catcher.on_signal)

    worker.run()

    try:
        assert json_catcher.json_data == tmp
    except:
        pytest.fail("QSignalSpy instance error")
    assert json_catcher.signal_emitted
    assert finished_catcher.signal_emitted

def test_worker_connection_failed(worker, requests_mock, caplog):
    requests_mock.get(UPDATE_CHECKER_VER_FILE_URL, exc=requests.ConnectionError("No internet connection"))
    misc_error_catcher = MiscErrorCatcher()
    finished_catcher = FinishedCatcher()
    worker.misc_error.connect(misc_error_catcher.on_signal)
    worker.finished.connect(finished_catcher.on_signal)

    worker.run()

    try:
        assert misc_error_catcher.error_message == "Couldn't connect to the server."
    except:
        pytest.fail("QSignalSpy instance error")
    assert "No internet connection" in caplog.text
    assert finished_catcher.signal_emitted

def test_worker_status_code_error(worker, requests_mock):
    requests_mock.get(UPDATE_CHECKER_VER_FILE_URL, json={}, status_code=404)
    status_code_error_catcher = StatusCodeErrorCatcher()
    finished_catcher = FinishedCatcher()
    worker.status_code_error.connect(status_code_error_catcher.on_signal)
    worker.finished.connect(finished_catcher.on_signal)

    worker.run()

    try:
        assert status_code_error_catcher.status_code == 404
    except:
        pytest.fail("QSignalSpy instance error")
    assert finished_catcher.signal_emitted

def test_worker_parse_json_failed(worker, requests_mock):
    requests_mock.get(UPDATE_CHECKER_VER_FILE_URL, json=None, status_code=200)
    misc_error_catcher = MiscErrorCatcher()
    finished_catcher = FinishedCatcher()
    worker.misc_error.connect(misc_error_catcher.on_signal)
    worker.finished.connect(finished_catcher.on_signal)

    worker.run()

    try:
        assert misc_error_catcher.error_message == "Parsing JSON failed."
    except:
        pytest.fail("QSignalSpy instance error")
    assert finished_catcher.signal_emitted
    
@patch("core.update_checker.Worker")
@patch("core.update_checker.QThread")
def test_runner_run(mock_qthread, mock_worker, runner):
    worker_instance = mock_worker.return_value
    thread_instance = mock_qthread.return_value

    runner.run()

    thread_instance.started.connect.assert_called_once_with(worker_instance.run)
    worker_instance.finished.connect.assert_called_once_with(runner.handleFinish)
    worker_instance.json.connect.assert_called_once_with(runner.json)
    worker_instance.status_code_error.connect.assert_called_once_with(runner.handleErrorStatusCode)
    worker_instance.misc_error.connect.assert_called_once_with(runner.handleError)
    worker_instance.moveToThread.assert_called_once_with(thread_instance)
    thread_instance.start.assert_called_once()

def test_runner_handleErrorStatusCode(runner):
    catcher = SignalCatcher()
    runner.error.connect(catcher.on_error)

    runner.handleErrorStatusCode(404)
    runner.handleErrorStatusCode(500)
    runner.handleErrorStatusCode(123)

    try:
        assert catcher.error_messages[0] == "Version file not found."
        assert catcher.error_messages[1] == "Internal server error."
        assert catcher.error_messages[2] == "Error, status code: 123"
    except:
        pytest.fail("QSignalSpy instance error")

def test_runner_handleError(runner):
    catcher = SignalCatcher()
    runner.error.connect(catcher.on_error)

    runner.handleError("Custom error.")

    try:
        assert catcher.error_messages[0] == "Custom error."
    except:
        pytest.fail("QSignalSpy instance error")

@patch("core.update_checker.Worker")
@patch("core.update_checker.QThread")
def test_runner_handleFinish(mock_qthread, mock_worker, runner):
    worker_instance = mock_worker.return_value
    thread_instance = mock_qthread.return_value
    runner.thread = thread_instance
    runner.worker = worker_instance

    runner.handleFinish()

    thread_instance.isRunning.assert_called_once()
    thread_instance.requestInterruption.assert_called_once()
    thread_instance.quit.assert_called_once()
    thread_instance.wait.assert_called_once()
    thread_instance.deleteLater.assert_called_once()
    assert runner.thread is None
    worker_instance.deleteLater.assert_called_once()
    assert runner.worker is None

def test_runner_handleFinish_not_started(runner):
    catcher = SignalCatcher()
    runner.finished.connect(catcher.on_signal)

    runner.handleFinish()
    
    assert catcher.signal_emitted
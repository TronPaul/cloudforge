import unittest
import datetime
import mock

from boto.exception import BotoServerError
from boto.cloudformation.stack import StackEvent
from boto.cloudformation.connection import CloudFormationConnection

from cloudforge.watcher import filter_events_before, Watcher


def make_events(count):
    events = []
    for i in range(count):
        e = StackEvent()
        e.event_id = i
        events.append(e)
    return list(reversed(events))


def make_fake_event():
    fake_event = mock.MagicMock(spec=StackEvent)
    fake_event.timestamp = datetime.datetime.now()
    fake_event.resource_status = None
    fake_event.resource_type = None
    fake_event.logical_resource_id = None
    fake_event.physical_resource_id = None
    fake_event.event_id = None
    fake_event.resource_status_reason = None
    return fake_event


class WatcherTest(unittest.TestCase):
    def test_filter_events_no_matching_event(self):
        events = make_events(10)
        last_event = StackEvent()
        last_event.event_id = -1
        self.assertEqual(events, filter_events_before(last_event, events))

    def test_filter_events_first_matching_event(self):
        events = make_events(10)
        self.assertEqual(events[:0], filter_events_before(events[0], events))

    def test_filter_events_last_matching_event(self):
        events = make_events(10)
        self.assertEqual(events[:9], filter_events_before(events[-1], events))

    @mock.patch('cloudforge.watcher.time.sleep')
    def test_watch_stack(self, mock_sleep):
        conn = mock.MagicMock(spec=CloudFormationConnection)
        stack = conn.describe_stacks.return_value.__getitem__.return_value
        stack.stack_status.encode.side_effect = ['CREATE_IN_PROGRESS'] * 3 + ['CREATE_COMPLETE']
        watcher = Watcher(conn)
        rv = watcher.watch('test', ['CREATE_IN_PROGRESS'])
        self.assertEqual(3, stack.update.call_count)
        self.assertEqual(4, conn.describe_stack_events.call_count)
        self.assertEqual('CREATE_COMPLETE', rv)

    def test_watch_missing_stack_returns_gone(self):
        conn = mock.MagicMock(spec=CloudFormationConnection)
        error = BotoServerError(None, None)
        error.message = 'Stack:test does not exist'
        conn.describe_stacks.side_effect = error
        watcher = Watcher(conn)
        rv = watcher.watch('test', ['CREATE_IN_PROGRESS'])
        self.assertEqual('STACK_GONE', rv)

    @mock.patch('cloudforge.watcher.time.sleep')
    def test_watch_stack_going_missing_returns_gone(self, mock_sleep):
        conn = mock.MagicMock(spec=CloudFormationConnection)
        error = BotoServerError(None, None)
        error.message = 'Stack:test does not exist'
        stack = conn.describe_stacks.return_value.__getitem__.return_value
        stack.stack_status.encode.return_value = 'CREATE_IN_PROGRESS'
        conn.describe_stack_events.side_effect = [[make_fake_event()]] * 3 + [error]
        watcher = Watcher(conn)
        rv = watcher.watch('test', ['CREATE_IN_PROGRESS'])
        self.assertEqual('STACK_GONE', rv)


if __name__ == '__main__':
    unittest.main()

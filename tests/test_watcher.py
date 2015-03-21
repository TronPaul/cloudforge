import unittest
import mock
from boto.cloudformation.stack import StackEvent
from boto.cloudformation.connection import CloudFormationConnection
from cloudforge.watcher import filter_events_before, log_event, Watcher


def make_events(count):
    events = []
    for i in range(count):
        e = StackEvent()
        e.event_id = i
        events.append(e)
    return list(reversed(events))


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
        watcher.watch('test', ['CREATE_IN_PROGRESS'])
        self.assertEqual(3, stack.update.call_count)
        self.assertEqual(4, conn.describe_stack_events.call_count)


if __name__ == '__main__':
    unittest.main()

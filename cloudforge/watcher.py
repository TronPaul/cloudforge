import logging
from boto.exception import BotoServerError
import time


def filter_events_before(last_event, events):
    event_ids = [e.event_id for e in events]
    if last_event.event_id not in event_ids:
        return events
    else:
        pos = [pos for pos, eid in enumerate(event_ids) if eid == last_event.event_id][0]
        return events[:pos]


def log_event(logger, event):
    logger.info('{} {} {} {} {} {}'.format(
        event.timestamp.isoformat(),
        event.resource_status,
        event.resource_type,
        event.logical_resource_id,
        event.physical_resource_id,
        event.resource_status_reason
    ))


class Watcher(object):
    def __init__(self, connection, log_level):
        self.connection = connection
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level.upper()))

    def watch(self, stack_name, while_statuses):
        try:
            stack = self.connection.describe_stacks(stack_name)[0]
            prev_events = self.connection.describe_stack_events(stack_name)
        except BotoServerError as e:
            if e.error_message == 'Stack:{} does not exist'.format(stack_name):
                return 'STACK_GONE'
            else:
                raise e
        prev_event_count = 5
        self.logger.info('Last {} events for {} stack'.format(prev_event_count, stack_name))
        for event in reversed(prev_events[:prev_event_count]):
            log_event(event)
        self.logger.info('New events:')
        last_event = prev_events[0]
        status = stack.stack_status.encode('utf-8')
        while status in while_statuses:
            try:
                events = self.connection.describe_stack_events(stack_name)
            except BotoServerError as e:
                if e.error_message == 'Stack:{} does not exist'.format(stack_name):
                    return 'STACK_GONE'
                else:
                    raise e
            new_events = filter_events_before(last_event, events)
            if new_events:
                for event in reversed(new_events):
                    log_event(self.logger, event)
                last_event = new_events[0]
            stack.update()
            status = stack.stack_status.encode('utf-8')
            time.sleep(5)
        return status

PROCORE_GET_USER = '/vapid/me'
PROCORE_SHOW_SUBMITTAL = '/vapid/projects/{project_id}/submittals/{resource_id}'
PROCORE_SHOW_RFI = '/vapid/projects/{project_id}/rfis/{resource_id}'
PROCORE_WEBHOOKS = '/vapid/webhooks/hooks'
PROCORE_TRIGGERS = '/vapid/webhooks/hooks/{hook_id}/triggers'
PROCORE_TRIGGER = '/vapid/webhooks/hooks/{hook_id}/triggers/{trigger_id}'

procore_resource_endpoint_dict = {
    'Submittals': PROCORE_SHOW_SUBMITTAL,
    'RFIs': PROCORE_SHOW_RFI
}

GCAL_CALENDARS = '/users/me/calendarList'
GCAL_CALENDAR = '/calendars/{calendar_id}'
GCAL_EVENTS = '/calendars/{calendar_id}/events'
GCAL_EVENT = '/calendars/{calendar_id}/events/{event_id}'

SELF_WEBHOOK_HANDLER = '/webhook_handler'
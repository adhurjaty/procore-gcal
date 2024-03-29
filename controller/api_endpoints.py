PROCORE_GET_USER = '/vapid/me'
PROCORE_SHOW_SUBMITTAL = '/vapid/projects/{project_id}/submittals/{resource_id}'
PROCORE_SHOW_RFI = '/vapid/projects/{project_id}/rfis/{resource_id}'
PROCORE_WEBHOOKS = '/vapid/webhooks/hooks?project_id={project_id}'
PROCORE_TRIGGERS = '/vapid/webhooks/hooks/{hook_id}/triggers?project_id={project_id}'
PROCORE_TRIGGER = '/vapid/webhooks/hooks/{hook_id}/triggers/{trigger_id}?project_id={project_id}'
PROCORE_COMPANIES = '/vapid/companies'
PROCORE_PROJECTS = '/vapid/projects'

procore_resource_endpoint_dict = {
    'Submittals': PROCORE_SHOW_SUBMITTAL,
    'RFIs': PROCORE_SHOW_RFI
}

GCAL_CALENDARS = '/users/me/calendarList'
GCAL_CALENDAR = '/calendars/{calendar_id}'
GCAL_EVENTS = '/calendars/{calendar_id}/events'
GCAL_EVENT = '/calendars/{calendar_id}/events/{event_id}'
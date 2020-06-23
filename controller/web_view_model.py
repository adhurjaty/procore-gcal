from typing import List

from util.utils import get_signed_token
from interactor.account_manager_response import AccountManagerResponse


class WebViewModel:

    def show_user(self, user: AccountManagerResponse):
        selected_calendar = user.gcal_data.calendar_id or \
            (user.calendars and user.calendars[0].id)
        return {
            'id': user.id,
            'email': user.email,
            'fullName': user.full_name,
            'calendars': user.calendars and [c.to_json() for c in user.calendars] or [],
            'isGcalLoggedIn': user.calendars is not None,
            'selectedCalendar': selected_calendar,
            'eventTypes': user.procore_data.calendar_event_types,
            'collaborators': [{'id': c.id, 'name': c.full_name} for c in user.collaborators],
            'emailSettings': user.procore_data.email_settings,
            'temporary': user.temporary,
            'isSubscribed': user.subscribed,
            'projectId': user.project_id,
            'projects': [{'id': p.id, 'name': p.name} for p in user.projects],
            'csrfToken': get_signed_token(user.procore_data.token.access_token)
        }




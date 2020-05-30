from typing import List

from .gcal_view_model import GCalViewModel
from .procore_view_model import ProcoreViewModel
from .web_view_model import WebViewModel
from .vm_factory import VMFactory
from interactor.presenter_interface import PresenterInterface
from interactor.account_manager_response import AccountManagerResponse
from interactor.user_response import UserResponse
from interactor.procore_event import ProcoreEvent
from interactor.rfi import Rfi
from interactor.submittal import Submittal
from interactor.change_order import ChangeOrder
from interactor.named_item import NamedItem

class Presenter(PresenterInterface):
    vm_factory: VMFactory = None

    def __init__(self, vm_factory: VMFactory):
        super().__init__()
        self.vm_factory = vm_factory

    def get_user_info(self, token: dict) -> dict:
        procore_vm = self.vm_factory.create_procore_vm(token=token)

        return procore_vm.get_user_info()

    def get_manager_vm(self, user: AccountManagerResponse) -> dict:
        vm = self.vm_factory.create_web_vm()
        return vm.show_user(user)

    def get_procore_event(self, user: UserResponse, resource_name: str='', 
        resource_id: int=-1) -> ProcoreEvent:

        vm = self.vm_factory.create_procore_vm(user)
        event = vm.get_event(resource_name=resource_name, resource_id=resource_id)
        procore_event = self._get_event_type(event)
        procore_event.update_from_dict(event)
        return procore_event

    def _get_event_type(self, event: dict) -> ProcoreEvent:
        if event.get('rfi_manager'):
            return Rfi()
        if event.get('submittal_manager'):
            return Submittal()
        if event.get('signed_change_order_received_date'):
            return ChangeOrder()
        raise Exception('Unimplemented event type')

    def update_gcal(self, user: AccountManagerResponse, event: ProcoreEvent):
        vm = self.vm_factory.create_gcal_vm(user)

        if isinstance(event, Rfi):
            vm.set_rfi_event(event)
            return
        if isinstance(event, Submittal):
            vm.set_submittal_events(event)
            return
        # if isinstance(event, ChangeOrder):
        #     pass

        raise Exception('Unimplemented event type')

    def set_manager_selections(self, user: AccountManagerResponse):
        user.projects = self._get_projects(user)
        user.calendars = self._get_calendars(user)
        return user

    def _get_projects(self, user: AccountManagerResponse) -> List[NamedItem]:
        vm = self.vm_factory.create_procore_vm(user)
        company_ids = vm.get_company_ids()
        projects = vm.get_projects(company_ids)
        return [NamedItem(p['id'], p['name']) for p in projects]

    def _get_calendars(self, user: UserResponse) -> List[NamedItem]:
        vm = self.vm_factory.create_gcal_vm(user)
        calendars = vm.get_calendars()
        return [NamedItem(c['id'], c['name']) for c in calendars]

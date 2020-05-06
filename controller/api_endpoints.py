PROCORE_GET_USER = '/vapid/me'
PROCORE_SHOW_SUBMITTAL = '/vapid/projects/{project_id}/submittals/{resource_id}'
PROCORE_SHOW_RFI = '/vapid/projects/{project_id}/rfis/{resource_id}'

procore_resource_endpoint_dict = {
    'Submittals': PROCORE_SHOW_SUBMITTAL,
    'RFIs': PROCORE_SHOW_RFI
}

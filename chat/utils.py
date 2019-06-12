TYPE_SCOUT = "new_participant_scout"
TYPE_TENANT = "new_participant_tenant"

ParticipantTypeCategories = (
    (TYPE_SCOUT, 'New Scout'),
    (TYPE_TENANT, 'New Tenant')
)


def get_sender_from_request(request, accept_sender_from_request_body=False):
    if accept_sender_from_request_body:
        return request.data["sender"]

    return request.user.participant


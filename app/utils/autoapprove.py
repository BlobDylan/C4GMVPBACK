from app.models import Event, Registration


def should_autoapprove_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return False

    regs = Registration.query.filter_by(event_id=event_id).all()
    if not regs:
        return False

    family_rep_count = 0
    guide_count = 0
    for reg in regs:
        if reg.user and reg.user.role == "Family Representative":
            family_rep_count += 1
        elif reg.user and reg.user.role == "Guide":
            guide_count += 1

    if family_rep_count >= 1:
        return True
    if guide_count >= event.num_instructors_needed:
        return True
    return False

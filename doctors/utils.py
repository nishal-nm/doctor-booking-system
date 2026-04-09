from datetime import datetime, timedelta
from appointments.models import Appointment


# Generate available slots for a doctor on a given date
def generate_slots(doctor, date, for_admin=False):

    # Check if doctor works on this day
    day_name = date.strftime('%A').lower()
    if day_name not in doctor.working_days:
        return []

    # Skip if doctor is on approved leave
    is_on_leave = doctor.leave_requests.filter(
        date=date,
        status='approved'
    ).exists()
    if is_on_leave:
        return []

    # Get already booked slot start times
    booked_times = set(
        Appointment.objects.filter(
            doctor=doctor,
            date=date
        ).values_list('start_time', flat=True)
    )

    slots = []

    # Prepare time range and slot duration
    current = datetime.combine(date, doctor.start_time)
    end = datetime.combine(date, doctor.end_time)
    duration = timedelta(minutes=doctor.slot_duration)

    total_count = 0

    # Loop through time range and generate slots
    while current + duration <= end:

        # Limit slots based on max consultations per day
        if total_count >= doctor.consultations_per_day:
            break

        slot_time = current.time()
        total_count += 1

        is_booked = slot_time in booked_times

        # For admin: show all slots with status
        if for_admin:
            slots.append({
                'start_time': slot_time.strftime('%H:%M'),
                'end_time': (current + duration).time().strftime('%H:%M'),
                'status': 'booked' if is_booked else 'available'
            })

        # For customer: only show available slots
        elif not is_booked:
            slots.append({
                'start_time': slot_time.strftime('%H:%M'),
                'end_time': (current + duration).time().strftime('%H:%M'),
            })

        # Move to next slot
        current += duration

    return slots
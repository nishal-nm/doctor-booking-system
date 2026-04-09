from datetime import datetime, timedelta
from appointments.models import Appointment


def generate_slots(doctor, date, for_admin=False):
    day_name = date.strftime('%A').lower()
    if day_name not in doctor.working_days:
        return []

    is_on_leave = doctor.leave_requests.filter(
        date=date,
        status='approved'
    ).exists()
    if is_on_leave:
        return []

    booked_times = set(
        Appointment.objects.filter(
            doctor=doctor,
            date=date
        ).values_list('start_time', flat=True)
    )

    slots = []
    current = datetime.combine(date, doctor.start_time)
    end = datetime.combine(date, doctor.end_time)
    duration = timedelta(minutes=doctor.slot_duration)
    total_count = 0

    while current + duration <= end:
        if total_count >= doctor.consultations_per_day:
            break
        slot_time = current.time()
        total_count += 1
        is_booked = slot_time in booked_times
        if for_admin:
            slots.append({
                'start_time': slot_time.strftime('%H:%M'),
                'end_time': (current + duration).time().strftime('%H:%M'),
                'status': 'booked' if is_booked else 'available'
            })
        elif not is_booked:
            slots.append({
                'start_time': slot_time.strftime('%H:%M'),
                'end_time': (current + duration).time().strftime('%H:%M'),
            })
        current += duration

    return slots
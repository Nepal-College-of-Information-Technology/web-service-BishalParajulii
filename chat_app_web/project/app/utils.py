from django.utils import timezone

def format_timestamp(timestamp):
    now = timezone.now()
    if timestamp.date() == now.date():
        return f"Today at {timestamp.strftime('%I:%M %p')}"
    elif timestamp.date() == (now - timezone.timedelta(days=1)).date():
        return f"Yesterday at {timestamp.strftime('%I:%M %p')}"
    elif timestamp.year == now.year:
        return timestamp.strftime('%b %d at %I:%M %p')
    else:
        return timestamp.strftime('%b %d, %Y at %I:%M %p')

from django import template
import datetime

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, None)


@register.filter
def time_ago(value):
    now = datetime.datetime.now(datetime.timezone.utc)
    diff = now - value
    
    if diff.days >= 1:
        return f"{diff.days}d ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours}h ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes}m ago"
    else:
        return "just now"

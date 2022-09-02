from django import template
from django.utils.timesince import timesince
from django.utils.translation import ngettext_lazy

register = template.Library()


def thousands_separator(num):
    return "{:,}".format(num)

def truncate_zero_decimal(num):
    return int(num) if num < int(num) + 0.1 else int(num * 10) / 10

@register.filter(name='tweet_time_since')
def tweet_time_since(value):
    time_strings = {
        "year": ngettext_lazy("%(num)d year", "%(num)d years", "num"),
        "month": ngettext_lazy("%(num)d month", "%(num)d months", "num"),
        "week": ngettext_lazy("%(num)dw", "%(num)dw", "num"),
        "day": ngettext_lazy("%(num)dd", "%(num)dd", "num"),
        "hour": ngettext_lazy("%(num)dh", "%(num)dh", "num"),
        "minute": ngettext_lazy("%(num)dm", "%(num)dm", "num"),
    }
    timesince_str = timesince(value, time_strings=time_strings).replace(',', '')
    return timesince_str

@register.filter(name='abbreviate_num')
def abbreviate_num(value):
    """
    Takes a number and abbreviates it.

    Examples: 
    45678 -> 45.6K
    1000000 -> 1M
    1230000 -> 1.2M
    """
    print()
    suffixes = ['K', 'M', 'B']
    intervals = [1e3, 1e6, 1e9, 1e12]
    threshold = 1e4
    
    if value < threshold:
        return thousands_separator(value)
    
    for ix in range(len(suffixes)):
        if intervals[ix] <= value < intervals[ix + 1]:
            prefix = value / intervals[ix]
            return thousands_separator(truncate_zero_decimal(prefix)) + suffixes[ix]
from django import template

register = template.Library()


def thousands_separator(num):
    return "{:,}".format(num)

def truncate_zero_decimal(num):
    return int(num) if num < int(num) + 0.1 else int(num * 10) / 10

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
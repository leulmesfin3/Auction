    
from django import template

register = template.Library()

def my_rank(item, user): 
    return item.rank(user)

def my_last_price(item, user): 
    return item.last_price(user)

register.filter(my_rank)
register.filter(my_last_price)
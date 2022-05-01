from enum import Enum, IntEnum

class StatusEnum(str, Enum):
    draft = 'draft'
    submitted = 'submitted'
    approved = 'approved'
    rejected = 'rejected'
    shipping = 'shipping'
    completed = 'completed'
    partial_fulfillment = 'partial fulfillment'
    
class LogisticsEnum(str, Enum):
    own = 'own_logistics'
    eunimart = 'eunimart_logistics'



def greater_than_1_gram(v):
    if float(v) >= 0.001:
        return v
    else:
        raise ValueError('must be greater than or equal to 1 gram (0.001 Kg)')
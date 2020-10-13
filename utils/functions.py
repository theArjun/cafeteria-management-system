def calculate_percentage(amount: float, percent: float, method: str):
    if amount < 0:
        raise ValueError('Amount should be positive.')
    if percent < 0 or percent > 100:
        raise ValueError('Percent should be between 0.0 and 100.0')
    if method not in ['+', '-']:
        raise ValueError('Method should be either + or -')

    if method == '+':
        return amount + amount * percent / 100
    elif method == '-':
        return amount - amount * percent / 100

from django.http import JsonResponse

from cafeteria.models import Stock


def get_stock(request, id):
    try:
        item_stock = Stock.objects.get(id=id)
        stock = item_stock.item_remaining
    except Stock.DoesNotExist:
        stock = 0
    response = {
        'stock':stock
    }
    return JsonResponse(response)



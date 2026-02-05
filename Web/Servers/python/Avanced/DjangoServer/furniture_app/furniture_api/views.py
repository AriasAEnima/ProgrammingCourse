from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import FurnitureItem

# Create your views here.
@api_view(['GET'])
def get_furnitures(request):
    width = request.GET.get("width",0)
    muebles  = list(FurnitureItem.objects(width__gte=width).order_by('-creation_date'))
    muebles_seriazable = list(map(lambda f_item: f_item.as_dic(),muebles))
    return Response(muebles_seriazable, status=200)

@api_view(['POST'])
def post_furniture(request):
    body = request.data
    new_furniture = FurnitureItem(
        name = body['name'],
        width = body['width'],
        height = body['height'],
        depth = body['depth'],
        material = body['material'])
    new_furniture.save()    
    return Response(new_furniture.as_dic(), status=201)

def get_furniture(_,id):
    try:
        furniture =  FurnitureItem.objects.get(id=id)
        return Response(furniture.as_dic(), status= 200)
    except FurnitureItem.DoesNotExist:
        return Response({"message": f"Furniture {id} not exist"}, status= 404)
    

def delete_furniture(_,id):
    try:
        furniture =  FurnitureItem.objects.get(id=id)
        data = furniture.as_dic()
        furniture.delete()
        return Response(data, status= 200)
    except FurnitureItem.DoesNotExist:
        return Response({"message": f"Furniture {id} not exist"}, status= 204)

@api_view(["GET","DELETE"])
def handle_one_furniture(request,id):
    if request.method== "GET":
        return get_furniture(request,id)
    else:
        return delete_furniture(request,id)
    
@api_view(["GET"])
def v2(_,id):
    furniture =  FurnitureItem.objects.get(id=id)
    data = furniture.as_dic()
    data["version"] = "V2"
    return Response(data, status= 200)

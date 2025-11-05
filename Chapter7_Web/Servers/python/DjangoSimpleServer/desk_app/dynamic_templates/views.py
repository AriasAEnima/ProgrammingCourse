from django.shortcuts import render

# Create your views here.

desks = [
                {"desk_id": 1, "name": "Mesa Venture", "width": 125, "height": 225},
                {"desk_id": 2, "name": "Mesa Koto", "width": 200, "height": 223},
                {"desk_id": 3, "name": "Mesa Amatista", "width": 200, "height": 300}
            ]

def get_desk(_,desk_id):
   filtered = list(filter(lambda x : x["desk_id"]==desk_id,desks))
   return filter[0]


def get_desks(request):
   contexto = {
       "desks" : desks,
       "tab_title": "GET ALL DESKS"
   }
   return render(request,'dynamic_templates/desk_list.html', contexto)
    
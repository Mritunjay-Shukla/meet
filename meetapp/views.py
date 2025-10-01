from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def create_room(request):
    # Hardcode or generate a random room string
    if request.method=="GET":
        return render(request, "room_create.html")
    else:
        room_id = request.POST["room_id"]
        room_id = room_id.replace(" ", "_")
        return redirect(f"/call/room/{room_id}/")

def call_room(request, room_id):
    is_host = request.user.is_authenticated  # only logged-in users = host
    return render(request, "call.html", {"room_id": room_id, "is_host": is_host})
 
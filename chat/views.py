from django.shortcuts import render

def index(request):
    return render(request, "chat/index.html")

def pdb(request, pdb_id):
    return render(request, "chat/pdb.html", {"pdb_id": pdb_id})

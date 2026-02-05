import requests
from django.shortcuts import render, redirect

def anime_list(request):
    query = request.GET.get("q")

    res = requests.get(
        "https://api.jikan.moe/v4/anime",
        params={"q": query, "limit": 20}
    )

    data = res.json()["data"]
    return render(request, "anime_list.html", {"anime": data})

def anime_detail(request, anime_id):
    res = requests.get(f"https://api.jikan.moe/v4/anime/{anime_id}")
    anime = res.json()["data"]
    return render(request, "anime_detail.html", {"anime": anime})

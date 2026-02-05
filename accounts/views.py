from django.shortcuts import render, redirect
from .supabase import supabase

def register_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        user_id = res.user.id
        supabase.table("profiles").insert({
            "id": user_id,
            "username": email.split("@")[0]
        }).execute()
        # auto login after signup
        request.session["user_id"] = res.user.id
        request.session.modified = True
        return redirect("/anime/")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        request.session["user_id"] = res.user.id
        return redirect("/anime/")

    return render(request, "login.html")


def logout_view(request):
    request.session.flush()
    return redirect("/login/")


def add_to_list(request):
    if request.method == "POST":
        supabase.table("anime_list").insert({
            "user_id": request.session["user_id"],
            "mal_id": request.POST["mal_id"],
            "title": request.POST["title"],
            "image_url": request.POST["image"]
        }).execute()

    return redirect("/anime/")


def my_list(request):
    res = supabase.table("anime_list") \
        .select("*") \
        .eq("user_id", request.session["user_id"]) \
        .execute()

    return render(request, "my_list.html", {"anime": res.data})


def update_status(request):
    if request.method == "POST":
        supabase.table("anime_list") \
            .update({"status": request.POST["status"]}) \
            .eq("id", request.POST["id"]) \
            .execute()

    return redirect("/my-list/")


def remove_anime(request):
    if request.method == "POST":
        supabase.table("anime_list") \
            .delete() \
            .eq("id", request.POST["id"]) \
            .execute()

    return redirect("/my-list/")

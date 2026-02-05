from django.shortcuts import render, redirect
from .supabase import supabase

def register_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            # Sign up user
            auth_res = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            # Check if user was created
            if not auth_res.user:
                return render(request, "register.html", {"error": "Registration failed"})
            
            user_id = auth_res.user.id
            
            # Insert profile - separate try-catch so auth success still logs in
            try:
                supabase.table("profiles").insert({
                    "id": user_id,
                    "username": email.split("@")[0]
                }).execute()
            except Exception as profile_error:
                print(f"Profile creation error (continuing): {profile_error}")
            
            # Auto login after signup
            request.session["user_id"] = user_id
            request.session.modified = True
            print(f"User registered and logged in: {user_id}")  # Debug
            return redirect("/anime/")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Registration error: {error_msg}")
            
            if "already registered" in error_msg.lower():
                error_msg = "Email already registered. Try logging in."
            elif "password" in error_msg.lower():
                error_msg = "Password must be at least 6 characters"
            
            return render(request, "register.html", {"error": error_msg})
    
    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not res.user:
                return render(request, "login.html", {"error": "Invalid credentials"})

            request.session["user_id"] = res.user.id
            request.session.modified = True
            print(f"User logged in: {res.user.id}")  # Debug
            return redirect("/anime/")
            
        except Exception as e:
            print(f"Login error: {e}")
            return render(request, "login.html", {"error": "Invalid email or password"})

    return render(request, "login.html")


def logout_view(request):
    user_id = request.session.get("user_id")
    print(f"User logged out: {user_id}")  # Debug
    request.session.flush()
    return redirect("/login/")


def add_to_list(request):
    if request.method == "POST":
        # Check session
        if "user_id" not in request.session:
            print("Add to list: No user_id in session")
            return redirect("/login/")
        
        user_id = request.session["user_id"]
        print(f"Adding anime for user: {user_id}")  # Debug
        
        try:
            supabase.table("anime_list").insert({
                "user_id": user_id,
                "mal_id": request.POST["mal_id"],
                "title": request.POST["title"],
                "image_url": request.POST["image"]
            }).execute()
        except Exception as e:
            print(f"Add to list error: {e}")

    return redirect("/anime/")


def my_list(request):
    # Check session
    if "user_id" not in request.session:
        print("My list: No user_id in session")
        return redirect("/login/")
    
    user_id = request.session["user_id"]
    print(f"Fetching list for user: {user_id}")  # Debug
    
    try:
        res = supabase.table("anime_list") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()
        
        print(f"Found {len(res.data)} anime for user {user_id}")  # Debug
        return render(request, "my_list.html", {"anime": res.data})
    except Exception as e:
        print(f"My list error: {e}")
        return render(request, "my_list.html", {"anime": [], "error": str(e)})


def update_status(request):
    if request.method == "POST":
        if "user_id" not in request.session:
            return redirect("/login/")
        
        try:
            supabase.table("anime_list") \
                .update({"status": request.POST["status"]}) \
                .eq("id", request.POST["id"]) \
                .eq("user_id", request.session["user_id"]) \
                .execute()
        except Exception as e:
            print(f"Update status error: {e}")

    return redirect("/my-list/")


def remove_anime(request):
    if request.method == "POST":
        if "user_id" not in request.session:
            return redirect("/login/")
        
        try:
            supabase.table("anime_list") \
                .delete() \
                .eq("id", request.POST["id"]) \
                .eq("user_id", request.session["user_id"]) \
                .execute()
        except Exception as e:
            print(f"Remove anime error: {e}")

    return redirect("/my-list/")


# Anime API views
import requests

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
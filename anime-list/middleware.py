from django.shortcuts import redirect

class SupabaseAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of paths that don't require login
        public_paths = ['/login/', '/register/', '/static/']
        
        if not any(request.path.startswith(path) for path in public_paths):
            if 'user_id' not in request.session:
                return redirect('/login/')
        
        return self.get_response(request)
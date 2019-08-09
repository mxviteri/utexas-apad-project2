def user_context(request):
    context_data = dict()
    context_data["current_user"] = request.USER
    return context_data
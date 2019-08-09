import ast

def getCurrentUser(get_response):

    def middleware(request):
        if 'user' in request.COOKIES:
            value = request.COOKIES['user']
            request.USER = ast.literal_eval(value)
        else:
            request.USER = {}

        response = get_response(request)
        return response

    return middleware


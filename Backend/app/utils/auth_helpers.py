# This imports wraps, a helper from Python's functools module. 
# It's used to preserve metadata (like function name and docstring) when wrapping functions with decorators.
from functools import wraps
# This imports verify_jwt_in_request and get_jwt_identity from Flask-JWT-Extended.
# verify_jwt_in_request() ensures that a valid JWT is present in the request (usually in the Authorization header).
#get_jwt_identity() retrieves the user's identity (usually the user ID) from the token.
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify
# Imports the User model so you can query the database and check the current user's role.
from app.models.members import Member

# Defines the outer function of the decorator. It accepts a variable number of roles,
# The asterisk * before the parameter name (roles) allows the function to accept any number of arguments, which will be collected into a tuple.
# In this context, roles will be a tuple containing all the role names you want to allow access to a route.
def role_required(*roles):
    
    # Defines the inner decorator function that wraps the target function (fn) you want to protect.
    def decorator(fn):

        # This is the actual wrapper function that will replace the original function.
        # Ensures the wrapped function keeps its original name and docstring, which is useful for debugging and introspection.
        @wraps(fn)
        # Defines the actual function that will run instead of fn if access is denied.
        # *args and **kwargs allow the wrapper to accept any number of positional and keyword arguments, just like the original function.
        def wrapper(*args, **kwargs):
            # Verify the JWT token
            # Verifies that the request contains a valid JWT. If not, it will automatically return a 401 Unauthorized.
            verify_jwt_in_request()
            # Get the current user's identity
            current_user_id = get_jwt_identity()
            user = Member.query.get(current_user_id)

            if not user:
                return jsonify({"msg": "User not found"}), 404

            if user.role not in roles:
                return jsonify({"msg": f"Access forbidden for role {user.role}"}), 403

            return fn(*args, **kwargs)

        return wrapper
    return decorator

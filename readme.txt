the authentication flow:

User Login:


Upon successful login, the server returns both an access token and a refresh token to the client.
Accessing Protected Routes:

When the client accesses a protected route (e.g., /protected, /users), it includes the access token in the request header.
If the access token is valid and not expired, the server allows access to the protected route.
If the access token is expired, the server returns a 403 response indicating that the token has expired.
Token Refresh:

If the client receives a 403 response due to an expired access token, it can then send a request to the /refresh endpoint with the refresh token.
The server verifies the refresh token, and if it's valid, it generates a new access token and returns it to the client.
The client can then retry the original request to the protected route with the new access token.
Accessing the Users Route:

The /users route is protected and requires a valid access token to access.
If the access token is expired when accessing the /users route, the token_required decorator automatically refreshes the access token using the refresh token before allowing access to the route.
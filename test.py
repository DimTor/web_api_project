from requests import get

print(get('http://localhost:5000/api/artists').json())


print(get('http://localhost:5000/api/artists/3').json())
print(get('http://localhost:5000/api/artists/54').json())
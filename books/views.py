from django.http import JsonResponse
from .models import Genre, Author

def search_genres(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Limit to top 20 matches so the UI stays fast and clean
    genres = Genre.objects.filter(name__icontains=query)[:20]
    results = [{'id': g.id, 'text': g.name} for g in genres]
    return JsonResponse({'results': results})


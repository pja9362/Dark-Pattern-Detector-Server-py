import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@csrf_exempt
def detect_price_pattern(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        url = data.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        print('장고 스크래핑 시작! URL:', url)
        
        return JsonResponse({'message': 'Scraping started!'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

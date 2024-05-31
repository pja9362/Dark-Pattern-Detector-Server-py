import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

@csrf_exempt
def detect_price_pattern(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        url = data.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        print('장고 스크래핑 시작! URL:', url)

        try:
            options = Options()
            options.add_argument("--headless")
            options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
            options.add_argument("--log-level=3")
            options.add_experimental_option("detach", True)

            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            driver.get(url)
            WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-selenium="selectedHotelContainer"]')))
            sleep(3)

            def scroll(trial):
                actions = ActionChains(driver)
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    for _ in range(trial):
                        actions.send_keys(Keys.SPACE).perform()
                        sleep(1)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height

            scroll(2)

            list_items = driver.find_elements(By.CSS_SELECTOR, 'div[data-selenium="selectedHotelContainer"]')
            sleep(1)

            class Hotel:
                def __init__(self, name, price, link):
                    self.name = name
                    self.price = price
                    self.link = link

                def __str__(self):
                    return self.name + " = " + self.price
                
                def __repr__(self):
                    return str(self)

            show_prices = []
            for item in list_items[:1]:  # 상위 1개의 호텔만 대상으로 함
                hotel_name = WebDriverWait(item, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h3[data-selenium="hotel-name"]')))
                hotel_price = WebDriverWait(item, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-element-name="final-price"]')))
                hotel_link = item.find_element(By.CSS_SELECTOR, 'a[data-element-name="property-card-content"]').get_attribute('href')
                
                if hotel_name is not None and hotel_price is not None:
                    new_hotel_data = Hotel(hotel_name.text, hotel_price.text, hotel_link)
                    show_prices.append(new_hotel_data)

            def get_room_prices(hotel_name, hotel_url):
                driver.get(hotel_url)
                sleep(2)
                print("객실 페이지 진입!!!!!!", hotel_name, hotel_url)
                
                room_prices = []
                room_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-selenium="MasterRoom"]')))
                print("총 객실 개수: ", len(room_elements))
                
                for room in room_elements:
                    try:
                        room_options_list = room.find_elements(By.CSS_SELECTOR, 'div[data-selenium="ChildRoomsList-room"]')
                        
                        print("총 옵션 개수: ", len(room_options_list))
                        idx = 1
                        for room_option in room_options_list:
                            room_price_element = room_option.find_element(By.CSS_SELECTOR, 'strong[data-ppapi="room-price"]')
                            room_price_text = room_price_element.text.replace(',', '').replace('₩', '')
                            room_prices.append(int(room_price_text))
                            print(f"{idx}번째 객실 가격: {room_price_text}")
                            idx += 1
                        
                    except:
                        print(f"가격 정보를 가져올 수 없습니다: {room}")
                        
                if len(room_prices) > 0:
                    print(f"{hotel_name}의 객실 가격 정보: ", room_prices)
                    avg_price = sum(room_prices) / len(room_prices)
                    max_price = max(room_prices)
                    print(f"{hotel_name}의 평균 객실 가격: ₩{avg_price:.0f}")
                    print(f"{hotel_name}의 최고 객실 가격: ₩{max_price:.0f}")
                    return avg_price, max_price
                
                return None, None

            def get_final_price(hotel_url):
                final_price_list = []
                btn_list = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button[data-selenium="ChildRoomsList-bookButtonInput"]')))
                for i in range(len(btn_list)):
                    driver.get(hotel_url)
                    sleep(3)
                
                    re_btn_list = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button[data-selenium="ChildRoomsList-bookButtonInput"]')))
                    sleep(1)
                    driver.execute_script("arguments[0].click();", re_btn_list[i])

                    final_price_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="TotalPrice__boldText--3W9eX"]')))
                    final_price_text = final_price_element.text.replace('₩', '').replace(',', '')
                    final_price_list.append(int(final_price_text))
                    sleep(3)

                avg_real_price = sum(final_price_list) // len(final_price_list)
                return avg_real_price, final_price_list

            results = []
            for hotel in show_prices:
                avg_price, max_price = get_room_prices(hotel.name, hotel.link)
                if avg_price is not None and max_price is not None:
                    avg_final_price, final_price = get_final_price(hotel.link)
                    print(f"{hotel.name}의 평균 최종 가격: ₩{avg_final_price}")
                    print(f"{hotel.name}의 최종 가격 리스트: {final_price}")
                    results.append({
                        'hotel_name': hotel.name,
                        'avg_price': avg_price,
                        'max_price': max_price,
                        'avg_final_price': avg_final_price,
                        'final_price_list': final_price
                    })
                else:
                    results.append({
                        'hotel_name': hotel.name,
                        'error': '객실 가격 정보를 가져올 수 없습니다.'
                    })

            print('결과:', results)
            driver.quit()

            return JsonResponse({'hotels': results})
        except Exception as e:
            print("스크래핑 중 예외 발생:", e)
            driver.quit()
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


# 헤드리스 적용 전
# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# from time import sleep
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys

# @csrf_exempt
# def detect_price_pattern(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         url = data.get('url')

#         if not url:
#             return JsonResponse({'error': 'URL is required'}, status=400)

#         print('장고 스크래핑 시작! URL:', url)

#         try:
#             options = Options()
#             # options.add_argument("--headless")  # Uncomment if you want to run headless
#             options.add_argument("--start-maximized")
#             options.add_experimental_option("detach", True)

#             service = ChromeService(ChromeDriverManager().install())
#             driver = webdriver.Chrome(service=service, options=options)

#             driver.get(url)
#             WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-selenium="selectedHotelContainer"]')))
#             sleep(3)

#             def scroll(trial):
#                 actions = ActionChains(driver)
#                 last_height = driver.execute_script("return document.body.scrollHeight")
#                 while True:
#                     for _ in range(trial):
#                         actions.send_keys(Keys.SPACE).perform()
#                         sleep(1)
#                     new_height = driver.execute_script("return document.body.scrollHeight")
#                     if new_height == last_height:
#                         break
#                     last_height = new_height

#             scroll(1)

#             list_items = driver.find_elements(By.CSS_SELECTOR, 'div[data-selenium="selectedHotelContainer"]')
#             sleep(1)

#             class Hotel:
#                 def __init__(self, name, price, link):
#                     self.name = name
#                     self.price = price
#                     self.link = link

#                 def __str__(self):
#                     return self.name + " = " + self.price
                
#                 def __repr__(self):
#                     return str(self)

#             show_prices = []
#             for item in list_items[:1]:  # 상위 2개의 호텔만 대상으로 함
#                 hotel_name = WebDriverWait(item, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h3[data-selenium="hotel-name"]')))
#                 hotel_price = WebDriverWait(item, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-element-name="final-price"]')))
#                 hotel_link = item.find_element(By.CSS_SELECTOR, 'a[data-element-name="property-card-content"]').get_attribute('href')
                
#                 if hotel_name is not None and hotel_price is not None:
#                     new_hotel_data = Hotel(hotel_name.text, hotel_price.text, hotel_link)
#                     show_prices.append(new_hotel_data)

#             def get_room_prices(hotel_name, hotel_url):
#                 driver.get(hotel_url)
#                 sleep(2)
#                 print("객실 페이지 진입!!!!!!", hotel_name, hotel_url)
                
#                 room_prices = []
#                 room_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-selenium="MasterRoom"]')))
#                 print("총 객실 개수: ", len(room_elements))
                
#                 for room in room_elements:
#                     try:
#                         room_options_list = room.find_elements(By.CSS_SELECTOR, 'div[data-selenium="ChildRoomsList-room"]')
                        
#                         print("총 옵션 개수: ", len(room_options_list))
#                         idx = 1
#                         for room_option in room_options_list:
#                             room_price_element = room_option.find_element(By.CSS_SELECTOR, 'strong[data-ppapi="room-price"]')
#                             room_price_text = room_price_element.text.replace(',', '').replace('₩', '')
#                             room_prices.append(int(room_price_text))
#                             print(f"{idx}번째 객실 가격: {room_price_text}")
#                             idx += 1
                        
#                     except:
#                         print(f"가격 정보를 가져올 수 없습니다: {room}")
                        
#                 if len(room_prices) > 0:
#                     print(f"{hotel_name}의 객실 가격 정보: ", room_prices)
#                     avg_price = sum(room_prices) / len(room_prices)
#                     max_price = max(room_prices)
#                     print(f"{hotel_name}의 평균 객실 가격: ₩{avg_price:.0f}")
#                     print(f"{hotel_name}의 최고 객실 가격: ₩{max_price:.0f}")
#                     return avg_price, max_price
                
#                 return None, None

#             results = []
#             for hotel in show_prices:
#                 avg_price, max_price = get_room_prices(hotel.name, hotel.link)
#                 if avg_price is not None and max_price is not None:
#                     results.append({
#                         'hotel_name': hotel.name,
#                         'avg_price': avg_price,
#                         'max_price': max_price,
#                     })
#                 else:
#                     results.append({
#                         'hotel_name': hotel.name,
#                         'error': '객실 가격 정보를 가져올 수 없습니다.'
#                     })

#             driver.quit()

#             return JsonResponse({'hotels': results})
#         except Exception as e:
#             print("스크래핑 중 예외 발생:", e)
#             driver.quit()
#             return JsonResponse({'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Invalid request method'}, status=405)

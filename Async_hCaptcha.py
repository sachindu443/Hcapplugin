from selenium.webdriver.chrome.options import Options
from colorama import Fore, init
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np
import cvlib as cv
import requests,json,time,cv2,asyncio,aiohttp,json,os

init(convert=True)

HEADERS = {
    'authority': 'hcaptcha.com',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://assets.hcaptcha.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'en-US,en;q=0.9'
}

SUBMITHEADERS = {
    'authority': 'hcaptcha.com',
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://assets.hcaptcha.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'en-US,en;q=0.9'}

builder = {}
c = {}
host2 = 'host'
sitekey2 = 'sitekey'
obj = object
url = ""
taskkey = ""
res = {}
req = ''
reqs = {}
solution = ""

#<--Gets Reqs-->
async def get_req(host,sitekey):
    global c
    async with aiohttp.ClientSession() as session:
            async with session.get(f'https://hcaptcha.com/checksiteconfig?host={host}&sitekey={sitekey}&sc=1&swa=1') as resp:
                value = await resp.json()
                c = value['c']
                return value['c']['req']

#<--Gets Payload-->
async def get_payload(host,sitekey):
    global req
    req = await get_req(host,sitekey)
    n = await get_n(req)
    data = {
        'sitekey':sitekey,
        'host':host,
        'hl': 'en',
        'motionData': '{}',
        'n': n,
        'c': '{"type":"hsw","req":"' + req + '"}'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post('https://hcaptcha.com/getcaptcha',headers = HEADERS,data = data) as resp2:
            value2 = await resp2.json()
            return value2

#<--Gets n Value-->
async def get_n(req):
    options = Options()
    options.headless = True
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    with open("result.js", "r") as f:
        return driver.execute_script(f.read() + f"return hsw('{req}');")

#<--Checks If Successful-->
async def is_correct(obj, url, taskkey):
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp3:
                    image = resp3.text()
            nparr = np.frombuffer(image, np.uint8)
            im = cv2.imdecode(nparr, flags=1)
            objects = cv.detect_common_objects(im, confidence=0.5, nms_thresh=1, enable_gpu=False)[1]
            if obj.lower() in objects:
                builder['answers'][taskkey] = 'true'
                return
            builder['answers'][taskkey] = 'false'
            break
        except Exception as e:
            return

#<--Handles Image Processing-->
async def handle_images(host2,sitekey2):
    payload = await get_payload(host2,sitekey2)
    print(f"{Fore.GREEN}[{Fore.WHITE}INFO{Fore.GREEN}]{Fore.CYAN} Received payload")
    key = payload['key']
    obj = payload['requester_question']['en'].split(' ')[-1].replace("motorbus", "bus")
    builder['job_mode'] = 'image_label_binary'
    builder['answers'] = {}
    builder['serverdomain'] = host2
    builder['sitekey'] = sitekey2
    builder['motionData'] = '{"st":' + str(int(round(time.time() * 1000))) +',"dct":' + str(int(round(time.time() * 1000))) +',"mm": []}'
    builder['n'] = await get_n(c['req'])
    builder['c'] = json.dumps(c).replace("'", '"')
    for task in payload['tasklist']:
        taskkey = task['task_key']
        url = task['datapoint_uri']
        await is_correct(obj, url, taskkey)
    await submit(key)

#<--Submits Keys-->
async def submit(key):
    global solution
    async with aiohttp.ClientSession() as session:
        async with session.post(f'https://hcaptcha.com/checkcaptcha/{key}',headers = SUBMITHEADERS,data = json.dumps(builder)) as resp3:
            value3 = await resp3.json()
    if value3['pass']:
        solution = value3['generated_pass_UUID']
        print(f"{Fore.GREEN}[{Fore.WHITE}PASSED{Fore.GREEN}] {Fore.CYAN}hCaptcha has been solved...")
        print(f"{Fore.GREEN}[{Fore.WHITE}KEY{Fore.GREEN}] {Fore.CYAN}UUID:\n{Fore.LIGHTBLACK_EX}" + solution)
        print(solution)
    else:
        print(f"{Fore.RED}[{Fore.WHITE}FAIL{Fore.RED}] Retrying...")
        await handle_images(host2,sitekey2)

#<--Checks Image Values-->
async def is_correct(obj, url, taskkey):
        while True:
            try:
                image = requests.get(url)
                nparr = np.frombuffer(image.content, np.uint8)
                im = cv2.imdecode(nparr, flags=1)
                objects = cv.detect_common_objects(im, confidence=0.5, nms_thresh=1, enable_gpu=False)[1]
                if obj.lower() in objects:
                    print(f'{Fore.GREEN}[{Fore.WHITE}INFO{Fore.GREEN}] {Fore.CYAN}{taskkey}.jpg is a {obj}')
                    builder['answers'][taskkey] = 'true'
                    return
                print(f'{Fore.GREEN}[{Fore.WHITE}INFO{Fore.GREEN}] {Fore.CYAN}{taskkey}.jpg is not a {obj}')
                builder['answers'][taskkey] = 'false'
                break
            except Exception as e:
                print(f"{Fore.RED}[{Fore.WHITE}ERROR{Fore.RED}] Unexpected error: {Fore.WHITE}{e}")
                return

async def Hcaptcha_Handler(host,sitekey):
    global solution,builder,c,obj,url,taskkey,res,req,reqs,host2,sitekey2
    host2 = host
    sitekey2 = sitekey
    solution = ""
    if os.path.exists('yolov3.weights') is False:
        print('yolov3.weights is not installed. Please Install from:(https://pjreddie.com/media/files/yolov3.weights)')
        return
    if os.path.exists('chromedriver.exe') is False:
        print('chromedriver.exe is not installed. Please Install from:(https://chromedriver.chromium.org/)')
        return
    await handle_images(host2,sitekey2)
    return solution

#asyncio.run(Hcaptcha_Handler('caspers.app','eaaffc67-ea9f-4844-9740-9eefd238c7dc'))
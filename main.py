import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openai import OpenAI

def do_course(title, stop):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, title))).click()
    do_vod(title, stop)
    if key != '0':
        do_examination(title)

def do_vod(title, stop):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, 'Lectures'))).click()
    for i in range(stop):
        print(f"{title} 수강 중 ... ({i+1}/{stop})")
        if 'complete' in driver.find_elements(By.CLASS_NAME, 'li04')[i].get_attribute('class'):
            continue
        btns = driver.find_elements(By.CLASS_NAME, 'btn_vod')[1::2]
        btns[i].click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'play-pause-button'))).click()
        WebDriverWait(driver, 9999).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
        time.sleep(3)

def do_examination(title):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, 'Examination'))).click()
    time.sleep(3)
    try:
        passed_element = driver.find_element(By.XPATH, "//table[@class='info-table']//td[text()='Passed']")
        print(f"{title}: 이미 완료된 시험입니다.")
        return
    except:
        pass
    driver.find_element(By.LINK_TEXT, 'LINK').click()
    question_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li"))
    )
    valid_questions = [item for item in question_elements if item.text and item.text.split('.')[0].isdigit()]
    
    for question_element in valid_questions:
        print(f"{title}: Examination test 진행 중 ... ({question_element.text.split('.')[0]}/{len(valid_questions)})")
        table_text = ''
        try:
            table_element = question_element.find_element(By.CSS_SELECTOR, "table")
            table_text = table_element.text
        except:
            pass
        question = f'{question_element.find_element(By.CLASS_NAME, "line-tit").text}\n{table_text}'

        option_elements = question_element.find_elements(By.CSS_SELECTOR, "li.check label")
        options = [option.text.strip() for option in option_elements]

        correct_option_indices = get_answer_from_chatgpt(question, options)
        radio_buttons = question_element.find_elements(By.CSS_SELECTOR, "li.check input[type='radio']")
        for index in correct_option_indices:
            radio_buttons[index].click()

    driver.find_element(By.ID, "btn_submit").click()
    driver.switch_to.alert.accept()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "btn_submit"))).click()
    driver.switch_to.alert.accept()
    try:
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
    except:
        pass
    print(f"{title} 완료 !")
    time.sleep(3)

def get_answer_from_chatgpt(question, options):
    options = ''.join(f'{idx}. {value}\n' for idx, value in enumerate(options))
    prompt = f'''
    Read the following question and choose the correct options:
    Question: {question}
    Options:
    {options}
    Please give me the correct answers **in number array format**. (ex: [0, 3]), **Do not include any other text**'''
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    answer = response.choices[0].message.content
    return eval(answer)
    
#본인 아이디, 비밀번호, api키 입력
id = input('아이디를 입력하세요: ')
pw = input('비밀번호를 입력하세요: ')
key = input('ChatGPT API Key를 입력하세요 (Examination test 응시에 필요함, 없으면 0 입력): ')

client = OpenAI(api_key=key)

my_options = webdriver.ChromeOptions()
my_options.add_argument('headless')
driver = webdriver.Chrome(options=my_options)
driver.implicitly_wait(3)
driver.get("https://iam2.kaist.ac.kr/api/sso/commonLogin?client_id=EETHICS&state=1736507761&redirect_url=https%3A%2F%2Feethics.kaist.ac.kr%2Fauth%2Fauth2.php")

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, '오늘 하루 그만보기'))).click()
driver.find_element(By.ID, 'IdInput').send_keys(id)
driver.find_element(By.XPATH, '/html/body/div/div/div[2]/div/div/fieldset/ul/li[2]/input[2]').click()
driver.find_element(By.ID, 'passwordInput').send_keys(pw)
driver.find_element(By.CLASS_NAME, 'loginbtn').click()

do_course('Lab Safety', 7)
do_course('Cyber Ethics', 33)
do_course('Research Technology Security', 6)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, 'Research Ethics'))).click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, 'Lectures'))).click()
for i in range(8):
    print(f"Research Ethics 수강 중 ... ({i+1}/8)")
    if 'complete' in driver.find_elements(By.CLASS_NAME, 'li04')[i].get_attribute('class'):
        continue
    driver.find_element(By.XPATH, f'/html/body/div/div[3]/div[3]/div[2]/div/div/div[1]/ul/li[{2+i*2}]/ul/li[1]/span[2]').click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.pop-b-close'))).click()
    WebDriverWait(driver, 10).until(EC.alert_is_present())
    driver.switch_to.alert.accept()
    time.sleep(3)
if key != '0':
    do_examination("Research Ethics")

driver.quit()
print("윤리및안전 교육을 모두 이수했습니다. 프로그램을 종료해주세요.")
os.system('pause')
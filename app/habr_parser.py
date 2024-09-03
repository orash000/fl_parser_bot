from dotenv import load_dotenv
from os import getenv
import requests
from bs4 import BeautifulSoup


load_dotenv()
HABR_URL = getenv("HABR_URL")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36"
}


last_seen_ids = set()


def fetch_tasks():
    response = requests.get(HABR_URL, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    tasks = soup.find_all("li", class_="content-list__item")

    return tasks[:5]


def parse_task(task):
    title_elem = task.find("div", class_="task__title")
    title = title_elem.get_text(strip=True)
    link = title_elem.find("a")["href"]

    tags = [tag.get_text(strip=True) for tag in task.find_all("a", class_="tags__item_link")]

    price_elem = task.find("div", class_="task__price")
    if price_elem.find("span", class_="negotiated_price"):
        price = "Договорная"
    else:
        price = price_elem.find("span", class_="count").get_text(strip=True)

    task_url = "https://freelance.habr.com" + link
    task_response = requests.get(task_url, headers=headers)
    task_soup = BeautifulSoup(task_response.content, "html.parser")

    description_elem = task_soup.find("div", class_="task__description")
    description = description_elem.get_text(separator="\n", strip=True)

    return {
        "title": title,
        "link": task_url,
        "tags": tags,
        "price": price,
        "description": description
    }


def format_task(parsed_task):
    title = f"📝 <b>{parsed_task['title']}</b>"
    link = f"🔗 <a href='{parsed_task['link']}'>Ссылка на задачу</a>"
    tags = f"🏷 <b>Теги:</b> {', '.join(parsed_task['tags'])}" if parsed_task['tags'] else "🏷 <b>Теги:</b> отсутствуют"
    price = f"💰 <b>Цена:</b> {parsed_task['price']}"
    description = f"📄 <b>Описание:</b>\n{parsed_task['description']}"

    return f"{title}\n\n{tags}\n\n{description}\n\n{price}\n\n{link}"


def check_for_new_tasks(tasks):
    global last_seen_ids
    new_tasks = []

    for task in tasks:
        task_id = task.find("a")["href"].split('/')[-1]
        if task_id not in last_seen_ids:
            last_seen_ids.add(task_id)
            new_tasks.append(task)

    return new_tasks


def fetch_and_format_tasks():
    tasks = fetch_tasks()
    new_tasks = check_for_new_tasks(tasks)

    if new_tasks:
        formatted_tasks = [format_task(parse_task(task)) for task in new_tasks]
        return formatted_tasks
    else:
        return []

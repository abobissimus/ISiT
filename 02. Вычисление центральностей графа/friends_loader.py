import time
import csv
import requests

ACCESS_TOKEN = "vk1.a.F1PWqXaiR-ddZsENlL-UqalycRA4aBmb0JJd8HhA8jb_kRkyAzn13a1uRSttC8gmYztt_M_BtqhmyajnNDJdEalGtzsE23mUw9kt7eLw0riqX8XObbsLfuyruTdmxbQN0MSiNclUh4qrrYpAhQtACJ0C-kKeHDAGym_wAUtUowzZLpMq5thMoKBGpBRGPQ7G"
API_VERSION = "5.199"
BASE_URL = "https://api.vk.com/method"
PAUSE = 0.35

CONTRIBUTORS = [488243736, 340121125, 326866301, 219305476] # Авторы работы (V0)

def vk_get(method, params):
    params["access_token"] = ACCESS_TOKEN
    params["v"] = API_VERSION
    while True:
        time.sleep(PAUSE)
        r = requests.get(f"{BASE_URL}/{method}", params=params, timeout=30).json()
        if "response" in r:
            return r["response"]
        err = r.get("error", {})
        code = err.get("error_code")
        if code in (15, 18, 30):
            return {"items": []}
        if code == 6:
            time.sleep(1.0)
            continue
        raise RuntimeError(f"VK error {code}: {err.get('error_msg')}")

def get_friends(uid, params={}):
    resp = vk_get("friends.get", params | {"user_id": uid})
    return resp.get("items", [])

def main():
    if ACCESS_TOKEN in ("", "YOUR_ACCESS_TOKEN"):
        raise SystemExit("Вставьте реальный ACCESS_TOKEN вверху файла.")

    v0 = set(CONTRIBUTORS)
    v1 = set()
    v2 = set()
    edges = set()

    # 1) Получаем друзей авторов работы (V1)
    print("Получение друзей авторов работы...")
    k = 0
    for user in v0:
        friends = get_friends(user)
        v1 |= set(friends)
        edges |= set([(user, friend) for friend in friends])
        k += 1
        print(f"\r{k}/{len(v0)}", end="")
    print()
    
    # 2) Получаем друзей друзей авторов работы (V2)
    print("Получение друзей друзей авторов работы...")
    k = 0
    for user in v1:
        friends = get_friends(user)
        v2 |= set(friends)
        edges |= set([(user, friend) for friend in friends])
        k += 1
        print(f"\r{k}/{len(v1)}", end="")
    print()

    vertices = v0 | v1 | v2
    
    # 3) Получаем друзей друзей друзей авторов работы (максимум 500 для каждого) без расширения множества вершин
    print("Уточнение связей между друзьями друзей авторов работы...")
    k = 0
    for user in v2:
        try:
            friends = get_friends(user, {"count": 500})
        except Exception as e:
            print(f"\nОшибка: {e}. Сохраняем то, что есть")
            break
        edges |= set([(user, friend) for friend in friends if friend in vertices])
        k += 1
        print(f"\r{k}/{len(v2)}", end="")
    
    print(f"Вершин: {len(vertices)}\nРебер: {len(edges)}\n\nСохранение данных в файл...")

    with open("friends.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source", "target"])
        for source, target in edges:
            w.writerow([source, target])
    print("Сохранено: friends.csv")

if __name__ == "__main__":
    start_time = time.time()
    main()
    running_time = time.time() - start_time
    print(f"Время выполнения: {running_time:.3f} секунд")

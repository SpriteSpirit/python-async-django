import random
import time
import redis


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    """
    Класс для ограничения частоты запросов к API
    """

    def __init__(
        self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0
    ):
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
        self.limit = 5
        self.window = 3

    def test(self) -> bool:
        """
        Проверяет, можно ли выполнить новый запрос, не превышая лимит в 5 запросов за последние 3 с.
        Используется упорядоченное множество.
        zcard() возвращает количество элементов в Sorted Set.
        После удаления старых запросов в Sorted Set остаются только те, которые были сделаны за последние 3 с.
        request_count — кол-во запросов за последние 3 с.
        """

        current_time = time.time()
        # ключ для хранения временной метки запросов
        key = "api_requests"

        # удаление элементов с временной меткой в диапазоне от -inf до тек. минус окно
        self.redis.zremrangebyscore(key, "-inf", current_time - self.window)

        # получение кол-ва запросов за последние 3 сек.
        request_count = self.redis.zcard(key)

        if request_count < self.limit:
            # добавление текущего запроса в Redis
            self.redis.zadd(key, {current_time: current_time})
            return True

        return False


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес-логика
        pass


if __name__ == "__main__":
    rate_limiter = RateLimiter()

    for _ in range(50):
        time.sleep(random.randint(1, 2))

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")

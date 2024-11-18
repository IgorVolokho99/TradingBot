from data_loader import load_data
from environment import TradingEnv
from model import train_model, test_model


def main():
    data = load_data()
    print("Данные успешно загружены.")
    print(f"Количество записей в данных: {len(data)}")

    train_data = data.iloc[:int(len(data) * 0.8)]
    test_data = data.iloc[int(len(data) * 0.8):]

    window_size = 168

    train_env = TradingEnv(train_data, window_size)
    print("Обучающая среда успешно создана.")

    print("Начинается обучение модели...")
    model = train_model(train_env)
    print("Обучение завершено.")

    test_env = TradingEnv(test_data, window_size)
    print("Тестовая среда успешно создана.")

    print("Начинается тестирование модели...")
    test_model(model, test_env)
    print("Тестирование завершено.")


if __name__ == "__main__":
    main()

import torch
import torch.nn as nn
import torchvision.models as models
from torch.utils.data import Dataset, DataLoader
import cv2
import numpy as np
import json


# ==================== ЗАГРУЗЧИК ДАННЫХ ====================
class DocumentCornerDataset(Dataset):
    def __init__(self, data_list, img_dir):
        self.data = data_list  # Список из JSON
        self.img_dir = img_dir  # Папка с картинками

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        # Получаем данные: [имя, x1,y1,x2,y2,x3,y3,x4,y4]
        item = self.data[idx]

        # Имя файла
        img_name = item[0]
        img_path = f"{self.img_dir}/{img_name}"

        # Загружаем картинку
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Координаты углов (8 чисел)
        corners = np.array(item[1:9], dtype=np.float32)

        # Нормализуем координаты (переводим в диапазон 0-1)
        h, w, _ = image.shape
        corners[0::2] /= w  # X координаты
        corners[1::2] /= h  # Y координаты

        # Преобразуем картинку в тензор PyTorch
        image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0

        return image, corners


# ==================== МОДЕЛЬ ====================
class CornerDetector(nn.Module):
    def __init__(self):
        super(CornerDetector, self).__init__()
        self.model = models.resnet18(weights='DEFAULT')
        self.model.fc = nn.Identity()
        self.fc = nn.Linear(512, 8)

    def forward(self, x):
        features = self.model(x)
        features = features.view(features.size(0), -1)
        corners = self.fc(features)
        return torch.sigmoid(corners)


# ==================== ОБУЧЕНИЕ ====================
if __name__ == "__main__":
    # 1. ЗАГРУЖАЕМ ДАННЫЕ ИЗ JSON
    print("Загрузка данных из JSON...")
    with open('json/json_main.json', 'r', encoding='utf-8') as f:
        data = json.load(f)  # data - это список

    print(f"Загружено примеров: {len(data)}")

    # 2. СОЗДАЁМ DATASET
    IMG_DIR = 'images/'  # Поменяй на свой путь!
    dataset = DocumentCornerDataset(data, IMG_DIR)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

    # 3. СОЗДАЁМ МОДЕЛЬ
    model = CornerDetector()

    # 4. ФУНКЦИЯ ПОТЕРЬ И ОПТИМИЗАТОР
    criterion = nn.SmoothL1Loss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # 5. ОБУЧЕНИЕ
    print("Начинаем обучение...")
    num_epochs = 20

    for epoch in range(num_epochs):
        total_loss = 0

        for images, targets in dataloader:
            # Прямой проход
            outputs = model(images)

            # Считаем ошибку
            loss = criterion(outputs, targets)

            # Обратный проход
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        print(f"Эпоха {epoch + 1}/{num_epochs}, Ошибка: {avg_loss:.4f}")

    # 6. СОХРАНЯЕМ МОДЕЛЬ
    torch.save(model.state_dict(), 'моя_модель_углов.pth')
    print("Модель сохранена!")
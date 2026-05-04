import torch
import torch.nn as nn
import torchvision.models as models
from torch.utils.data import Dataset, DataLoader
import cv2
import numpy as np
import json


### класс для загрузки датасета
class DocumentCornerDataset(Dataset):
    def __init__(self, data_list, img_dir):
        self.data = data_list  # json
        self.img_dir = img_dir  # png

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        # [id,x1,y1,x2,y2,x3,y3,x4,y4]
        item = self.data[idx]

        # имя картинки
        img_name = item[0]
        img_path = f"{self.img_dir}/{img_name}"

        # загрузка данного имени картинки
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # доставание углов
        corners = np.array(item[1:9], dtype=np.float32)

        # перевод координат в отрезок [0; 1]
        h, w, _ = image.shape
        corners[0::2] /= w  # X координаты
        corners[1::2] /= h  # Y координаты

        # преобразование в тензор пайторча
        image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0

        return image, corners


### модель нейросети
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


### обучение
if __name__ == "__main__":
    # загрузка разметки
    with open('json/json_main.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Загружено примеров: {len(data)}")

    # создание датасета
    IMG_DIR = 'images/'
    dataset = DocumentCornerDataset(data, IMG_DIR)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

    # модель
    model = CornerDetector()

    # штука проверяет потери
    criterion = nn.SmoothL1Loss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # само обучение
    print("Начало обучения")
    num_epochs = 20

    for epoch in range(num_epochs):
        total_loss = 0

        for images, targets in dataloader:
            # прямой проход
            outputs = model(images)

            # считаем ошибку
            loss = criterion(outputs, targets)

            # обратный проход
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        print(f"Эпоха {epoch + 1}/{num_epochs}, Ошибка: {avg_loss:.4f}")

    # сохранение
    torch.save(model.state_dict(), 'corner_model.pth')
    print("Модель сохранена")
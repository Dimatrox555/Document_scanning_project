import torch
import torch.nn as nn
from torchvision import models

model = models.resnet18(weights="DEFAULT")

model.fc = nn.Sequential(
    nn.Linear(model.fc.in_features, 8),
    nn.Sigmoid()
)
## нужно разобраться как начать обучение и кормить датасеты этой штуке
#!/usr/bin/env python3

import mlx
import mlx.core as mx
import mlx.nn as nn

class TestModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(10, 10)
    
    def forward(self, x):
        return self.linear(x)

# 測試
model = TestModel()
x = mx.random.normal((2, 10))

# 直接調用forward
print("Using forward():")
output = model.forward(x)
print(f"Output shape: {output.shape}")

# 使用__call__
print("\nUsing __call__():")
try:
    output = model(x)
    print(f"Output shape: {output.shape}")
except Exception as e:
    print(f"Error: {e}")

# 檢查model類型
print(f"\nModel type: {type(model)}")
print(f"Is callable: {callable(model)}")
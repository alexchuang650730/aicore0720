#!/usr/bin/env python3
"""
Manus歷史數據提取器
基於1000小時Manus使用經驗，提取真實對比數據
"""

import json
import time
import sqlite3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from real_time_comparison_tracker import RealTimeComparisonTracker

@dataclass
class ManusSession:
    """Manus會話記錄"""
    session_id: str
    timestamp: float
    prompt: str
    response: str
    category: str
    complexity: str
    satisfaction_score: int  # 基於實際使用效果評分 1-10
    time_taken: float
    tokens_used: int
    task_completed: bool
    notes: str

class ManusDataExtractor:
    """Manus數據提取器"""
    
    def __init__(self):
        self.tracker = RealTimeComparisonTracker()
        self.extracted_sessions = []
        
        # 基於Manus 1000小時經驗的場景分類
        self.scenario_categories = {
            "frontend": ["react", "vue", "typescript", "javascript", "css", "html", "ui"],
            "backend": ["python", "fastapi", "django", "node", "api", "server"],
            "algorithm": ["sort", "search", "dp", "graph", "tree", "leetcode"],
            "database": ["sql", "mongodb", "redis", "query", "optimization"],
            "devops": ["docker", "kubernetes", "deployment", "ci/cd", "aws"],
            "debug": ["error", "bug", "fix", "troubleshoot", "exception"],
            "architecture": ["design", "system", "scalability", "microservice"],
            "optimization": ["performance", "memory", "speed", "efficiency"]
        }
    
    def extract_from_manus_history(self, manual_entries: List[Dict]) -> List[ManusSession]:
        """
        手動輸入Manus歷史數據
        
        格式：
        {
            "prompt": "創建React Hook管理表單狀態",
            "response": "生成的代碼內容...",
            "satisfaction": 8,
            "time_taken": 45.2,
            "task_completed": True,
            "notes": "代碼質量很好，但缺少錯誤處理"
        }
        """
        sessions = []
        
        for i, entry in enumerate(manual_entries):
            # 自動分類
            category = self._categorize_prompt(entry["prompt"])
            complexity = self._assess_complexity(entry["prompt"], entry["response"])
            
            session = ManusSession(
                session_id=f"manus_{int(time.time())}_{i}",
                timestamp=time.time() - (len(manual_entries) - i) * 3600,  # 假設每小時一個任務
                prompt=entry["prompt"],
                response=entry["response"],
                category=category,
                complexity=complexity,
                satisfaction_score=entry["satisfaction"],
                time_taken=entry.get("time_taken", 30.0),
                tokens_used=len(entry["response"]) // 4,  # 估算token數
                task_completed=entry.get("task_completed", True),
                notes=entry.get("notes", "")
            )
            
            sessions.append(session)
        
        self.extracted_sessions = sessions
        return sessions
    
    def _categorize_prompt(self, prompt: str) -> str:
        """基於prompt內容自動分類"""
        prompt_lower = prompt.lower()
        
        for category, keywords in self.scenario_categories.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return category
        
        return "general"
    
    def _assess_complexity(self, prompt: str, response: str) -> str:
        """評估任務複雜度"""
        # 基於prompt和response長度、關鍵詞評估
        prompt_indicators = ["design", "architecture", "complex", "multiple", "integrate"]
        medium_indicators = ["create", "implement", "build", "develop"]
        
        if any(indicator in prompt.lower() for indicator in prompt_indicators):
            return "complex"
        elif any(indicator in prompt.lower() for indicator in medium_indicators):
            return "medium"
        elif len(response) > 1000:
            return "medium"
        else:
            return "simple"
    
    def convert_to_comparison_data(self) -> List[str]:
        """轉換為對比數據格式"""
        comparison_ids = []
        
        for session in self.extracted_sessions:
            # 記錄作為Claude歷史數據
            comparison_id = self.tracker.quick_log_claude_only(
                prompt=session.prompt,
                category=session.category,
                complexity=session.complexity,
                response=session.response,
                satisfaction=session.satisfaction_score,
                time_seconds=session.time_taken,
                notes=f"Manus歷史: {session.notes}"
            )
            
            comparison_ids.append(comparison_id)
        
        return comparison_ids
    
    def generate_k2_test_scenarios(self) -> List[Dict]:
        """生成K2測試場景"""
        test_scenarios = []
        
        for session in self.extracted_sessions:
            if session.satisfaction_score >= 7:  # 只對滿意的結果進行K2測試
                test_scenarios.append({
                    "prompt": session.prompt,
                    "category": session.category,
                    "complexity": session.complexity,
                    "expected_quality": session.satisfaction_score,
                    "original_time": session.time_taken,
                    "comparison_notes": f"與Manus結果對比 (原始滿意度: {session.satisfaction_score}/10)"
                })
        
        return test_scenarios

# Manus 1000小時經驗的重點場景示例
MANUS_SAMPLE_DATA = [
    {
        "prompt": "創建React自定義Hook用於API數據獲取，包含loading、error狀態管理",
        "response": """import { useState, useEffect } from 'react';

const useApi = (url) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [url]);

  return { data, loading, error };
};""",
        "satisfaction": 7,
        "time_taken": 25.5,
        "task_completed": True,
        "notes": "基本功能正確，但缺少重試機制和取消請求功能"
    },
    {
        "prompt": "實現Python快速排序算法，包含優化和邊界處理",
        "response": """def quicksort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# 優化版本 - 原地排序
def quicksort_inplace(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pi = partition(arr, low, high)
        quicksort_inplace(arr, low, pi - 1)
        quicksort_inplace(arr, pi + 1, high)

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1""",
        "satisfaction": 9,
        "time_taken": 35.0,
        "task_completed": True,
        "notes": "優秀的實現，包含兩種版本，邊界處理完善"
    },
    {
        "prompt": "設計FastAPI用戶認證系統，包含JWT token和權限管理",
        "response": """from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

app = FastAPI()
security = HTTPBearer()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_token(user_id: str):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/login")
def login(username: str, password: str):
    # 驗證用戶邏輯
    if verify_user(username, password):
        token = create_token(username)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/protected")
def protected_route(user_id: str = Depends(verify_token)):
    return {"message": f"Hello {user_id}"}""",
        "satisfaction": 8,
        "time_taken": 45.0,
        "task_completed": True,
        "notes": "功能完整，但缺少refresh token和角色權限系統"
    },
    {
        "prompt": "優化SQL查詢性能，處理大量數據的分頁和索引",
        "response": """-- 原始查詢（性能差）
SELECT u.name, u.email, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2023-01-01'
GROUP BY u.id
ORDER BY order_count DESC
LIMIT 20;

-- 優化後查詢
-- 1. 添加索引
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_users_id_created ON users(id, created_at);

-- 2. 優化查詢
WITH user_orders AS (
    SELECT 
        u.id,
        u.name,
        u.email,
        COUNT(o.id) as order_count
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.created_at > '2023-01-01'
        AND u.id > :last_user_id  -- 游標分頁
    GROUP BY u.id, u.name, u.email
    ORDER BY u.id
    LIMIT 20
)
SELECT * FROM user_orders
ORDER BY order_count DESC;""",
        "satisfaction": 9,
        "time_taken": 40.0,
        "task_completed": True,
        "notes": "優秀的查詢優化，考慮了索引和分頁策略"
    },
    {
        "prompt": "創建Vue 3組件實現表格功能，支持排序、搜索、分頁",
        "response": """<template>
  <div class="data-table">
    <div class="table-controls">
      <input 
        v-model="searchQuery" 
        placeholder="搜索..." 
        class="search-input"
      />
    </div>
    
    <table>
      <thead>
        <tr>
          <th 
            v-for="column in columns" 
            :key="column.key"
            @click="sort(column.key)"
            :class="{ sortable: column.sortable }"
          >
            {{ column.title }}
            <span v-if="sortColumn === column.key">
              {{ sortDirection === 'asc' ? '↑' : '↓' }}
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in paginatedData" :key="row.id">
          <td v-for="column in columns" :key="column.key">
            {{ row[column.key] }}
          </td>
        </tr>
      </tbody>
    </table>
    
    <div class="pagination">
      <button @click="prevPage" :disabled="currentPage === 1">上一頁</button>
      <span>{{ currentPage }} / {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages">下一頁</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  data: Array,
  columns: Array,
  pageSize: { type: Number, default: 10 }
})

const searchQuery = ref('')
const sortColumn = ref('')
const sortDirection = ref('asc')
const currentPage = ref(1)

const filteredData = computed(() => {
  if (!searchQuery.value) return props.data
  return props.data.filter(row =>
    Object.values(row).some(value =>
      String(value).toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  )
})

const sortedData = computed(() => {
  if (!sortColumn.value) return filteredData.value
  
  return [...filteredData.value].sort((a, b) => {
    const aVal = a[sortColumn.value]
    const bVal = b[sortColumn.value]
    const modifier = sortDirection.value === 'asc' ? 1 : -1
    
    if (aVal < bVal) return -1 * modifier
    if (aVal > bVal) return 1 * modifier
    return 0
  })
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * props.pageSize
  const end = start + props.pageSize
  return sortedData.value.slice(start, end)
})

const totalPages = computed(() => 
  Math.ceil(sortedData.value.length / props.pageSize)
)

const sort = (column) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'asc'
  }
  currentPage.value = 1
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

watch(searchQuery, () => {
  currentPage.value = 1
})
</script>""",
        "satisfaction": 8,
        "time_taken": 55.0,
        "task_completed": True,
        "notes": "功能完整的表格組件，使用Vue 3 Composition API，但缺少虛擬滾動優化"
    }
]

def main():
    """演示Manus數據提取流程"""
    print("🎯 Manus歷史數據提取器")
    print("基於1000小時Manus使用經驗")
    print("=" * 50)
    
    extractor = ManusDataExtractor()
    
    # 提取示例數據
    sessions = extractor.extract_from_manus_history(MANUS_SAMPLE_DATA)
    print(f"\n📊 已提取 {len(sessions)} 個Manus會話記錄")
    
    # 轉換為對比數據
    comparison_ids = extractor.convert_to_comparison_data()
    print(f"✅ 已轉換為 {len(comparison_ids)} 個對比記錄")
    
    # 生成K2測試場景
    k2_scenarios = extractor.generate_k2_test_scenarios()
    print(f"🧪 已生成 {len(k2_scenarios)} 個K2測試場景")
    
    # 顯示統計
    from real_time_comparison_tracker import show_stats
    show_stats()
    
    print(f"\n📝 接下來可以:")
    print(f"1. 使用相同prompt測試K2 API")
    print(f"2. 對比質量差異")
    print(f"3. 記錄成本和速度數據")
    print(f"4. 生成最終報告")

if __name__ == "__main__":
    main()
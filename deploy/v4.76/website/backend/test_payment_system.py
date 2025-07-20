#!/usr/bin/env python3
"""
PowerAuto.ai 支付系統測試腳本
測試完整的支付流程：產品展示 -> 結帳 -> 支付 -> 成功頁面
"""

import requests
import json
import time
from datetime import datetime

# 測試配置
BASE_URL = "http://localhost:5001"
TEST_CUSTOMER = {
    "name": "測試用戶",
    "email": "test@powerauto.ai",
    "company": "測試公司",
    "phone": "13800138000",
    "industry": "technology",
    "teamSize": "6-20"
}

def test_api_endpoint(url, method="GET", data=None, description=""):
    """測試API端點"""
    print(f"\n🧪 測試: {description}")
    print(f"   URL: {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        elif method == "PUT":
            response = requests.put(url, json=data, headers={'Content-Type': 'application/json'})
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"   狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 成功")
            try:
                result = response.json()
                if isinstance(result, dict) and len(result) < 10:
                    print(f"   回應: {json.dumps(result, ensure_ascii=False, indent=2)}")
                else:
                    print(f"   回應數據大小: {len(str(result))} 字符")
                return result
            except:
                print(f"   回應: {response.text[:200]}...")
                return response.text
        else:
            print(f"   ❌ 失敗: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("   ❌ 連接失敗 - 請確保服務器正在運行")
        return None
    except Exception as e:
        print(f"   ❌ 錯誤: {e}")
        return None

def test_complete_payment_flow():
    """測試完整支付流程"""
    print("🚀 開始測試 PowerAuto.ai 支付系統")
    print("=" * 60)
    
    # 1. 測試獲取定價方案
    print("\n📋 第一步：獲取定價方案")
    plans = test_api_endpoint(f"{BASE_URL}/api/plans", description="獲取所有定價方案")
    
    if not plans or not plans.get('plans'):
        print("❌ 無法獲取定價方案，測試終止")
        return False
    
    print(f"   可用方案數量: {len(plans['plans'])}")
    for plan in plans['plans']:
        print(f"   - {plan['name']}: ¥{plan['price_monthly']}/月")
    
    # 2. 測試獲取支付方式
    print("\n💳 第二步：獲取支付方式")
    payment_methods = test_api_endpoint(f"{BASE_URL}/api/payment-methods", description="獲取可用支付方式")
    
    if payment_methods and payment_methods.get('payment_methods'):
        print(f"   可用支付方式數量: {len(payment_methods['payment_methods'])}")
        for method in payment_methods['payment_methods']:
            print(f"   - {method['display_name']}: {method['type']}")
    
    # 3. 測試創建訂單
    print("\n📦 第三步：創建訂單")
    order_data = {
        "customer": TEST_CUSTOMER,
        "plan": "professional",
        "billingCycle": "monthly",
        "paymentMethod": "stripe"
    }
    
    order = test_api_endpoint(
        f"{BASE_URL}/api/orders/create",
        method="POST",
        data=order_data,
        description="創建專業版月付訂單"
    )
    
    if not order or not order.get('order_id'):
        print("❌ 無法創建訂單，測試終止")
        return False
    
    order_id = order['order_id']
    print(f"   訂單ID: {order_id}")
    print(f"   金額: ¥{order['amount']}")
    
    # 4. 測試創建支付意圖
    print("\n💰 第四步：創建支付意圖")
    payment_intent = test_api_endpoint(
        f"{BASE_URL}/api/orders/{order_id}/payment-intent",
        method="POST",
        description="為訂單創建支付意圖"
    )
    
    if payment_intent and payment_intent.get('payment_intent'):
        print(f"   支付意圖ID: {payment_intent['payment_intent']['id']}")
    
    # 5. 測試確認支付
    print("\n✅ 第五步：確認支付")
    payment_confirmation = {
        "order_id": order_id,
        "payment_method_id": "pm_test_card_visa",
        "amount": order['amount']
    }
    
    payment_result = test_api_endpoint(
        f"{BASE_URL}/api/payments/confirm",
        method="POST",
        data=payment_confirmation,
        description="確認支付成功"
    )
    
    if payment_result and payment_result.get('success'):
        print(f"   支付成功！訂單狀態: {payment_result.get('status')}")
        if payment_result.get('subscription_id'):
            print(f"   訂閱ID: {payment_result['subscription_id']}")
    
    # 6. 測試獲取訂單狀態
    print("\n📊 第六步：獲取訂單狀態")
    order_status = test_api_endpoint(
        f"{BASE_URL}/api/orders/{order_id}/status",
        description="獲取最新訂單狀態"
    )
    
    if order_status:
        print(f"   訂單狀態: {order_status.get('status')}")
        print(f"   支付狀態: {order_status.get('payment_status')}")
    
    # 7. 測試生成發票
    print("\n📄 第七步：生成發票")
    invoice = test_api_endpoint(
        f"{BASE_URL}/api/orders/{order_id}/invoice",
        description="生成訂單發票"
    )
    
    if invoice and invoice.get('invoice_id'):
        print(f"   發票ID: {invoice['invoice_id']}")
        print(f"   發票狀態: {invoice.get('status')}")
    
    # 8. 測試企業詢價
    print("\n🏢 第八步：測試企業詢價")
    enterprise_quote = {
        "company": "大型科技公司",
        "email": "enterprise@example.com",
        "phone": "400-888-0123",
        "teamSize": "100+",
        "requirements": "需要私有部署和定制功能"
    }
    
    quote_result = test_api_endpoint(
        f"{BASE_URL}/api/enterprise/quote",
        method="POST",
        data=enterprise_quote,
        description="提交企業版詢價"
    )
    
    if quote_result and quote_result.get('quote_id'):
        print(f"   詢價ID: {quote_result['quote_id']}")
        print(f"   預估回復時間: {quote_result.get('estimated_response_time')}")
    
    print("\n🎉 支付系統測試完成！")
    print("=" * 60)
    
    # 測試結果總結
    success_count = sum([
        plans is not None,
        payment_methods is not None,
        order is not None,
        payment_intent is not None,
        payment_result and payment_result.get('success'),
        order_status is not None,
        invoice is not None,
        quote_result is not None
    ])
    
    print(f"測試結果: {success_count}/8 項測試通過")
    
    if success_count >= 6:
        print("✅ 支付系統基本功能正常")
        return True
    else:
        print("❌ 支付系統存在問題，需要檢查")
        return False

def test_frontend_pages():
    """測試前端頁面"""
    print("\n🌐 測試前端頁面")
    print("-" * 40)
    
    pages = [
        ("/products", "產品展示頁面"),
        ("/checkout?plan=professional", "結帳頁面"),
        ("/success?order_id=test123", "支付成功頁面"),
        ("/register?plan=personal", "註冊頁面")
    ]
    
    for path, name in pages:
        response = test_api_endpoint(f"{BASE_URL}{path}", description=f"訪問{name}")
        if response:
            if isinstance(response, str) and "<!DOCTYPE html>" in response:
                print(f"   ✅ HTML頁面正常載入")
            else:
                print(f"   ⚠️  頁面內容可能不完整")

if __name__ == "__main__":
    print("🧪 PowerAuto.ai 支付系統完整測試")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目標服務器: {BASE_URL}")
    
    # 首先檢查服務器是否運行
    print("\n🔍 檢查服務器狀態...")
    health_check = test_api_endpoint(f"{BASE_URL}/api/plans", description="服務器健康檢查")
    
    if health_check is None:
        print("\n❌ 服務器未運行或無法訪問")
        print("請確保運行以下命令啟動服務器：")
        print("cd /Users/alexchuang/alexchuangtest/aicore0720/deploy/v4.76/website/backend")
        print("python app.py")
        exit(1)
    
    print("✅ 服務器正在運行")
    
    # 執行完整測試
    try:
        api_success = test_complete_payment_flow()
        test_frontend_pages()
        
        print(f"\n📋 測試完成於: {datetime.now().strftime('%H:%M:%S')}")
        
        if api_success:
            print("🎉 支付系統測試通過！可以開始使用。")
        else:
            print("⚠️  支付系統存在問題，請檢查日誌。")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  測試被用戶中斷")
    except Exception as e:
        print(f"\n❌ 測試過程中出現錯誤: {e}")
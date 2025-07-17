#!/usr/bin/env python3
"""
UI 规格书合规性测试套件
测试 PowerAutomation v4.6.9.6 是否完全遵循 UI_DESIGN_GUIDE_v4.6.9.6.md 规范
"""

import unittest
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class UISpecificationComplianceTests(unittest.TestCase):
    """UI 规格书合规性测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.wait = WebDriverWait(cls.driver, 10)
        cls.base_url = "http://127.0.0.1:5176"
        
        # 测试结果记录
        cls.test_results = {
            "ui_compliance": {},
            "layout_structure": {},
            "component_functionality": {},
            "responsive_design": {}
        }
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        # 保存测试结果
        os.makedirs('/home/ubuntu/aicore0716/tests/results', exist_ok=True)
        with open('/home/ubuntu/aicore0716/tests/results/ui_compliance_results.json', 'w', encoding='utf-8') as f:
            json.dump(cls.test_results, f, ensure_ascii=False, indent=2)
        
        cls.driver.quit()
    
    def setUp(self):
        """每个测试前的准备"""
        self.driver.get(self.base_url)
        time.sleep(2)
    
    def test_01_three_column_layout_structure(self):
        """测试三栏布局结构是否符合规格书要求"""
        print("\n🔍 测试三栏布局结构...")
        
        try:
            # 检查左侧仪表盘 (300px)
            left_panel = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "sidebar-left"))
            )
            left_width = left_panel.size['width']
            self.assertGreaterEqual(left_width, 280, "左侧面板宽度应该接近300px")
            self.assertLessEqual(left_width, 320, "左侧面板宽度不应超过320px")
            
            # 检查中间工作区 (自适应)
            main_content = self.driver.find_element(By.CLASS_NAME, "main-content")
            self.assertTrue(main_content.is_displayed(), "中间工作区应该可见")
            
            # 检查右侧AI助手 (350px)
            right_panel = self.driver.find_element(By.CLASS_NAME, "sidebar-right")
            right_width = right_panel.size['width']
            self.assertGreaterEqual(right_width, 330, "右侧面板宽度应该接近350px")
            self.assertLessEqual(right_width, 420, "右侧面板宽度不应超过420px")
            
            self.test_results["layout_structure"]["three_column_layout"] = {
                "status": "PASS",
                "left_width": left_width,
                "right_width": right_width,
                "message": "三栏布局结构符合规格书要求"
            }
            
        except Exception as e:
            self.test_results["layout_structure"]["three_column_layout"] = {
                "status": "FAIL",
                "error": str(e),
                "message": "三栏布局结构不符合规格书要求"
            }
            self.fail(f"三栏布局测试失败: {e}")
    
    def test_02_left_dashboard_components(self):
        """测试左侧仪表盘组件是否符合规格书要求"""
        print("\n🔍 测试左侧仪表盘组件...")
        
        required_sections = [
            "🚀 快速操作区",
            "📈 系统状态", 
            "🔄 工作流状态"
        ]
        
        missing_sections = []
        found_sections = []
        
        try:
            for section in required_sections:
                try:
                    section_element = self.driver.find_element(
                        By.XPATH, f"//*[contains(text(), '{section}')]"
                    )
                    if section_element.is_displayed():
                        found_sections.append(section)
                    else:
                        missing_sections.append(section)
                except:
                    missing_sections.append(section)
            
            self.test_results["ui_compliance"]["left_dashboard"] = {
                "status": "PASS" if not missing_sections else "PARTIAL",
                "found_sections": found_sections,
                "missing_sections": missing_sections,
                "compliance_rate": f"{len(found_sections)}/{len(required_sections)}"
            }
            
        except Exception as e:
            self.test_results["ui_compliance"]["left_dashboard"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.fail(f"左侧仪表盘测试失败: {e}")
    
    def test_03_ag_ui_smartui_integration(self):
        """测试 AG-UI 和 SmartUI 功能集成"""
        print("\n🔍 测试 AG-UI 和 SmartUI 功能集成...")
        
        try:
            # 测试 AG-UI 按钮
            ag_ui_btn = self.driver.find_element(
                By.XPATH, "//*[contains(text(), '生成AG-UI组件')]"
            )
            self.assertTrue(ag_ui_btn.is_displayed(), "AG-UI 按钮应该可见")
            
            # 测试 SmartUI 按钮
            smartui_btn = self.driver.find_element(
                By.XPATH, "//*[contains(text(), '创建SmartUI布局')]"
            )
            self.assertTrue(smartui_btn.is_displayed(), "SmartUI 按钮应该可见")
            
            self.test_results["component_functionality"]["ag_ui_smartui"] = {
                "status": "PASS",
                "ag_ui_available": True,
                "smartui_available": True,
                "message": "AG-UI 和 SmartUI 功能正常集成"
            }
            
        except Exception as e:
            self.test_results["component_functionality"]["ag_ui_smartui"] = {
                "status": "FAIL",
                "error": str(e)
            }
            self.fail(f"AG-UI 和 SmartUI 集成测试失败: {e}")

if __name__ == '__main__':
    # 创建测试结果目录
    os.makedirs('/home/ubuntu/aicore0716/tests/results', exist_ok=True)
    
    # 运行测试
    unittest.main(verbosity=2)


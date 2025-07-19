"""
UI生成工具
基于需求描述智能生成UI组件和界面
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class UIGenerationTool:
    """UI生成工具类"""
    
    def __init__(self):
        """初始化UI生成工具"""
        self.templates = {
            "react": {
                "modern": self._generate_modern_react,
                "classic": self._generate_classic_react,
                "minimal": self._generate_minimal_react,
                "material": self._generate_material_react,
                "tailwind": self._generate_tailwind_react
            },
            "vue": {
                "modern": self._generate_modern_vue,
                "classic": self._generate_classic_vue,
                "minimal": self._generate_minimal_vue
            },
            "html": {
                "modern": self._generate_modern_html,
                "classic": self._generate_classic_html,
                "minimal": self._generate_minimal_html
            }
        }
    
    async def generate(self, description: str, framework: str = "react", 
                      style: str = "modern", responsive: bool = True) -> str:
        """
        生成UI组件
        
        Args:
            description: UI需求描述
            framework: UI框架
            style: 样式风格
            responsive: 是否响应式
            
        Returns:
            生成的UI代码
        """
        try:
            logger.info(f"🎨 生成UI: {framework} - {style}")
            
            # 获取生成器函数
            if framework in self.templates and style in self.templates[framework]:
                generator = self.templates[framework][style]
                result = await generator(description, responsive)
                return result
            else:
                # 默认生成器
                return await self._generate_default_ui(description, framework, style, responsive)
                
        except Exception as e:
            logger.error(f"❌ UI生成失败: {e}")
            return f"❌ UI生成失败: {str(e)}"
    
    async def _generate_modern_react(self, description: str, responsive: bool = True) -> str:
        """生成现代风格的React组件"""
        responsive_classes = "responsive" if responsive else ""
        
        return f'''import React from 'react';
import './ModernComponent.css';

const ModernComponent = () => {{
  return (
    <div className="modern-container {responsive_classes}">
      <header className="modern-header">
        <h1>Generated UI Component</h1>
        <p>{description}</p>
      </header>
      
      <main className="modern-main">
        <div className="content-section">
          <h2>Main Content</h2>
          <p>This component was generated based on: {description}</p>
          
          <div className="action-buttons">
            <button className="btn-primary">Primary Action</button>
            <button className="btn-secondary">Secondary Action</button>
          </div>
        </div>
      </main>
      
      <footer className="modern-footer">
        <p>Generated with PowerAutomation UI Generator</p>
      </footer>
    </div>
  );
}};

export default ModernComponent;

/* CSS Styles */
.modern-container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}}

.modern-header {{
  text-align: center;
  margin-bottom: 30px;
  color: white;
}}

.modern-header h1 {{
  font-size: 2.5em;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}}

.modern-main {{
  background: white;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 20px;
}}

.content-section h2 {{
  color: #333;
  margin-bottom: 15px;
}}

.action-buttons {{
  display: flex;
  gap: 15px;
  margin-top: 20px;
}}

.btn-primary {{
  background: #667eea;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
}}

.btn-primary:hover {{
  background: #5a6fd8;
  transform: translateY(-2px);
}}

.btn-secondary {{
  background: #e2e8f0;
  color: #4a5568;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
}}

.btn-secondary:hover {{
  background: #cbd5e0;
}}

.modern-footer {{
  text-align: center;
  color: white;
  opacity: 0.8;
}}

{"@media (max-width: 768px) {" if responsive else ""}
{".modern-container {" if responsive else ""}
{"  padding: 10px;" if responsive else ""}
{"}" if responsive else ""}

{".action-buttons {" if responsive else ""}
{"  flex-direction: column;" if responsive else ""}
{"}" if responsive else ""}
{"}" if responsive else ""}'''
    
    async def _generate_tailwind_react(self, description: str, responsive: bool = True) -> str:
        """生成Tailwind CSS风格的React组件"""
        responsive_classes = "sm:px-6 lg:px-8" if responsive else "px-4"
        
        return f'''import React from 'react';

const TailwindComponent = () => {{
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 {responsive_classes}">
      <div className="max-w-4xl mx-auto py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
            Generated UI Component
          </h1>
          <p className="text-xl text-blue-100 max-w-2xl mx-auto">
            {description}
          </p>
        </header>
        
        <main className="bg-white rounded-2xl shadow-2xl p-8 md:p-12 mb-8">
          <div className="space-y-6">
            <h2 className="text-3xl font-semibold text-gray-800 mb-6">
              Main Content
            </h2>
            
            <p className="text-gray-600 leading-relaxed">
              This component was generated based on: {description}
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-2">Feature 1</h3>
                <p className="text-gray-600">Description of feature 1</p>
              </div>
              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-2">Feature 2</h3>
                <p className="text-gray-600">Description of feature 2</p>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 mt-8">
              <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex-1 sm:flex-none">
                Primary Action
              </button>
              <button className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex-1 sm:flex-none">
                Secondary Action
              </button>
            </div>
          </div>
        </main>
        
        <footer className="text-center text-white opacity-75">
          <p>Generated with PowerAutomation UI Generator</p>
        </footer>
      </div>
    </div>
  );
}};

export default TailwindComponent;'''
    
    async def _generate_modern_vue(self, description: str, responsive: bool = True) -> str:
        """生成现代风格的Vue组件"""
        return f'''<template>
  <div class="modern-container" :class="{{ responsive: isResponsive }}">
    <header class="modern-header">
      <h1>Generated UI Component</h1>
      <p>{description}</p>
    </header>
    
    <main class="modern-main">
      <div class="content-section">
        <h2>Main Content</h2>
        <p>This component was generated based on: {description}</p>
        
        <div class="action-buttons">
          <button class="btn-primary" @click="primaryAction">Primary Action</button>
          <button class="btn-secondary" @click="secondaryAction">Secondary Action</button>
        </div>
      </div>
    </main>
    
    <footer class="modern-footer">
      <p>Generated with PowerAutomation UI Generator</p>
    </footer>
  </div>
</template>

<script>
export default {{
  name: 'ModernComponent',
  data() {{
    return {{
      isResponsive: {str(responsive).lower()}
    }}
  }},
  methods: {{
    primaryAction() {{
      console.log('Primary action clicked');
    }},
    secondaryAction() {{
      console.log('Secondary action clicked');
    }}
  }}
}}
</script>

<style scoped>
.modern-container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}}

.modern-header {{
  text-align: center;
  margin-bottom: 30px;
  color: white;
}}

.modern-header h1 {{
  font-size: 2.5em;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}}

.modern-main {{
  background: white;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 20px;
}}

.action-buttons {{
  display: flex;
  gap: 15px;
  margin-top: 20px;
}}

.btn-primary {{
  background: #667eea;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
}}

.btn-primary:hover {{
  background: #5a6fd8;
  transform: translateY(-2px);
}}

.btn-secondary {{
  background: #e2e8f0;
  color: #4a5568;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
}}

.responsive .action-buttons {{
  flex-direction: column;
}}

@media (max-width: 768px) {{
  .responsive .modern-container {{
    padding: 10px;
  }}
}}
</style>'''
    
    async def _generate_modern_html(self, description: str, responsive: bool = True) -> str:
        """生成现代风格的HTML页面"""
        responsive_meta = '<meta name="viewport" content="width=device-width, initial-scale=1.0">' if responsive else ""
        responsive_css = """
@media (max-width: 768px) {
  .modern-container {
    padding: 10px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
""" if responsive else ""
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    {responsive_meta}
    <title>Generated UI Component</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }}
        
        .modern-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .modern-header {{
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }}
        
        .modern-header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .modern-main {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .content-section h2 {{
            color: #333;
            margin-bottom: 15px;
        }}
        
        .action-buttons {{
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }}
        
        .btn-primary {{
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }}
        
        .btn-primary:hover {{
            background: #5a6fd8;
            transform: translateY(-2px);
        }}
        
        .btn-secondary {{
            background: #e2e8f0;
            color: #4a5568;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }}
        
        .btn-secondary:hover {{
            background: #cbd5e0;
        }}
        
        .modern-footer {{
            text-align: center;
            color: white;
            opacity: 0.8;
        }}
        
        {responsive_css}
    </style>
</head>
<body>
    <div class="modern-container">
        <header class="modern-header">
            <h1>Generated UI Component</h1>
            <p>{description}</p>
        </header>
        
        <main class="modern-main">
            <div class="content-section">
                <h2>Main Content</h2>
                <p>This component was generated based on: {description}</p>
                
                <div class="action-buttons">
                    <button class="btn-primary" onclick="primaryAction()">Primary Action</button>
                    <button class="btn-secondary" onclick="secondaryAction()">Secondary Action</button>
                </div>
            </div>
        </main>
        
        <footer class="modern-footer">
            <p>Generated with PowerAutomation UI Generator</p>
        </footer>
    </div>
    
    <script>
        function primaryAction() {{
            alert('Primary action clicked!');
        }}
        
        function secondaryAction() {{
            alert('Secondary action clicked!');
        }}
    </script>
</body>
</html>'''
    
    async def _generate_default_ui(self, description: str, framework: str, 
                                  style: str, responsive: bool = True) -> str:
        """默认UI生成器"""
        return f'''// {framework.upper()} Component - {style.title()} Style
// Generated based on: {description}

const GeneratedComponent = () => {{
  return (
    <div className="generated-component">
      <h1>Generated UI Component</h1>
      <p>Framework: {framework}</p>
      <p>Style: {style}</p>
      <p>Responsive: {responsive}</p>
      <p>Description: {description}</p>
      
      <div className="actions">
        <button>Primary Action</button>
        <button>Secondary Action</button>
      </div>
    </div>
  );
}};

export default GeneratedComponent;'''
    
    # 其他生成器的基础实现
    async def _generate_classic_react(self, description: str, responsive: bool = True) -> str:
        return await self._generate_default_ui(description, "react", "classic", responsive)
    
    async def _generate_minimal_react(self, description: str, responsive: bool = True) -> str:
        return await self._generate_default_ui(description, "react", "minimal", responsive)
    
    async def _generate_material_react(self, description: str, responsive: bool = True) -> str:
        return await self._generate_default_ui(description, "react", "material", responsive)
    
    async def _generate_classic_vue(self, description: str, responsive: bool = True) -> str:
        return await self._generate_default_ui(description, "vue", "classic", responsive)
    
    async def _generate_minimal_vue(self, description: str, responsive: bool = True) -> str:
        return await self._generate_default_ui(description, "vue", "minimal", responsive)
    
    async def _generate_classic_html(self, description: str, responsive: bool = True) -> str:
        return await self._generate_default_ui(description, "html", "classic", responsive)
    
    async def _generate_minimal_html(self, description: str, responsive: bool = True) -> str:
        return await self._generate_default_ui(description, "html", "minimal", responsive)
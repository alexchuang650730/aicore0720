#!/usr/bin/env python3
"""
PowerAutomation Beta開發者計劃
為100名測試用戶提供限時免費開發者權限
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class BetaDeveloper:
    """Beta開發者信息"""
    user_id: str
    email: str
    name: str
    invite_code: str
    developer_level: str  # core, early, professional, community
    granted_at: datetime
    expires_at: datetime
    permissions: List[str]
    usage_limits: Dict[str, int]
    status: str  # active, expired, suspended

class BetaDeveloperProgram:
    """Beta開發者計劃管理"""
    
    def __init__(self):
        self.program_config = self._create_program_config()
        self.landing_page_config = self._create_landing_page_config()
        
    def _create_program_config(self) -> Dict[str, Any]:
        """創建Beta開發者計劃配置"""
        
        return {
            "program_info": {
                "name": "PowerAutomation Beta開發者計劃",
                "description": "加入革命性的Claude Code Tool增強平台開發",
                "duration_days": 60,  # 2個月免費期
                "total_slots": 100,
                "launch_date": "2025-07-25",
                "registration_deadline": "2025-07-31"
            },
            "developer_tiers": {
                "core": {
                    "name": "核心開發者",
                    "slots": 10,
                    "description": "技術專家，深度參與產品設計",
                    "permissions": [
                        "full_platform_access",
                        "unlimited_claude_requests",
                        "unlimited_k2_requests", 
                        "advanced_analytics",
                        "api_access",
                        "feature_preview",
                        "direct_feedback_channel",
                        "product_roadmap_input"
                    ],
                    "usage_limits": {
                        "daily_requests": -1,  # unlimited
                        "concurrent_sessions": 10,
                        "data_export": -1,
                        "custom_workflows": -1
                    },
                    "special_benefits": [
                        "專屬技術支持群",
                        "每週產品會議參與",
                        "優先feature request處理",
                        "終身50%折扣"
                    ]
                },
                "early": {
                    "name": "早期採用者",
                    "slots": 25,
                    "description": "活躍開發者，積極測試新功能",
                    "permissions": [
                        "full_platform_access",
                        "high_quota_requests",
                        "basic_analytics",
                        "beta_features",
                        "community_feedback"
                    ],
                    "usage_limits": {
                        "daily_requests": 1000,
                        "concurrent_sessions": 5,
                        "data_export": 100,
                        "custom_workflows": 10
                    },
                    "special_benefits": [
                        "Beta功能搶先體驗",
                        "月度反饋會議",
                        "正式版30%折扣"
                    ]
                },
                "professional": {
                    "name": "專業開發者",
                    "slots": 35,
                    "description": "專業團隊，評估企業使用",
                    "permissions": [
                        "standard_platform_access",
                        "team_collaboration",
                        "usage_analytics",
                        "integration_tools"
                    ],
                    "usage_limits": {
                        "daily_requests": 500,
                        "concurrent_sessions": 3,
                        "data_export": 50,
                        "custom_workflows": 5
                    },
                    "special_benefits": [
                        "團隊協作功能",
                        "企業級支持",
                        "正式版20%折扣"
                    ]
                },
                "community": {
                    "name": "社群開發者",
                    "slots": 30,
                    "description": "社群成員，體驗核心功能",
                    "permissions": [
                        "basic_platform_access",
                        "community_features",
                        "basic_analytics"
                    ],
                    "usage_limits": {
                        "daily_requests": 200,
                        "concurrent_sessions": 2,
                        "data_export": 20,
                        "custom_workflows": 3
                    },
                    "special_benefits": [
                        "社群專屬內容",
                        "正式版10%折扣"
                    ]
                }
            },
            "application_process": {
                "requirements": {
                    "core": [
                        "5年以上開發經驗",
                        "有AI工具深度使用經驗",
                        "願意提供詳細技術反饋",
                        "參與產品設計討論"
                    ],
                    "early": [
                        "3年以上開發經驗", 
                        "有代碼助手使用經驗",
                        "積極測試新功能"
                    ],
                    "professional": [
                        "團隊開發背景",
                        "企業環境使用需求",
                        "評估商業應用場景"
                    ],
                    "community": [
                        "基本編程經驗",
                        "對AI工具感興趣",
                        "願意分享使用體驗"
                    ]
                },
                "selection_criteria": [
                    "技術背景匹配度",
                    "使用場景多樣性",
                    "反饋質量潛力",
                    "推廣影響力",
                    "長期合作意願"
                ]
            }
        }
    
    def _create_landing_page_config(self) -> Dict[str, Any]:
        """創建Beta開發者計劃登陸頁配置"""
        
        return {
            "hero_section": {
                "headline": "加入PowerAutomation Beta開發者計劃",
                "subheadline": "成為革命性Claude Code Tool增強平台的共同創造者",
                "cta_primary": "立即申請開發者權限",
                "cta_secondary": "了解更多詳情",
                "hero_image": "developer_program_hero.png",
                "key_stats": [
                    "100個限量名額",
                    "60天免費使用",
                    "無限Claude+K2對比",
                    "專屬開發者權限"
                ]
            },
            "value_proposition": {
                "title": "為什麼選擇成為Beta開發者？",
                "benefits": [
                    {
                        "icon": "🚀",
                        "title": "搶先體驗",
                        "description": "最先體驗PowerAutomation的完整功能，包括Claude+K2智能路由"
                    },
                    {
                        "icon": "💰", 
                        "title": "免費使用",
                        "description": "60天完全免費使用，價值$299的Professional功能"
                    },
                    {
                        "icon": "🎯",
                        "title": "影響產品",
                        "description": "直接參與產品設計，你的反饋將影響數萬開發者的工具"
                    },
                    {
                        "icon": "🏆",
                        "title": "開發者身份",
                        "description": "獲得官方開發者認證，專屬權限和社群access"
                    }
                ]
            },
            "program_tiers": {
                "title": "開發者等級與權限",
                "description": "根據你的經驗和參與度，獲得相應的開發者權限",
                "tiers_display": [
                    {
                        "name": "核心開發者",
                        "badge": "CORE",
                        "color": "#FF6B35",
                        "spots": "10個名額",
                        "features": [
                            "無限制使用所有功能",
                            "API訪問權限",
                            "產品路線圖參與",
                            "專屬技術支持",
                            "終身50%折扣"
                        ],
                        "requirements": "5年+經驗，AI工具專家"
                    },
                    {
                        "name": "早期採用者", 
                        "badge": "EARLY",
                        "color": "#4ECDC4",
                        "spots": "25個名額",
                        "features": [
                            "高配額使用限制",
                            "Beta功能搶先體驗",
                            "月度反饋會議",
                            "正式版30%折扣"
                        ],
                        "requirements": "3年+經驗，活躍開發者"
                    },
                    {
                        "name": "專業開發者",
                        "badge": "PRO", 
                        "color": "#45B7D1",
                        "spots": "35個名額",
                        "features": [
                            "團隊協作功能",
                            "企業級支持",
                            "使用分析報告",
                            "正式版20%折扣"
                        ],
                        "requirements": "團隊背景，企業需求"
                    },
                    {
                        "name": "社群開發者",
                        "badge": "COMMUNITY",
                        "color": "#96CEB4", 
                        "spots": "30個名額",
                        "features": [
                            "核心功能訪問",
                            "社群專屬內容",
                            "基礎分析工具",
                            "正式版10%折扣"
                        ],
                        "requirements": "基礎經驗，學習意願"
                    }
                ]
            },
            "application_form": {
                "title": "申請Beta開發者權限",
                "fields": [
                    {
                        "name": "email",
                        "type": "email",
                        "label": "郵箱地址",
                        "required": True,
                        "placeholder": "your@email.com"
                    },
                    {
                        "name": "name",
                        "type": "text", 
                        "label": "姓名",
                        "required": True,
                        "placeholder": "張小明"
                    },
                    {
                        "name": "github",
                        "type": "url",
                        "label": "GitHub Profile",
                        "required": False,
                        "placeholder": "https://github.com/username"
                    },
                    {
                        "name": "experience_years",
                        "type": "select",
                        "label": "開發經驗",
                        "required": True,
                        "options": [
                            "1-2年",
                            "3-5年", 
                            "5-10年",
                            "10年以上"
                        ]
                    },
                    {
                        "name": "primary_stack",
                        "type": "multiselect",
                        "label": "主要技術棧",
                        "required": True,
                        "options": [
                            "Python",
                            "JavaScript/TypeScript",
                            "Java",
                            "Go",
                            "Rust",
                            "C/C++",
                            "其他"
                        ]
                    },
                    {
                        "name": "ai_tools_experience",
                        "type": "multiselect",
                        "label": "AI工具使用經驗",
                        "required": True,
                        "options": [
                            "GitHub Copilot",
                            "Claude Code Tool",
                            "Manus",
                            "Cursor",
                            "其他"
                        ]
                    },
                    {
                        "name": "preferred_tier",
                        "type": "select",
                        "label": "期望開發者等級",
                        "required": True,
                        "options": [
                            "核心開發者",
                            "早期採用者",
                            "專業開發者", 
                            "社群開發者"
                        ]
                    },
                    {
                        "name": "use_cases",
                        "type": "textarea",
                        "label": "主要使用場景",
                        "required": True,
                        "placeholder": "描述你計劃如何使用PowerAutomation，以及期望解決的問題..."
                    },
                    {
                        "name": "feedback_commitment",
                        "type": "checkbox",
                        "label": "我承諾積極提供使用反饋和建議",
                        "required": True
                    },
                    {
                        "name": "daily_usage_estimate",
                        "type": "select",
                        "label": "預計每日使用時間",
                        "required": True,
                        "options": [
                            "30分鐘以下",
                            "30分鐘-1小時",
                            "1-3小時",
                            "3小時以上"
                        ]
                    }
                ]
            },
            "testimonials": {
                "title": "開發者早期反饋",
                "items": [
                    {
                        "name": "李小明",
                        "role": "資深前端工程師",
                        "company": "某知名互聯網公司",
                        "avatar": "testimonial_1.jpg",
                        "content": "PowerAutomation的Claude+K2智能路由真的很棒，既保證了代碼質量又大幅降低了成本。作為Beta開發者，我能直接影響產品發展方向。"
                    },
                    {
                        "name": "王小華",
                        "role": "全棧開發者",
                        "company": "創業公司CTO",
                        "avatar": "testimonial_2.jpg", 
                        "content": "60天免費使用期讓我們團隊充分評估了PowerAutomation。現在我們已經決定在正式版發布後立即購買企業版。"
                    },
                    {
                        "name": "陳小美",
                        "role": "AI研究工程師",
                        "company": "AI實驗室",
                        "avatar": "testimonial_3.jpg",
                        "content": "作為核心開發者，我參與了多個關鍵功能的設計討論。看到自己的建議被實現的感覺很棒！"
                    }
                ]
            },
            "faq": {
                "title": "常見問題",
                "items": [
                    {
                        "question": "Beta開發者計劃是完全免費的嗎？",
                        "answer": "是的，60天完全免費使用，包括所有開發者權限功能。無需信用卡，無隱藏費用。"
                    },
                    {
                        "question": "如何獲得更高等級的開發者權限？",
                        "answer": "根據你的技術背景、使用頻率和反饋質量，我們會邀請表現優秀的開發者升級到更高等級。"
                    },
                    {
                        "question": "Beta期結束後會發生什麼？",
                        "answer": "Beta開發者將獲得正式版的專屬折扣，並優先獲得新功能訪問權限。"
                    },
                    {
                        "question": "我的數據和代碼安全嗎？",
                        "answer": "我們採用企業級安全標準，所有數據傳輸加密，代碼片段不會被存儲或分享。"
                    },
                    {
                        "question": "可以邀請團隊成員加入嗎？",
                        "answer": "專業開發者和核心開發者可以邀請有限數量的團隊成員加入測試。"
                    }
                ]
            },
            "footer_cta": {
                "title": "立即加入Beta開發者計劃",
                "subtitle": "100個名額，先到先得",
                "cta_button": "申請開發者權限",
                "urgency_text": "限時開放：2025年7月31日截止申請"
            }
        }
    
    def generate_invite_code(self, tier: str, sequence: int) -> str:
        """生成邀請碼"""
        tier_prefixes = {
            "core": "CORE",
            "early": "EARLY", 
            "professional": "PRO",
            "community": "COMM"
        }
        
        prefix = tier_prefixes.get(tier, "BETA")
        return f"{prefix}-{sequence:04d}-2025"
    
    def create_developer_onboarding(self, tier: str) -> Dict[str, Any]:
        """創建開發者入職流程"""
        
        base_onboarding = [
            {
                "step": 1,
                "title": "歡迎成為Beta開發者",
                "description": "觀看5分鐘產品介紹視頻",
                "action": "watch_intro_video",
                "estimated_time": "5分鐘"
            },
            {
                "step": 2,
                "title": "設置開發環境",
                "description": "配置Claude Code Tool集成",
                "action": "setup_claude_integration",
                "estimated_time": "10分鐘"
            },
            {
                "step": 3,
                "title": "第一次對比測試",
                "description": "體驗Claude vs K2智能路由",
                "action": "first_comparison_test",
                "estimated_time": "15分鐘"
            },
            {
                "step": 4,
                "title": "加入開發者社群",
                "description": "加入專屬討論群組",
                "action": "join_developer_community",
                "estimated_time": "2分鐘"
            },
            {
                "step": 5,
                "title": "設置反饋偏好",
                "description": "配置如何提供反饋",
                "action": "setup_feedback_preferences", 
                "estimated_time": "5分鐘"
            }
        ]
        
        tier_specific = {
            "core": [
                {
                    "step": 6,
                    "title": "API訪問設置",
                    "description": "獲取API密鑰和文檔",
                    "action": "setup_api_access",
                    "estimated_time": "10分鐘"
                },
                {
                    "step": 7,
                    "title": "產品路線圖介紹",
                    "description": "了解產品發展計劃",
                    "action": "review_product_roadmap",
                    "estimated_time": "15分鐘"
                }
            ],
            "early": [
                {
                    "step": 6,
                    "title": "Beta功能預覽",
                    "description": "體驗即將發布的新功能",
                    "action": "preview_beta_features",
                    "estimated_time": "10分鐘"
                }
            ],
            "professional": [
                {
                    "step": 6,
                    "title": "團隊協作設置",
                    "description": "邀請團隊成員並設置權限",
                    "action": "setup_team_collaboration",
                    "estimated_time": "15分鐘"
                }
            ],
            "community": []
        }
        
        return {
            "tier": tier,
            "steps": base_onboarding + tier_specific.get(tier, []),
            "total_estimated_time": "40-60分鐘",
            "completion_reward": "開發者徽章 + 專屬權限激活"
        }
    
    def generate_landing_page_html(self) -> str:
        """生成Beta開發者計劃登陸頁HTML"""
        
        config = self.landing_page_config
        
        html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config["hero_section"]["headline"]} | PowerAutomation</title>
    <meta name="description" content="{config["hero_section"]["subheadline"]}">
    
    <!-- CSS Framework -->
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <style>
        .gradient-bg {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .tier-card {{
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .tier-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }}
        .core-badge {{ background-color: #FF6B35; }}
        .early-badge {{ background-color: #4ECDC4; }}
        .pro-badge {{ background-color: #45B7D1; }}
        .community-badge {{ background-color: #96CEB4; }}
    </style>
</head>
<body class="bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center">
                    <img src="/static/logo.png" alt="PowerAutomation" class="h-8 w-auto">
                    <span class="ml-2 text-xl font-bold text-gray-900">PowerAutomation</span>
                </div>
                <nav class="hidden md:flex space-x-8">
                    <a href="#program" class="text-gray-700 hover:text-indigo-600">計劃詳情</a>
                    <a href="#tiers" class="text-gray-700 hover:text-indigo-600">開發者等級</a>
                    <a href="#apply" class="text-gray-700 hover:text-indigo-600">立即申請</a>
                </nav>
                <button class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">
                    登錄
                </button>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="gradient-bg text-white py-20">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center">
                <h1 class="text-5xl font-bold mb-6">
                    {config["hero_section"]["headline"]}
                </h1>
                <p class="text-xl mb-8 max-w-3xl mx-auto">
                    {config["hero_section"]["subheadline"]}
                </p>
                
                <!-- Key Stats -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <div class="bg-white bg-opacity-20 rounded-lg p-4">
                        <div class="text-2xl font-bold">100</div>
                        <div class="text-sm">限量名額</div>
                    </div>
                    <div class="bg-white bg-opacity-20 rounded-lg p-4">
                        <div class="text-2xl font-bold">60天</div>
                        <div class="text-sm">免費使用</div>
                    </div>
                    <div class="bg-white bg-opacity-20 rounded-lg p-4">
                        <div class="text-2xl font-bold">無限</div>
                        <div class="text-sm">Claude+K2對比</div>
                    </div>
                    <div class="bg-white bg-opacity-20 rounded-lg p-4">
                        <div class="text-2xl font-bold">專屬</div>
                        <div class="text-sm">開發者權限</div>
                    </div>
                </div>
                
                <div class="space-x-4">
                    <button class="bg-white text-indigo-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 text-lg">
                        {config["hero_section"]["cta_primary"]}
                    </button>
                    <button class="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-indigo-600">
                        {config["hero_section"]["cta_secondary"]}
                    </button>
                </div>
            </div>
        </div>
    </section>

    <!-- Value Proposition -->
    <section id="program" class="py-20 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16">
                <h2 class="text-4xl font-bold text-gray-900 mb-4">
                    {config["value_proposition"]["title"]}
                </h2>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">'''

        # Add benefits
        for benefit in config["value_proposition"]["benefits"]:
            html += f'''
                <div class="text-center">
                    <div class="text-4xl mb-4">{benefit["icon"]}</div>
                    <h3 class="text-xl font-semibold mb-2">{benefit["title"]}</h3>
                    <p class="text-gray-600">{benefit["description"]}</p>
                </div>'''

        html += '''
            </div>
        </div>
    </section>

    <!-- Developer Tiers -->
    <section id="tiers" class="py-20 bg-gray-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16">
                <h2 class="text-4xl font-bold text-gray-900 mb-4">
                    開發者等級與權限
                </h2>
                <p class="text-xl text-gray-600">
                    根據你的經驗和參與度，獲得相應的開發者權限
                </p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">'''

        # Add tier cards
        for tier in config["program_tiers"]["tiers_display"]:
            badge_class = tier["name"].lower().replace("開發者", "").replace("早期採用者", "early").replace("專業", "pro").replace("社群", "community").replace("核心", "core") + "-badge"
            
            html += f'''
                <div class="tier-card bg-white rounded-xl shadow-lg p-6 relative">
                    <div class="text-center">
                        <span class="badge {badge_class}">{tier["badge"]}</span>
                        <h3 class="text-xl font-bold mt-4 mb-2">{tier["name"]}</h3>
                        <p class="text-sm text-gray-600 mb-4">{tier["spots"]}</p>
                        
                        <div class="space-y-3 mb-6">'''
            
            for feature in tier["features"]:
                html += f'''
                            <div class="flex items-center text-sm">
                                <i class="fas fa-check text-green-500 mr-2"></i>
                                <span>{feature}</span>
                            </div>'''
            
            html += f'''
                        </div>
                        
                        <div class="border-t pt-4">
                            <p class="text-xs text-gray-500">{tier["requirements"]}</p>
                        </div>
                    </div>
                </div>'''

        html += '''
            </div>
        </div>
    </section>

    <!-- Application Form -->
    <section id="apply" class="py-20 bg-white">
        <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-12">
                <h2 class="text-4xl font-bold text-gray-900 mb-4">
                    申請Beta開發者權限
                </h2>
                <p class="text-xl text-gray-600">
                    填寫申請表，我們將在24小時內回覆
                </p>
            </div>
            
            <form class="bg-white shadow-xl rounded-lg p-8">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">郵箱地址 *</label>
                        <input type="email" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="your@email.com" required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">姓名 *</label>
                        <input type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="張小明" required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">開發經驗 *</label>
                        <select class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" required>
                            <option value="">請選擇</option>
                            <option value="1-2年">1-2年</option>
                            <option value="3-5年">3-5年</option>
                            <option value="5-10年">5-10年</option>
                            <option value="10年以上">10年以上</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">期望開發者等級 *</label>
                        <select class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" required>
                            <option value="">請選擇</option>
                            <option value="core">核心開發者</option>
                            <option value="early">早期採用者</option>
                            <option value="professional">專業開發者</option>
                            <option value="community">社群開發者</option>
                        </select>
                    </div>
                </div>
                
                <div class="mt-6">
                    <label class="block text-sm font-medium text-gray-700 mb-2">主要使用場景 *</label>
                    <textarea class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 h-32" placeholder="描述你計劃如何使用PowerAutomation，以及期望解決的問題..." required></textarea>
                </div>
                
                <div class="mt-6">
                    <label class="flex items-center">
                        <input type="checkbox" class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" required>
                        <span class="ml-2 text-sm text-gray-700">我承諾積極提供使用反饋和建議</span>
                    </label>
                </div>
                
                <div class="mt-8 text-center">
                    <button type="submit" class="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 text-lg">
                        提交申請
                    </button>
                    <p class="text-sm text-gray-500 mt-2">
                        限時開放：2025年7月31日截止申請
                    </p>
                </div>
            </form>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center">
                <h3 class="text-2xl font-bold mb-4">立即加入Beta開發者計劃</h3>
                <p class="text-gray-300 mb-6">100個名額，先到先得</p>
                <button class="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700">
                    申請開發者權限
                </button>
            </div>
        </div>
    </footer>

    <!-- JavaScript -->
    <script>
        // Form submission handling
        document.querySelector('form').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('申請已提交！我們將在24小時內通過郵件聯繫您。');
        });
        
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
    </script>
</body>
</html>'''
        
        return html

def main():
    """生成Beta開發者計劃"""
    program = BetaDeveloperProgram()
    
    print("🚀 PowerAutomation Beta開發者計劃")
    print("=" * 50)
    
    # 程序配置
    config = program.program_config
    print(f"\n📋 計劃概要:")
    print(f"   名稱: {config['program_info']['name']}")
    print(f"   總名額: {config['program_info']['total_slots']}")
    print(f"   免費期: {config['program_info']['duration_days']}天")
    print(f"   啟動日期: {config['program_info']['launch_date']}")
    
    # 開發者等級
    print(f"\n👥 開發者等級分配:")
    for tier_key, tier_info in config['developer_tiers'].items():
        print(f"   {tier_info['name']:12} | {tier_info['slots']:2d}個名額 | {tier_info['description']}")
    
    # 生成登陸頁
    html_content = program.generate_landing_page_html()
    with open('beta_developer_landing.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # 生成入職流程示例
    core_onboarding = program.create_developer_onboarding('core')
    
    print(f"\n📚 核心開發者入職流程:")
    for step in core_onboarding['steps']:
        print(f"   第{step['step']}步: {step['title']} ({step['estimated_time']})")
    
    # 生成邀請碼示例
    print(f"\n🎫 邀請碼示例:")
    for tier in ['core', 'early', 'professional', 'community']:
        invite_code = program.generate_invite_code(tier, 1)
        print(f"   {tier:12} | {invite_code}")
    
    # 保存完整配置
    full_config = {
        "program_config": config,
        "landing_page_config": program.landing_page_config,
        "generated_at": datetime.now().isoformat()
    }
    
    with open('beta_developer_program.json', 'w', encoding='utf-8') as f:
        json.dump(full_config, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📁 文件已生成:")
    print(f"   Landing Page: beta_developer_landing.html")
    print(f"   配置文件: beta_developer_program.json")
    
    print(f"\n🎯 關鍵優勢:")
    print(f"   ✅ 測試用戶獲得開發者身份和專屬權限")
    print(f"   ✅ 60天免費期建立用戶粘性")
    print(f"   ✅ 分層管理確保高質量反饋")
    print(f"   ✅ 激勵機制促進長期合作")

if __name__ == "__main__":
    main()
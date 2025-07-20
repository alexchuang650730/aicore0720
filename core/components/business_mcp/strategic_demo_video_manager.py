#!/usr/bin/env python3
"""
Business MCP 驅動的戰略演示視頻管理器
根據市場策略來剪輯和呈現 ClaudeEditor 演示錄製
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import os

from .business_manager import business_manager
from .strategic_demo_engine import strategic_demo_engine

logger = logging.getLogger(__name__)

class VideoType(Enum):
    """視頻類型"""
    HERO_SHOWCASE = "hero_showcase"           # 首頁主展示
    FEATURE_DEMO = "feature_demo"             # 功能演示
    USE_CASE = "use_case"                     # 用例展示
    CUSTOMER_STORY = "customer_story"         # 客戶故事
    TUTORIAL = "tutorial"                     # 教程視頻

class TargetAudience(Enum):
    """目標受眾"""
    INDIVIDUAL_DEVELOPER = "individual_developer"
    STARTUP_TEAM = "startup_team"
    SME_COMPANY = "sme_company"
    ENTERPRISE = "enterprise"
    ALL_USERS = "all_users"

@dataclass
class DemoVideoSegment:
    """演示視頻片段"""
    segment_id: str
    title: str
    description: str
    start_time: float                # 開始時間（秒）
    end_time: float                  # 結束時間（秒）
    features_demonstrated: List[str]  # 演示的功能
    business_value: str              # 商業價值
    target_audience: TargetAudience
    complexity_level: int            # 複雜度 1-5
    roi_impact: float               # ROI 影響評分

@dataclass
class StrategicDemoVideo:
    """戰略演示視頻"""
    video_id: str
    title: str
    description: str
    video_type: VideoType
    target_audiences: List[TargetAudience]
    segments: List[DemoVideoSegment]
    total_duration: float            # 總時長（秒）
    original_file_path: str         # 原始文件路徑
    edited_file_path: Optional[str] # 編輯後文件路徑
    thumbnail_path: Optional[str]   # 縮略圖路徑
    business_rationale: str         # 商業邏輯
    market_positioning: str         # 市場定位
    call_to_action: str            # 行動號召
    created_at: datetime
    last_updated: datetime

class StrategicDemoVideoManager:
    """戰略演示視頻管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 視頻庫
        self.demo_videos: Dict[str, StrategicDemoVideo] = {}
        
        # 視頻存儲路徑
        self.video_storage_path = "/opt/powerauto/static/videos"
        self.thumbnail_storage_path = "/opt/powerauto/static/thumbnails"
        
        # 確保目錄存在
        os.makedirs(self.video_storage_path, exist_ok=True)
        os.makedirs(self.thumbnail_storage_path, exist_ok=True)
        
        # 初始化演示視頻庫
        self._initialize_demo_video_library()
    
    def _initialize_demo_video_library(self):
        """初始化演示視頻庫"""
        # 模擬已有的 ClaudeEditor 演示錄製
        demo_videos = [
            # 首頁主展示視頻
            StrategicDemoVideo(
                video_id="hero_main_demo",
                title="PowerAuto.ai 完整開發流程演示",
                description="從需求分析到部署的完整AI驅動開發流程",
                video_type=VideoType.HERO_SHOWCASE,
                target_audiences=[TargetAudience.ALL_USERS],
                segments=[
                    DemoVideoSegment(
                        segment_id="intro_overview",
                        title="產品概覽",
                        description="PowerAuto.ai 核心價值主張介紹",
                        start_time=0.0,
                        end_time=30.0,
                        features_demonstrated=["界面總覽", "核心功能"],
                        business_value="建立產品認知和信任",
                        target_audience=TargetAudience.ALL_USERS,
                        complexity_level=1,
                        roi_impact=8.5
                    ),
                    DemoVideoSegment(
                        segment_id="smart_intervention_demo",
                        title="Smart Intervention 實時演示",
                        description="展示 <100ms 響應的智能干預功能",
                        start_time=30.0,
                        end_time=90.0,
                        features_demonstrated=["Smart Intervention", "實時代碼生成", "錯誤預防"],
                        business_value="證明技術領先性和效率提升",
                        target_audience=TargetAudience.INDIVIDUAL_DEVELOPER,
                        complexity_level=3,
                        roi_impact=9.2
                    ),
                    DemoVideoSegment(
                        segment_id="k2_cost_savings",
                        title="K2模型成本節省演示",
                        description="對比 Claude vs K2，展示60%成本節省",
                        start_time=90.0,
                        end_time=150.0,
                        features_demonstrated=["K2模型", "成本監控", "智能路由"],
                        business_value="突出成本優勢和商業價值",
                        target_audience=TargetAudience.SME_COMPANY,
                        complexity_level=2,
                        roi_impact=9.5
                    ),
                    DemoVideoSegment(
                        segment_id="team_collaboration",
                        title="團隊協作工作流",
                        description="展示多人協作和項目管理功能",
                        start_time=150.0,
                        end_time=210.0,
                        features_demonstrated=["團隊協作", "進度跟踪", "任務分配"],
                        business_value="證明團隊效率和協作能力",
                        target_audience=TargetAudience.STARTUP_TEAM,
                        complexity_level=4,
                        roi_impact=8.8
                    ),
                    DemoVideoSegment(
                        segment_id="enterprise_integration",
                        title="企業級集成展示",
                        description="展示與企業現有系統的無縫集成",
                        start_time=210.0,
                        end_time=270.0,
                        features_demonstrated=["API集成", "SSO", "權限管理", "合規性"],
                        business_value="證明企業就緒和可擴展性",
                        target_audience=TargetAudience.ENTERPRISE,
                        complexity_level=5,
                        roi_impact=9.0
                    ),
                    DemoVideoSegment(
                        segment_id="results_roi",
                        title="結果展示與ROI計算",
                        description="展示最終成果和投資回報率",
                        start_time=270.0,
                        end_time=300.0,
                        features_demonstrated=["結果展示", "ROI計算", "性能指標"],
                        business_value="提供決策依據和購買動機",
                        target_audience=TargetAudience.ALL_USERS,
                        complexity_level=2,
                        roi_impact=9.8
                    )
                ],
                total_duration=300.0,
                original_file_path="/opt/powerauto/videos/claudeeditor_complete_demo.mp4",
                edited_file_path=None,
                thumbnail_path=None,
                business_rationale="全面展示產品能力，建立信任並推動轉換",
                market_positioning="AI開發工具領導者",
                call_to_action="立即免費試用",
                created_at=datetime.now(),
                last_updated=datetime.now()
            ),
            
            # 功能專項演示
            StrategicDemoVideo(
                video_id="efficiency_focus_demo",
                title="10倍效率提升專項演示",
                description="專注展示效率提升的核心功能",
                video_type=VideoType.FEATURE_DEMO,
                target_audiences=[TargetAudience.INDIVIDUAL_DEVELOPER, TargetAudience.STARTUP_TEAM],
                segments=[
                    DemoVideoSegment(
                        segment_id="before_after_comparison",
                        title="效率對比",
                        description="傳統開發 vs PowerAuto.ai 開發效率對比",
                        start_time=0.0,
                        end_time=60.0,
                        features_demonstrated=["效率對比", "時間節省"],
                        business_value="直觀展示價值主張",
                        target_audience=TargetAudience.INDIVIDUAL_DEVELOPER,
                        complexity_level=2,
                        roi_impact=9.0
                    ),
                    DemoVideoSegment(
                        segment_id="six_workflows_demo",
                        title="六大工作流自動化",
                        description="展示完整的自動化工作流程",
                        start_time=60.0,
                        end_time=180.0,
                        features_demonstrated=["需求分析", "架構設計", "編碼", "測試", "部署", "監控"],
                        business_value="證明全流程自動化能力",
                        target_audience=TargetAudience.STARTUP_TEAM,
                        complexity_level=4,
                        roi_impact=9.3
                    )
                ],
                total_duration=180.0,
                original_file_path="/opt/powerauto/videos/efficiency_demo.mp4",
                edited_file_path=None,
                thumbnail_path=None,
                business_rationale="針對效率關注者的專項展示",
                market_positioning="效率提升專家",
                call_to_action="體驗10倍效率",
                created_at=datetime.now(),
                last_updated=datetime.now()
            ),
            
            # 企業用例演示
            StrategicDemoVideo(
                video_id="enterprise_use_case",
                title="企業數字化轉型案例",
                description="展示大型企業如何使用PowerAuto.ai進行數字化轉型",
                video_type=VideoType.USE_CASE,
                target_audiences=[TargetAudience.ENTERPRISE],
                segments=[
                    DemoVideoSegment(
                        segment_id="enterprise_challenges",
                        title="企業挑戰分析",
                        description="分析大型企業面臨的技術挑戰",
                        start_time=0.0,
                        end_time=45.0,
                        features_demonstrated=["問題識別", "需求分析"],
                        business_value="建立問題共鳴",
                        target_audience=TargetAudience.ENTERPRISE,
                        complexity_level=3,
                        roi_impact=8.0
                    ),
                    DemoVideoSegment(
                        segment_id="solution_implementation",
                        title="解決方案實施",
                        description="展示PowerAuto.ai企業級解決方案",
                        start_time=45.0,
                        end_time=165.0,
                        features_demonstrated=["企業集成", "安全合規", "規模化部署"],
                        business_value="證明企業級能力",
                        target_audience=TargetAudience.ENTERPRISE,
                        complexity_level=5,
                        roi_impact=9.5
                    )
                ],
                total_duration=165.0,
                original_file_path="/opt/powerauto/videos/enterprise_case_study.mp4",
                edited_file_path=None,
                thumbnail_path=None,
                business_rationale="針對企業客戶的深度用例展示",
                market_positioning="企業級解決方案提供商",
                call_to_action="預約企業演示",
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
        ]
        
        for video in demo_videos:
            self.demo_videos[video.video_id] = video
    
    async def generate_strategic_video_plan(self) -> Dict[str, Any]:
        """根據 Business MCP 策略生成視頻計劃"""
        self.logger.info("根據 Business MCP 策略生成視頻展示計劃")
        
        # 獲取 Business MCP 數據
        market_analysis = await business_manager.generate_market_analysis()
        acquisition_strategy = await business_manager.generate_customer_acquisition_strategy()
        
        # 分析目標市場和獲客渠道
        target_segments = market_analysis.get("target_segments", [])
        acquisition_channels = acquisition_strategy.get("channels", [])
        
        # 生成視頻策略計劃
        video_plan = {
            "executive_summary": {
                "strategy_focus": "根據市場細分和獲客渠道優化視頻內容",
                "primary_objectives": [
                    "提升轉換率",
                    "降低獲客成本",
                    "建立市場地位",
                    "加速決策流程"
                ],
                "target_improvement": "30% 轉換率提升"
            },
            "audience_prioritization": self._prioritize_audiences(target_segments),
            "content_strategy": self._create_content_strategy(acquisition_channels),
            "video_placement_plan": await self._create_video_placement_plan(),
            "editing_guidelines": self._create_editing_guidelines(),
            "performance_tracking": {
                "key_metrics": [
                    "視頻完成率",
                    "點擊轉換率", 
                    "演示預約率",
                    "trial_signup_rate"
                ],
                "target_benchmarks": {
                    "completion_rate": "70%",
                    "click_through_rate": "8%",
                    "demo_request_rate": "15%",
                    "signup_conversion": "25%"
                }
            }
        }
        
        return video_plan
    
    def _prioritize_audiences(self, target_segments: List[Dict]) -> List[Dict[str, Any]]:
        """根據市場潛力排序目標受眾"""
        audience_priority = []
        
        for segment in target_segments:
            segment_name = segment.get("segment", "")
            growth_rate = float(segment.get("growth_rate", "0%").replace("%", "")) / 100
            
            if "中小企業" in segment_name:
                audience_priority.append({
                    "audience": TargetAudience.SME_COMPANY.value,
                    "priority": 1,
                    "market_size": segment.get("size", "50萬"),
                    "growth_rate": growth_rate,
                    "video_focus": "成本節省和團隊效率",
                    "recommended_duration": "2-3分鐘"
                })
            elif "個人開發者" in segment_name:
                audience_priority.append({
                    "audience": TargetAudience.INDIVIDUAL_DEVELOPER.value,
                    "priority": 2,
                    "market_size": segment.get("size", "200萬"),
                    "growth_rate": growth_rate,
                    "video_focus": "技能提升和效率工具",
                    "recommended_duration": "1-2分鐘"
                })
            elif "大型企業" in segment_name:
                audience_priority.append({
                    "audience": TargetAudience.ENTERPRISE.value,
                    "priority": 3,
                    "market_size": segment.get("size", "5000"),
                    "growth_rate": growth_rate,
                    "video_focus": "企業級功能和集成",
                    "recommended_duration": "3-5分鐘"
                })
        
        # 按優先級排序
        audience_priority.sort(key=lambda x: x["priority"])
        return audience_priority
    
    def _create_content_strategy(self, acquisition_channels: List[Dict]) -> Dict[str, Any]:
        """根據獲客渠道創建內容策略"""
        content_strategy = {
            "channel_specific_content": {},
            "universal_content": {
                "hero_video": {
                    "duration": "90秒",
                    "focus": "核心價值主張",
                    "call_to_action": "立即免費試用"
                }
            }
        }
        
        for channel in acquisition_channels:
            channel_name = channel.get("channel", "")
            
            if "內容營銷" in channel_name:
                content_strategy["channel_specific_content"]["content_marketing"] = {
                    "video_type": "教育型演示",
                    "duration": "3-5分鐘",
                    "focus": "技術深度和專業性",
                    "placement": ["技術博客", "視頻教程平台"]
                }
            elif "社區運營" in channel_name:
                content_strategy["channel_specific_content"]["community"] = {
                    "video_type": "快速演示",
                    "duration": "1-2分鐘",
                    "focus": "實用功能和效果",
                    "placement": ["Discord", "GitHub", "技術論壇"]
                }
            elif "付費廣告" in channel_name:
                content_strategy["channel_specific_content"]["paid_ads"] = {
                    "video_type": "轉換型廣告",
                    "duration": "30-60秒",
                    "focus": "ROI和立即行動",
                    "placement": ["搜索廣告", "社交媒體"]
                }
        
        return content_strategy
    
    async def _create_video_placement_plan(self) -> Dict[str, Any]:
        """創建視頻放置計劃"""
        return {
            "homepage": {
                "hero_section": {
                    "video_id": "hero_main_demo",
                    "segments": ["intro_overview", "smart_intervention_demo", "results_roi"],
                    "total_duration": "90秒",
                    "autoplay": True,
                    "controls": True
                },
                "features_section": {
                    "video_id": "efficiency_focus_demo", 
                    "segments": ["six_workflows_demo"],
                    "total_duration": "120秒",
                    "trigger": "scroll_into_view"
                }
            },
            "pricing_page": {
                "value_demonstration": {
                    "video_id": "hero_main_demo",
                    "segments": ["k2_cost_savings", "results_roi"],
                    "total_duration": "90秒",
                    "focus": "ROI證明"
                }
            },
            "enterprise_page": {
                "enterprise_showcase": {
                    "video_id": "enterprise_use_case",
                    "segments": ["solution_implementation"],
                    "total_duration": "120秒",
                    "focus": "企業級能力"
                }
            }
        }
    
    def _create_editing_guidelines(self) -> Dict[str, Any]:
        """創建編輯指導原則"""
        return {
            "general_principles": [
                "前30秒是黃金時間，必須抓住注意力",
                "每個片段都要有明確的商業價值",
                "使用數據和指標增強說服力",
                "結尾必須有明確的行動號召"
            ],
            "audience_specific_editing": {
                "individual_developer": {
                    "pace": "快節奏",
                    "focus": "技術細節和效率提升",
                    "tone": "專業但親和",
                    "visual_style": "代碼為主"
                },
                "startup_team": {
                    "pace": "中等節奏",
                    "focus": "團隊協作和快速交付",
                    "tone": "激勵型",
                    "visual_style": "團隊工作場景"
                },
                "enterprise": {
                    "pace": "穩重節奏",
                    "focus": "穩定性和企業級功能",
                    "tone": "權威專業",
                    "visual_style": "企業環境"
                }
            },
            "technical_requirements": {
                "resolution": "1920x1080",
                "format": "MP4",
                "bitrate": "5-8 Mbps",
                "frame_rate": "30fps",
                "audio": "AAC 128kbps"
            }
        }
    
    async def create_audience_specific_video(self, video_id: str, 
                                           target_audience: TargetAudience) -> Dict[str, Any]:
        """為特定受眾創建定制視頻"""
        if video_id not in self.demo_videos:
            return {"error": "視頻不存在"}
        
        original_video = self.demo_videos[video_id]
        
        # 根據受眾篩選相關片段
        relevant_segments = [
            segment for segment in original_video.segments
            if segment.target_audience == target_audience or 
               segment.target_audience == TargetAudience.ALL_USERS
        ]
        
        # 按 ROI 影響排序
        relevant_segments.sort(key=lambda x: x.roi_impact, reverse=True)
        
        # 選擇前3-4個最相關的片段
        selected_segments = relevant_segments[:4]
        
        # 計算總時長
        total_duration = sum(seg.end_time - seg.start_time for seg in selected_segments)
        
        # 生成編輯指導
        editing_plan = {
            "target_audience": target_audience.value,
            "selected_segments": [
                {
                    "segment_id": seg.segment_id,
                    "title": seg.title,
                    "start_time": seg.start_time,
                    "end_time": seg.end_time,
                    "duration": seg.end_time - seg.start_time,
                    "business_value": seg.business_value,
                    "roi_impact": seg.roi_impact
                }
                for seg in selected_segments
            ],
            "total_duration": total_duration,
            "editing_instructions": self._generate_editing_instructions(target_audience, selected_segments),
            "call_to_action": self._get_audience_specific_cta(target_audience),
            "thumbnail_concept": self._generate_thumbnail_concept(target_audience)
        }
        
        return editing_plan
    
    def _generate_editing_instructions(self, audience: TargetAudience, 
                                     segments: List[DemoVideoSegment]) -> List[str]:
        """生成編輯指導"""
        instructions = [
            f"目標受眾: {audience.value}",
            "開場30秒內必須建立價值主張",
        ]
        
        if audience == TargetAudience.INDIVIDUAL_DEVELOPER:
            instructions.extend([
                "強調技術細節和代碼生成能力",
                "使用快節奏剪輯保持注意力",
                "展示實際編程場景",
                "突出效率提升的具體數據"
            ])
        elif audience == TargetAudience.STARTUP_TEAM:
            instructions.extend([
                "突出團隊協作和快速交付",
                "展示產品上市時間縮短",
                "強調成本控制和資源優化",
                "使用激勵性的配樂和節奏"
            ])
        elif audience == TargetAudience.ENTERPRISE:
            instructions.extend([
                "強調企業級安全和合規",
                "展示大規模部署和集成能力",
                "突出ROI和商業價值",
                "使用權威專業的敘述風格"
            ])
        
        # 添加片段特定指導
        for i, segment in enumerate(segments):
            instructions.append(f"片段{i+1}: {segment.title} - {segment.business_value}")
        
        return instructions
    
    def _get_audience_specific_cta(self, audience: TargetAudience) -> str:
        """獲取受眾特定的行動號召"""
        cta_map = {
            TargetAudience.INDIVIDUAL_DEVELOPER: "立即免費試用 - 體驗10倍效率",
            TargetAudience.STARTUP_TEAM: "申請14天免費試用 - 加速產品上市",
            TargetAudience.SME_COMPANY: "預約產品演示 - 了解成本節省方案",
            TargetAudience.ENTERPRISE: "聯繫企業銷售 - 獲取定制解決方案"
        }
        return cta_map.get(audience, "立即開始免費試用")
    
    def _generate_thumbnail_concept(self, audience: TargetAudience) -> str:
        """生成縮略圖概念"""
        thumbnail_concepts = {
            TargetAudience.INDIVIDUAL_DEVELOPER: "代碼界面 + 效率數據 + 開發者圖像",
            TargetAudience.STARTUP_TEAM: "團隊協作界面 + 增長曲線 + 團隊圖像",
            TargetAudience.SME_COMPANY: "儀表板界面 + ROI數據 + 專業人士圖像",
            TargetAudience.ENTERPRISE: "企業級界面 + 安全標識 + 商務場景"
        }
        return thumbnail_concepts.get(audience, "產品界面 + 核心價值")
    
    async def generate_homepage_video_integration(self) -> str:
        """生成首頁視頻集成代碼"""
        video_plan = await self.generate_strategic_video_plan()
        
        # 根據用戶細分選擇不同的視頻內容
        integration_code = '''
        <!-- Business MCP 戰略視頻展示系統 -->
        <div class="strategic-video-container" style="position: relative; margin: 2rem 0;">
            <div id="heroVideoContainer" style="border-radius: 16px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.15);">
                <!-- 默認視頻 - 通用展示 -->
                <video id="mainDemoVideo" 
                       controls 
                       preload="metadata" 
                       poster="/static/thumbnails/hero_demo_thumbnail.jpg"
                       style="width: 100%; height: auto; background: #000;">
                    <source src="/static/videos/hero_main_demo_optimized.mp4" type="video/mp4">
                    <source src="/static/videos/hero_main_demo_optimized.webm" type="video/webm">
                    您的瀏覽器不支持視頻播放。
                </video>
                
                <!-- 視頻覆蓋層 - 顯示商業價值 -->
                <div class="video-overlay" style="position: absolute; top: 10px; right: 10px; 
                                                 background: rgba(0,0,0,0.8); color: white; 
                                                 padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.9rem;">
                    <span id="videoValueProposition">💰 ROI: 200%+ | ⚡ 效率: 10倍提升</span>
                </div>
                
                <!-- 進度指示器 -->
                <div class="video-progress-indicator" style="position: absolute; bottom: 10px; left: 10px; right: 10px;">
                    <div style="background: rgba(255,255,255,0.3); height: 4px; border-radius: 2px;">
                        <div id="businessValueProgress" style="background: #10b981; height: 100%; width: 0%; 
                                                             border-radius: 2px; transition: width 0.3s ease;"></div>
                    </div>
                </div>
            </div>
            
            <!-- 視頻選擇器 - 基於用戶細分 -->
            <div class="video-selector" style="display: flex; gap: 1rem; margin-top: 1rem; justify-content: center;">
                <button class="video-option" data-audience="individual_developer" 
                        style="padding: 0.5rem 1rem; border: 2px solid #667eea; background: white; 
                               border-radius: 8px; cursor: pointer; transition: all 0.3s ease;">
                    👨‍💻 個人開發者
                </button>
                <button class="video-option" data-audience="startup_team"
                        style="padding: 0.5rem 1rem; border: 2px solid #10b981; background: white; 
                               border-radius: 8px; cursor: pointer; transition: all 0.3s ease;">
                    🚀 創業團隊
                </button>
                <button class="video-option" data-audience="enterprise"
                        style="padding: 0.5rem 1rem; border: 2px solid #f59e0b; background: white; 
                               border-radius: 8px; cursor: pointer; transition: all 0.3s ease;">
                    🏢 企業
                </button>
            </div>
            
            <!-- 當前視頻信息 -->
            <div class="current-video-info" style="text-align: center; margin-top: 1rem; color: #666;">
                <h4 id="currentVideoTitle" style="margin: 0.5rem 0;">PowerAuto.ai 完整開發流程演示</h4>
                <p id="currentVideoDescription" style="margin: 0; font-size: 0.9rem;">
                    從需求分析到部署的完整AI驅動開發流程
                </p>
                <div style="margin-top: 0.5rem;">
                    <span id="videoDuration" style="color: #667eea;">⏱️ 5:00</span>
                    <span style="margin: 0 1rem;">|</span>
                    <span id="videoFocus" style="color: #10b981;">🎯 全流程演示</span>
                </div>
            </div>
        </div>
        
        <script>
        (function() {
            // 視頻配置 - 基於 Business MCP 策略
            const videoConfigs = {
                'individual_developer': {
                    src: '/static/videos/developer_focused_demo.mp4',
                    poster: '/static/thumbnails/developer_demo_thumb.jpg',
                    title: '個人開發者效率提升演示',
                    description: '展示如何將編程效率提升10倍，從重複工作中解放',
                    duration: '3:00',
                    focus: '10倍效率提升',
                    valueProposition: '⚡ 效率: 10倍 | 💰 成本: 節省80%',
                    cta: '立即免費體驗10倍效率'
                },
                'startup_team': {
                    src: '/static/videos/startup_team_demo.mp4',
                    poster: '/static/thumbnails/startup_demo_thumb.jpg',
                    title: '創業團隊協作演示',
                    description: '展示如何讓小團隊實現大企業的開發效率',
                    duration: '4:00',
                    focus: '團隊協作 + 快速交付',
                    valueProposition: '🚀 速度: 3倍提升 | 💰 ROI: 250%',
                    cta: '申請14天免費試用'
                },
                'enterprise': {
                    src: '/static/videos/enterprise_demo.mp4',
                    poster: '/static/thumbnails/enterprise_demo_thumb.jpg',
                    title: '企業級解決方案演示',
                    description: '展示企業級安全、合規和大規模部署能力',
                    duration: '6:00',
                    focus: '企業級安全 + 規模化',
                    valueProposition: '🏢 企業級 | 🔒 100%合規 | 💰 ROI: 500%',
                    cta: '預約企業演示'
                }
            };
            
            const videoElement = document.getElementById('mainDemoVideo');
            const videoButtons = document.querySelectorAll('.video-option');
            
            // 用戶細分檢測
            function detectUserSegment() {
                const referrer = document.referrer;
                const userAgent = navigator.userAgent;
                const screenWidth = window.innerWidth;
                
                // 簡單的用戶細分邏輯
                if (referrer.includes('github.com') || referrer.includes('stackoverflow.com')) {
                    return 'individual_developer';
                } else if (screenWidth > 1400 && !userAgent.includes('Mobile')) {
                    return 'enterprise';
                } else {
                    return 'startup_team';
                }
            }
            
            // 切換視頻
            function switchVideo(audienceType) {
                const config = videoConfigs[audienceType];
                if (!config) return;
                
                // 更新視頻源
                videoElement.src = config.src;
                videoElement.poster = config.poster;
                
                // 更新信息
                document.getElementById('currentVideoTitle').textContent = config.title;
                document.getElementById('currentVideoDescription').textContent = config.description;
                document.getElementById('videoDuration').innerHTML = `⏱️ ${config.duration}`;
                document.getElementById('videoFocus').innerHTML = `🎯 ${config.focus}`;
                document.getElementById('videoValueProposition').textContent = config.valueProposition;
                
                // 更新按鈕狀態
                videoButtons.forEach(btn => {
                    btn.style.background = 'white';
                    btn.style.color = btn.style.borderColor;
                });
                
                const activeButton = document.querySelector(`[data-audience="${audienceType}"]`);
                if (activeButton) {
                    activeButton.style.background = activeButton.style.borderColor;
                    activeButton.style.color = 'white';
                }
                
                // 記錄用戶偏好
                localStorage.setItem('preferredVideoAudience', audienceType);
                
                // 分析跟踪
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'video_segment_selection', {
                        'audience_type': audienceType,
                        'video_title': config.title
                    });
                }
            }
            
            // 視頻進度追蹤
            videoElement.addEventListener('timeupdate', function() {
                const progress = (this.currentTime / this.duration) * 100;
                document.getElementById('businessValueProgress').style.width = progress + '%';
                
                // 關鍵時刻提示
                if (progress > 25 && progress < 30) {
                    document.getElementById('videoValueProposition').textContent = '🎯 智能代碼生成演示中...';
                } else if (progress > 50 && progress < 55) {
                    document.getElementById('videoValueProposition').textContent = '💰 ROI計算展示中...';
                } else if (progress > 80 && progress < 85) {
                    document.getElementById('videoValueProposition').textContent = '✨ 準備體驗?';
                }
            });
            
            // 視頻完成後的行動號召
            videoElement.addEventListener('ended', function() {
                const currentAudience = localStorage.getItem('preferredVideoAudience') || 'startup_team';
                const config = videoConfigs[currentAudience];
                
                // 顯示個性化CTA
                const ctaOverlay = document.createElement('div');
                ctaOverlay.style.cssText = `
                    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; padding: 2rem; border-radius: 16px; text-align: center;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3); z-index: 1000;
                `;
                ctaOverlay.innerHTML = `
                    <h3 style="margin: 0 0 1rem 0;">準備好體驗了嗎？</h3>
                    <p style="margin: 0 0 1.5rem 0; opacity: 0.9;">${config.description}</p>
                    <button onclick="window.location.href='/register'" 
                            style="background: white; color: #667eea; border: none; 
                                   padding: 1rem 2rem; border-radius: 8px; font-weight: 600; 
                                   cursor: pointer; font-size: 1.1rem;">
                        ${config.cta}
                    </button>
                    <button onclick="this.closest('div').remove()" 
                            style="background: transparent; color: white; border: 1px solid white; 
                                   padding: 1rem 2rem; border-radius: 8px; margin-left: 1rem; 
                                   cursor: pointer;">
                        稍後再說
                    </button>
                `;
                
                document.getElementById('heroVideoContainer').appendChild(ctaOverlay);
            });
            
            // 綁定事件
            videoButtons.forEach(button => {
                button.addEventListener('click', function() {
                    switchVideo(this.dataset.audience);
                });
            });
            
            // 自動檢測並設置用戶細分
            const detectedSegment = detectUserSegment();
            switchVideo(detectedSegment);
            
            console.log('🎬 Business MCP 戰略視頻系統已載入');
        })();
        </script>
        '''
        
        return integration_code

# 全局視頻管理器實例
strategic_demo_video_manager = StrategicDemoVideoManager()

# 演示功能
async def demo_strategic_video_management():
    """戰略視頻管理系統演示"""
    print("🎬 Business MCP 戰略演示視頻管理系統演示")
    print("=" * 70)
    
    # 1. 生成視頻戰略計劃
    print("\n1. 生成視頻戰略計劃")
    video_plan = await strategic_demo_video_manager.generate_strategic_video_plan()
    
    print(f"戰略焦點: {video_plan['executive_summary']['strategy_focus']}")
    print(f"目標改善: {video_plan['executive_summary']['target_improvement']}")
    
    print("\n受眾優先級:")
    for audience in video_plan['audience_prioritization']:
        print(f"  {audience['priority']}. {audience['audience']}")
        print(f"     市場規模: {audience['market_size']}")
        print(f"     視頻焦點: {audience['video_focus']}")
        print(f"     建議時長: {audience['recommended_duration']}")
    
    # 2. 創建受眾特定視頻
    print("\n2. 創建受眾特定視頻")
    audiences = [
        TargetAudience.INDIVIDUAL_DEVELOPER,
        TargetAudience.STARTUP_TEAM,
        TargetAudience.ENTERPRISE
    ]
    
    for audience in audiences:
        editing_plan = await strategic_demo_video_manager.create_audience_specific_video(
            "hero_main_demo", audience
        )
        
        print(f"\n{audience.value} 視頻計劃:")
        print(f"  總時長: {editing_plan['total_duration']:.0f}秒")
        print(f"  片段數量: {len(editing_plan['selected_segments'])}")
        print(f"  行動號召: {editing_plan['call_to_action']}")
        print(f"  縮略圖概念: {editing_plan['thumbnail_concept']}")
        
        print("  選中片段:")
        for i, segment in enumerate(editing_plan['selected_segments'][:2], 1):
            print(f"    {i}. {segment['title']} (ROI影響: {segment['roi_impact']})")
    
    # 3. 生成首頁視頻集成代碼
    print("\n3. 生成首頁視頻集成代碼")
    integration_code = await strategic_demo_video_manager.generate_homepage_video_integration()
    code_size = len(integration_code)
    print(f"集成代碼已生成: {code_size:,} 字符")
    print("功能包含:")
    print("  - 用戶細分自動檢測")
    print("  - 動態視頻切換")
    print("  - 商業價值實時展示")
    print("  - 個性化行動號召")
    print("  - 性能和轉換追蹤")
    
    # 4. 展示視頻庫統計
    print("\n4. 視頻庫統計")
    total_videos = len(strategic_demo_video_manager.demo_videos)
    total_segments = sum(len(video.segments) for video in strategic_demo_video_manager.demo_videos.values())
    total_duration = sum(video.total_duration for video in strategic_demo_video_manager.demo_videos.values())
    
    print(f"總視頻數: {total_videos}")
    print(f"總片段數: {total_segments}")
    print(f"總時長: {total_duration/60:.1f}分鐘")
    
    video_types = {}
    for video in strategic_demo_video_manager.demo_videos.values():
        video_type = video.video_type.value
        video_types[video_type] = video_types.get(video_type, 0) + 1
    
    print("\n視頻類型分佈:")
    for video_type, count in video_types.items():
        print(f"  - {video_type}: {count}個")
    
    return {
        "videos_managed": total_videos,
        "segments_available": total_segments,
        "audiences_targeted": len(audiences),
        "integration_code_generated": True,
        "strategic_plan_ready": True
    }

if __name__ == "__main__":
    result = asyncio.run(demo_strategic_video_management())
    print(f"\n🎉 戰略視頻管理系統演示完成！")
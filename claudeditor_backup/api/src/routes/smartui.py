"""
SmartUI API Routes - 智能响应式UI API接口
基于AG-UI指导的后端API服务
"""

from flask import Blueprint, request, jsonify
import logging
import asyncio
from typing import Dict, Any, Optional

# 导入SmartUI组件
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../core/components'))
    from smartui_mcp.smartui_manager import SmartUIManager
    from ag_ui_mcp.ag_ui_manager import ComponentGenerator
except ImportError as e:
    logging.warning(f"SmartUI components not available: {e}")
    SmartUIManager = None
    ComponentGenerator = None

logger = logging.getLogger(__name__)

# 创建蓝图
smartui_bp = Blueprint('smartui', __name__, url_prefix='/api/smartui')

# 全局SmartUI管理器实例
smartui_manager = None

def get_smartui_manager():
    """获取SmartUI管理器实例"""
    global smartui_manager
    if smartui_manager is None and SmartUIManager:
        smartui_manager = SmartUIManager()
    return smartui_manager

@smartui_bp.route('/configure', methods=['POST'])
def configure_smartui():
    """配置SmartUI响应式设计"""
    try:
        data = request.get_json()
        
        viewport_width = data.get('viewport_width', 1200)
        viewport_height = data.get('viewport_height', 800)
        user_agent = data.get('user_agent', '')
        pixel_ratio = data.get('pixel_ratio', 1.0)
        touch_support = data.get('touch_support', False)
        
        logger.info(f"SmartUI配置请求: {viewport_width}x{viewport_height}, UA: {user_agent[:50]}...")
        
        manager = get_smartui_manager()
        if not manager:
            # 降级到前端检测
            return jsonify({
                'success': False,
                'message': 'SmartUI backend not available, using frontend detection',
                'fallback': True
            })
        
        # 异步检测设备并配置
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            config = loop.run_until_complete(
                manager.detect_device_and_configure(
                    viewport_width, viewport_height, user_agent
                )
            )
            
            # 生成响应式CSS
            css = loop.run_until_complete(manager.generate_responsive_css(config))
            
            # 生成JavaScript配置
            js_config = {
                'deviceType': config.device_type.value,
                'breakpoint': config.breakpoint.value,
                'layoutColumns': config.layout_columns,
                'touchOptimized': config.touch_optimized,
                'sidebarWidth': config.sidebar_width,
                'headerHeight': config.header_height,
                'fontScale': config.font_scale,
                'spacingScale': config.spacing_scale
            }
            
            logger.info(f"SmartUI配置完成: {config.device_type.value}")
            
            return jsonify({
                'success': True,
                'config': {
                    'device_type': config.device_type.value,
                    'breakpoint': config.breakpoint.value,
                    'viewport_width': config.viewport_width,
                    'viewport_height': config.viewport_height,
                    'layout_columns': config.layout_columns,
                    'sidebar_width': config.sidebar_width,
                    'header_height': config.header_height,
                    'touch_optimized': config.touch_optimized,
                    'font_scale': config.font_scale,
                    'spacing_scale': config.spacing_scale
                },
                'css': css,
                'js_config': js_config
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"SmartUI配置失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'SmartUI configuration failed'
        }), 500

@smartui_bp.route('/reconfigure', methods=['POST'])
def reconfigure_smartui():
    """重新配置SmartUI（用于视口变化）"""
    try:
        data = request.get_json()
        
        viewport_width = data.get('viewport_width', 1200)
        viewport_height = data.get('viewport_height', 800)
        user_agent = data.get('user_agent', '')
        
        logger.info(f"SmartUI重新配置: {viewport_width}x{viewport_height}")
        
        manager = get_smartui_manager()
        if not manager:
            return jsonify({
                'success': False,
                'message': 'SmartUI backend not available'
            })
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            config = loop.run_until_complete(
                manager.detect_device_and_configure(
                    viewport_width, viewport_height, user_agent
                )
            )
            
            css = loop.run_until_complete(manager.generate_responsive_css(config))
            
            return jsonify({
                'success': True,
                'device_type': config.device_type.value,
                'css': css,
                'config': {
                    'layout_columns': config.layout_columns,
                    'sidebar_width': config.sidebar_width,
                    'touch_optimized': config.touch_optimized
                }
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"SmartUI重新配置失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@smartui_bp.route('/ag-ui-guidance', methods=['POST'])
def get_ag_ui_guidance():
    """获取AG-UI智能指导"""
    try:
        data = request.get_json()
        
        component_type = data.get('component_type', 'general')
        context = data.get('context', {})
        
        logger.info(f"AG-UI指导请求: {component_type}")
        
        manager = get_smartui_manager()
        if not manager:
            return jsonify({
                'success': False,
                'guidance': 'AG-UI guidance not available',
                'recommendations': []
            })
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            guidance = loop.run_until_complete(
                manager.get_ag_ui_guidance(component_type, context)
            )
            
            return jsonify({
                'success': True,
                'guidance': guidance,
                'component_type': component_type,
                'context': context
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"AG-UI指导获取失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'guidance': 'Error getting AG-UI guidance'
        }), 500

@smartui_bp.route('/status', methods=['GET'])
def get_smartui_status():
    """获取SmartUI系统状态"""
    try:
        manager = get_smartui_manager()
        
        status = {
            'smartui_available': manager is not None,
            'ag_ui_available': ComponentGenerator is not None,
            'current_config': None,
            'device_configs': None
        }
        
        if manager:
            current_config = manager.get_current_config()
            if current_config:
                status['current_config'] = {
                    'device_type': current_config.device_type.value,
                    'breakpoint': current_config.breakpoint.value,
                    'layout_columns': current_config.layout_columns,
                    'touch_optimized': current_config.touch_optimized
                }
            
            device_configs = manager.get_device_configs()
            status['device_configs'] = {
                device_type.value: {
                    'breakpoint': config.breakpoint.value,
                    'layout_columns': config.layout_columns,
                    'sidebar_width': config.sidebar_width,
                    'touch_optimized': config.touch_optimized
                }
                for device_type, config in device_configs.items()
            }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"SmartUI状态获取失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@smartui_bp.route('/test', methods=['GET'])
def test_smartui():
    """测试SmartUI系统"""
    try:
        # 测试不同设备类型的配置
        test_cases = [
            {'width': 375, 'height': 667, 'name': 'iPhone'},
            {'width': 768, 'height': 1024, 'name': 'iPad'},
            {'width': 1200, 'height': 800, 'name': 'Desktop'},
            {'width': 1920, 'height': 1080, 'name': 'Large Desktop'}
        ]
        
        results = []
        manager = get_smartui_manager()
        
        if not manager:
            return jsonify({
                'success': False,
                'message': 'SmartUI not available for testing'
            })
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            for case in test_cases:
                config = loop.run_until_complete(
                    manager.detect_device_and_configure(
                        case['width'], case['height'], ''
                    )
                )
                
                results.append({
                    'test_case': case['name'],
                    'viewport': f"{case['width']}x{case['height']}",
                    'detected_device': config.device_type.value,
                    'breakpoint': config.breakpoint.value,
                    'layout_columns': config.layout_columns,
                    'sidebar_width': config.sidebar_width,
                    'touch_optimized': config.touch_optimized
                })
            
            return jsonify({
                'success': True,
                'test_results': results,
                'message': 'SmartUI test completed successfully'
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"SmartUI测试失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 错误处理
@smartui_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'SmartUI API endpoint not found'
    }), 404

@smartui_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'SmartUI internal server error'
    }), 500


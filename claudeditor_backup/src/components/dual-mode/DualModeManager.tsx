import React, { useState, useCallback, useRef } from 'react';
import { Edit3, Play, Settings, Maximize2, Minimize2 } from 'lucide-react';
import { EditMode } from './EditMode';
import { PresentationMode } from './PresentationMode';

export type EditorMode = 'edit' | 'presentation';

interface DualModeManagerProps {
  className?: string;
  onModeChange?: (mode: EditorMode) => void;
}

export const DualModeManager: React.FC<DualModeManagerProps> = ({
  className = '',
  onModeChange
}) => {
  // 简化的状态管理
  const [mode, setMode] = useState<EditorMode>('edit');
  const [editState, setEditState] = useState({
    openFiles: [] as string[],
    activeFile: '',
    fileContents: {} as Record<string, string>,
    cursorPosition: { line: 1, column: 1 },
    selections: [] as any[],
    theme: 'dark' as const,
    fontSize: 14,
    wordWrap: true,
    minimap: true
  });
  const [presentationState, setPresentationState] = useState({
    currentSlide: 0,
    slides: [] as any[],
    isPlaying: false,
    settings: { 
      showNotes: false,
      autoAdvance: false,
      slideInterval: 5000,
      theme: 'dark' as const,
      transition: 'fade' as const
    },
    playbackHistory: [] as number[]
  });
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // 简化的模式切换
  const switchMode = useCallback((newMode: EditorMode) => {
    if (mode === newMode || isTransitioning) return;
    
    setIsTransitioning(true);
    setMode(newMode);
    
    setTimeout(() => {
      setIsTransitioning(false);
    }, 300);
    
    onModeChange?.(newMode);
  }, [mode, isTransitioning, onModeChange]);

  // 全屏切换
  const toggleFullscreen = useCallback(() => {
    setIsFullscreen(!isFullscreen);
  }, [isFullscreen]);

  return (
    <div 
      ref={containerRef}
      className={`dual-mode-manager ${className} ${isFullscreen ? 'fullscreen' : ''}`}
    >
      {/* 模式切换工具栏 */}
      <div className="mode-toolbar flex items-center justify-between p-2 bg-gray-100 dark:bg-gray-800 border-b">
        <div className="mode-buttons flex items-center space-x-2">
          <button
            onClick={() => switchMode('edit')}
            className={`flex items-center space-x-2 px-3 py-1 rounded ${
              mode === 'edit' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
            disabled={isTransitioning}
          >
            <Edit3 className="w-4 h-4" />
            <span>编辑模式</span>
          </button>
          
          <button
            onClick={() => switchMode('presentation')}
            className={`flex items-center space-x-2 px-3 py-1 rounded ${
              mode === 'presentation' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
            disabled={isTransitioning}
          >
            <Play className="w-4 h-4" />
            <span>演示模式</span>
          </button>
        </div>

        <div className="toolbar-actions flex items-center space-x-2">
          <button
            onClick={toggleFullscreen}
            className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
            title={isFullscreen ? "退出全屏" : "全屏"}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
          
          <button className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700" title="设置">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 模式内容区域 */}
      <div className="mode-content flex-1 relative">
        {isTransitioning && (
          <div className="transition-overlay absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="text-white text-lg">切换中...</div>
          </div>
        )}

        {mode === 'edit' && (
          <EditMode
            isActive={mode === 'edit'}
            state={editState as any}
            onStateChange={setEditState as any}
          />
        )}

        {mode === 'presentation' && (
          <PresentationMode
            isActive={mode === 'presentation'}
            state={presentationState as any}
            onStateChange={setPresentationState as any}
            isFullscreen={isFullscreen}
          />
        )}
      </div>
    </div>
  );
};

export default DualModeManager;


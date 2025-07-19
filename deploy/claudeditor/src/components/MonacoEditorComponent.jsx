import React, { useState, useEffect, useRef, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import './MonacoEditorComponent.css';

// 专业的 Monaco Editor 组件，集成 LSP 功能
const MonacoEditorComponent = ({ isVisible, onClose, initialFile = null }) => {
  const editorRef = useRef(null);
  const monacoRef = useRef(null);
  
  // 编辑器状态
  const [editorState, setEditorState] = useState({
    language: 'javascript',
    theme: 'vs-light',
    content: initialFile?.content || `// PowerAutomation ClaudeEditor - Monaco Editor with LSP
// 智能代码编辑器，支持语法高亮、智能补全、错误检测

import React from 'react';

/**
 * 示例组件 - 展示 Monaco Editor 的强大功能
 * @param {Object} props - 组件属性
 * @returns {JSX.Element} React 组件
 */
const ExampleComponent = ({ title, data }) => {
  const [state, setState] = React.useState({
    loading: false,
    items: data || []
  });

  // 异步数据处理函数
  const handleDataFetch = async () => {
    setState(prev => ({ ...prev, loading: true }));
    
    try {
      const response = await fetch('/api/data');
      const result = await response.json();
      
      setState({
        loading: false,
        items: result.items
      });
    } catch (error) {
      console.error('数据获取失败:', error);
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  return (
    <div className="example-component">
      <h2>{title}</h2>
      {state.loading ? (
        <div>加载中...</div>
      ) : (
        <ul>
          {state.items.map((item, index) => (
            <li key={index}>{item.name}</li>
          ))}
        </ul>
      )}
      <button onClick={handleDataFetch}>
        刷新数据
      </button>
    </div>
  );
};

export default ExampleComponent;`,
    fileName: initialFile?.name || 'example.jsx',
    modified: false,
    cursorPosition: { line: 1, column: 1 },
    selections: []
  });

  // LSP 功能状态
  const [lspState, setLspState] = useState({
    diagnostics: [],
    completions: [],
    hover: null,
    definitions: [],
    references: [],
    symbols: [],
    isConnected: false,
    serverStatus: 'disconnected'
  });

  // 文件管理状态
  const [fileManager, setFileManager] = useState({
    openFiles: [
      { name: 'example.jsx', content: editorState.content, language: 'javascript', modified: false },
      { name: 'styles.css', content: '/* CSS 样式文件 */\n.example-component {\n  padding: 20px;\n  border: 1px solid #ccc;\n}\n\n.example-component h2 {\n  color: #333;\n  margin-bottom: 16px;\n}', language: 'css', modified: false },
      { name: 'config.json', content: '{\n  "name": "PowerAutomation",\n  "version": "4.6.9.6",\n  "description": "智能开发平台",\n  "main": "index.js",\n  "scripts": {\n    "start": "react-scripts start",\n    "build": "react-scripts build",\n    "test": "react-scripts test"\n  }\n}', language: 'json', modified: false }
    ],
    activeFileIndex: 0,
    recentFiles: []
  });

  // 编辑器配置
  const editorOptions = {
    selectOnLineNumbers: true,
    roundedSelection: false,
    readOnly: false,
    cursorStyle: 'line',
    automaticLayout: true,
    glyphMargin: true,
    useTabStops: false,
    fontSize: 14,
    lineHeight: 20,
    fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
    minimap: {
      enabled: true,
      side: 'right'
    },
    scrollBeyondLastLine: false,
    wordWrap: 'on',
    theme: editorState.theme,
    language: editorState.language,
    // LSP 相关配置
    quickSuggestions: {
      other: true,
      comments: true,
      strings: true
    },
    parameterHints: {
      enabled: true
    },
    suggestOnTriggerCharacters: true,
    acceptSuggestionOnEnter: 'on',
    tabCompletion: 'on',
    wordBasedSuggestions: true,
    // 错误和警告
    renderValidationDecorations: 'on',
    // 代码折叠
    folding: true,
    foldingStrategy: 'auto',
    showFoldingControls: 'always',
    // 括号匹配
    matchBrackets: 'always',
    // 自动缩进
    autoIndent: 'full',
    formatOnPaste: true,
    formatOnType: true
  };

  // 初始化 Monaco Editor
  const handleEditorDidMount = useCallback((editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // 配置语言服务
    setupLanguageServices(monaco);
    
    // 设置主题
    setupCustomThemes(monaco);
    
    // 注册快捷键
    registerKeyBindings(editor, monaco);
    
    // 启动 LSP 连接
    initializeLSP(editor, monaco);
    
    // 监听编辑器事件
    setupEditorEvents(editor, monaco);
    
    console.log('Monaco Editor 初始化完成');
  }, []);

  // 设置语言服务
  const setupLanguageServices = (monaco) => {
    // JavaScript/TypeScript 语言配置 - 增强版
    monaco.languages.typescript.javascriptDefaults.setCompilerOptions({
      target: monaco.languages.typescript.ScriptTarget.ES2022,
      allowNonTsExtensions: true,
      moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
      module: monaco.languages.typescript.ModuleKind.ESNext,
      noEmit: true,
      esModuleInterop: true,
      allowSyntheticDefaultImports: true,
      jsx: monaco.languages.typescript.JsxEmit.ReactJSX,
      reactNamespace: 'React',
      allowJs: true,
      checkJs: true,
      strict: true,
      noImplicitAny: false,
      strictNullChecks: true,
      strictFunctionTypes: true,
      noImplicitReturns: true,
      noFallthroughCasesInSwitch: true,
      noUncheckedIndexedAccess: false,
      exactOptionalPropertyTypes: false,
      typeRoots: ['node_modules/@types'],
      lib: ['ES2022', 'DOM', 'DOM.Iterable']
    });

    // TypeScript 语言配置
    monaco.languages.typescript.typescriptDefaults.setCompilerOptions({
      target: monaco.languages.typescript.ScriptTarget.ES2022,
      allowNonTsExtensions: true,
      moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
      module: monaco.languages.typescript.ModuleKind.ESNext,
      noEmit: true,
      esModuleInterop: true,
      allowSyntheticDefaultImports: true,
      jsx: monaco.languages.typescript.JsxEmit.ReactJSX,
      reactNamespace: 'React',
      strict: true,
      noImplicitAny: true,
      strictNullChecks: true,
      strictFunctionTypes: true,
      noImplicitReturns: true,
      noFallthroughCasesInSwitch: true,
      typeRoots: ['node_modules/@types'],
      lib: ['ES2022', 'DOM', 'DOM.Iterable']
    });

    // 设置诊断选项
    monaco.languages.typescript.javascriptDefaults.setDiagnosticsOptions({
      noSemanticValidation: false,
      noSyntaxValidation: false,
      noSuggestionDiagnostics: false,
      diagnosticCodesToIgnore: [1108] // 忽略某些不重要的诊断
    });

    monaco.languages.typescript.typescriptDefaults.setDiagnosticsOptions({
      noSemanticValidation: false,
      noSyntaxValidation: false,
      noSuggestionDiagnostics: false
    });

    // 添加完整的 React 类型定义
    const reactTypes = `
      declare module 'react' {
        import * as CSS from 'csstype';
        
        export interface Component<P = {}, S = {}, SS = any> {}
        export interface PureComponent<P = {}, S = {}, SS = any> {}
        
        // Hooks
        export function useState<T>(initialState: T | (() => T)): [T, (value: T | ((prev: T) => T)) => void];
        export function useEffect(effect: () => void | (() => void), deps?: ReadonlyArray<any>): void;
        export function useCallback<T extends (...args: any[]) => any>(callback: T, deps: ReadonlyArray<any>): T;
        export function useMemo<T>(factory: () => T, deps: ReadonlyArray<any>): T;
        export function useRef<T>(initialValue: T): { current: T };
        export function useRef<T = undefined>(): { current: T | undefined };
        export function useContext<T>(context: Context<T>): T;
        export function useReducer<R extends Reducer<any, any>>(
          reducer: R,
          initialState: ReducerState<R>,
          initializer?: undefined
        ): [ReducerState<R>, Dispatch<ReducerAction<R>>];
        export function useLayoutEffect(effect: () => void | (() => void), deps?: ReadonlyArray<any>): void;
        export function useImperativeHandle<T, R extends T>(
          ref: Ref<T> | undefined,
          init: () => R,
          deps?: ReadonlyArray<any>
        ): void;
        
        // Types
        export type ReactNode = ReactChild | ReactFragment | ReactPortal | boolean | null | undefined;
        export type ReactChild = ReactElement | ReactText;
        export type ReactText = string | number;
        export type ReactElement<P = any, T extends string | JSXElementConstructor<any> = string | JSXElementConstructor<any>> = {
          type: T;
          props: P;
          key: Key | null;
        };
        export type ReactFragment = {} | ReactNodeArray;
        export type ReactNodeArray = Array<ReactNode>;
        export type ReactPortal = {
          key: Key | null;
          children: ReactNode;
        };
        
        export type Key = string | number;
        export type Ref<T> = { current: T } | ((instance: T | null) => void) | null;
        export type JSXElementConstructor<P> = ((props: P) => ReactElement | null) | (new (props: P) => Component<P, any>);
        
        export interface Context<T> {
          Provider: Provider<T>;
          Consumer: Consumer<T>;
          displayName?: string;
        }
        
        export interface Provider<T> {
          (props: { value: T; children?: ReactNode }): ReactElement | null;
        }
        
        export interface Consumer<T> {
          (props: { children: (value: T) => ReactNode }): ReactElement | null;
        }
        
        export type Reducer<S, A> = (prevState: S, action: A) => S;
        export type ReducerState<R extends Reducer<any, any>> = R extends Reducer<infer S, any> ? S : never;
        export type ReducerAction<R extends Reducer<any, any>> = R extends Reducer<any, infer A> ? A : never;
        export type Dispatch<A> = (value: A) => void;
        
        // Event types
        export interface SyntheticEvent<T = Element, E = Event> {
          currentTarget: T;
          target: EventTarget & T;
          preventDefault(): void;
          stopPropagation(): void;
        }
        
        export interface MouseEvent<T = Element> extends SyntheticEvent<T, NativeMouseEvent> {
          clientX: number;
          clientY: number;
          button: number;
        }
        
        export interface ChangeEvent<T = Element> extends SyntheticEvent<T> {
          target: EventTarget & T;
        }
        
        export interface FormEvent<T = Element> extends SyntheticEvent<T> {}
        export interface KeyboardEvent<T = Element> extends SyntheticEvent<T, NativeKeyboardEvent> {
          key: string;
          keyCode: number;
        }
        
        // HTML attributes
        export interface HTMLAttributes<T> {
          className?: string;
          id?: string;
          style?: CSS.Properties;
          onClick?: (event: MouseEvent<T>) => void;
          onChange?: (event: ChangeEvent<T>) => void;
          onSubmit?: (event: FormEvent<T>) => void;
          onKeyDown?: (event: KeyboardEvent<T>) => void;
          children?: ReactNode;
        }
        
        export interface InputHTMLAttributes<T> extends HTMLAttributes<T> {
          value?: string | ReadonlyArray<string> | number;
          defaultValue?: string | ReadonlyArray<string> | number;
          placeholder?: string;
          type?: string;
          disabled?: boolean;
          required?: boolean;
        }
        
        export interface ButtonHTMLAttributes<T> extends HTMLAttributes<T> {
          disabled?: boolean;
          type?: 'submit' | 'reset' | 'button';
        }
        
        // JSX
        export namespace JSX {
          interface Element extends ReactElement<any, any> {}
          interface IntrinsicElements {
            div: HTMLAttributes<HTMLDivElement>;
            span: HTMLAttributes<HTMLSpanElement>;
            p: HTMLAttributes<HTMLParagraphElement>;
            h1: HTMLAttributes<HTMLHeadingElement>;
            h2: HTMLAttributes<HTMLHeadingElement>;
            h3: HTMLAttributes<HTMLHeadingElement>;
            h4: HTMLAttributes<HTMLHeadingElement>;
            h5: HTMLAttributes<HTMLHeadingElement>;
            h6: HTMLAttributes<HTMLHeadingElement>;
            button: ButtonHTMLAttributes<HTMLButtonElement>;
            input: InputHTMLAttributes<HTMLInputElement>;
            form: HTMLAttributes<HTMLFormElement>;
            ul: HTMLAttributes<HTMLUListElement>;
            ol: HTMLAttributes<HTMLOListElement>;
            li: HTMLAttributes<HTMLLIElement>;
            img: HTMLAttributes<HTMLImageElement> & { src?: string; alt?: string; };
            a: HTMLAttributes<HTMLAnchorElement> & { href?: string; target?: string; };
          }
        }
        
        export const Fragment: any;
        export function createElement<P extends {}>(
          type: string | ((props: P) => ReactElement | null),
          props?: P | null,
          ...children: ReactNode[]
        ): ReactElement<P>;
        
        export default React;
      }
      
      declare global {
        namespace JSX {
          interface Element extends React.ReactElement<any, any> {}
          interface IntrinsicElements extends React.JSX.IntrinsicElements {}
        }
      }
    `;
    
    monaco.languages.typescript.javascriptDefaults.addExtraLib(
      reactTypes,
      'file:///node_modules/@types/react/index.d.ts'
    );

    // 添加 Node.js 类型定义
    const nodeTypes = `
      declare module 'fs' {
        export function readFileSync(path: string, encoding?: string): string | Buffer;
        export function writeFileSync(path: string, data: string | Buffer): void;
        export function existsSync(path: string): boolean;
      }
      
      declare module 'path' {
        export function join(...paths: string[]): string;
        export function resolve(...paths: string[]): string;
        export function dirname(path: string): string;
        export function basename(path: string, ext?: string): string;
        export function extname(path: string): string;
      }
      
      declare var console: {
        log(...args: any[]): void;
        error(...args: any[]): void;
        warn(...args: any[]): void;
        info(...args: any[]): void;
        debug(...args: any[]): void;
      };
      
      declare var process: {
        env: { [key: string]: string | undefined };
        argv: string[];
        cwd(): string;
        exit(code?: number): never;
      };
      
      declare var Buffer: {
        from(data: string | ArrayBuffer | number[], encoding?: string): Buffer;
        alloc(size: number): Buffer;
      };
      
      interface Buffer {
        toString(encoding?: string): string;
        length: number;
      }
    `;
    
    monaco.languages.typescript.javascriptDefaults.addExtraLib(
      nodeTypes,
      'file:///node_modules/@types/node/index.d.ts'
    );

    // CSS 语言配置
    monaco.languages.css.cssDefaults.setOptions({
      validate: true,
      lint: {
        compatibleVendorPrefixes: 'ignore',
        vendorPrefix: 'warning',
        duplicateProperties: 'warning',
        emptyRules: 'warning',
        importStatement: 'ignore',
        boxModel: 'ignore',
        universalSelector: 'ignore',
        zeroUnits: 'ignore',
        fontFaceProperties: 'warning',
        hexColorLength: 'error',
        argumentsInColorFunction: 'error',
        unknownProperties: 'warning',
        ieHack: 'ignore',
        unknownVendorSpecificProperties: 'ignore',
        propertyIgnoredDueToDisplay: 'warning',
        important: 'ignore',
        float: 'ignore',
        idSelector: 'ignore'
      }
    });

    // JSON 语言配置
    monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
      validate: true,
      allowComments: false,
      schemas: [{
        uri: 'http://myserver/package-schema.json',
        fileMatch: ['package.json'],
        schema: {
          type: 'object',
          properties: {
            name: { type: 'string' },
            version: { type: 'string' },
            description: { type: 'string' },
            main: { type: 'string' },
            scripts: { type: 'object' }
          }
        }
      }]
    });
  };

  // 设置自定义主题
  const setupCustomThemes = (monaco) => {
    // PowerAutomation 亮色主题
    monaco.editor.defineTheme('powerautomation-light', {
      base: 'vs',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6a737d', fontStyle: 'italic' },
        { token: 'keyword', foreground: '8b5cf6', fontStyle: 'bold' },
        { token: 'string', foreground: '10b981' },
        { token: 'number', foreground: 'f59e0b' },
        { token: 'regexp', foreground: 'ec4899' },
        { token: 'type', foreground: '3b82f6' },
        { token: 'class', foreground: 'ef4444' },
        { token: 'function', foreground: '06b6d4' },
        { token: 'variable', foreground: '1f2937' }
      ],
      colors: {
        'editor.background': '#ffffff',
        'editor.foreground': '#1f2937',
        'editor.lineHighlightBackground': '#f8fafc',
        'editor.selectionBackground': '#e0e7ff',
        'editor.inactiveSelectionBackground': '#f1f5f9',
        'editorCursor.foreground': '#8b5cf6',
        'editorWhitespace.foreground': '#e5e7eb'
      }
    });

    // PowerAutomation 暗色主题
    monaco.editor.defineTheme('powerautomation-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6b7280', fontStyle: 'italic' },
        { token: 'keyword', foreground: 'a78bfa', fontStyle: 'bold' },
        { token: 'string', foreground: '34d399' },
        { token: 'number', foreground: 'fbbf24' },
        { token: 'regexp', foreground: 'f472b6' },
        { token: 'type', foreground: '60a5fa' },
        { token: 'class', foreground: 'f87171' },
        { token: 'function', foreground: '22d3ee' },
        { token: 'variable', foreground: 'f9fafb' }
      ],
      colors: {
        'editor.background': '#1f2937',
        'editor.foreground': '#f9fafb',
        'editor.lineHighlightBackground': '#374151',
        'editor.selectionBackground': '#4c1d95',
        'editor.inactiveSelectionBackground': '#374151',
        'editorCursor.foreground': '#a78bfa',
        'editorWhitespace.foreground': '#4b5563'
      }
    });
  };

  // 注册快捷键
  const registerKeyBindings = (editor, monaco) => {
    // Ctrl+S 保存
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      handleSaveFile();
    });

    // Ctrl+Shift+P 命令面板
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyP, () => {
      editor.trigger('', 'editor.action.quickCommand');
    });

    // F12 跳转到定义
    editor.addCommand(monaco.KeyCode.F12, () => {
      editor.trigger('', 'editor.action.revealDefinition');
    });

    // Shift+F12 查找所有引用
    editor.addCommand(monaco.KeyMod.Shift | monaco.KeyCode.F12, () => {
      editor.trigger('', 'editor.action.goToReferences');
    });

    // Ctrl+Shift+F 格式化文档
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyF, () => {
      editor.trigger('', 'editor.action.formatDocument');
    });
  };

  // 初始化 LSP
  const initializeLSP = (editor, monaco) => {
    // 模拟 LSP 连接
    setLspState(prev => ({
      ...prev,
      isConnected: true,
      serverStatus: 'connected'
    }));

    // 注册诊断信息提供者
    const diagnosticsProvider = monaco.languages.registerCodeActionProvider('javascript', {
      provideCodeActions: (model, range, context) => {
        const diagnostics = context.markers.map(marker => ({
          title: `修复: ${marker.message}`,
          kind: 'quickfix',
          edit: {
            edits: [{
              resource: model.uri,
              edit: {
                range: marker,
                text: '// 已修复'
              }
            }]
          }
        }));
        return { actions: diagnostics, dispose: () => {} };
      }
    });

    // 注册悬停信息提供者
    const hoverProvider = monaco.languages.registerHoverProvider('javascript', {
      provideHover: (model, position) => {
        const word = model.getWordAtPosition(position);
        if (word) {
          return {
            range: new monaco.Range(position.lineNumber, word.startColumn, position.lineNumber, word.endColumn),
            contents: [
              { value: `**${word.word}**` },
              { value: `类型: ${getTypeInfo(word.word)}` },
              { value: `描述: ${getDescription(word.word)}` }
            ]
          };
        }
        return null;
      }
    });

    // 注册自动补全提供者
    const completionProvider = monaco.languages.registerCompletionItemProvider('javascript', {
      provideCompletionItems: (model, position) => {
        const word = model.getWordUntilPosition(position);
        const range = {
          startLineNumber: position.lineNumber,
          endLineNumber: position.lineNumber,
          startColumn: word.startColumn,
          endColumn: word.endColumn
        };

        const suggestions = [
          // React Hooks
          {
            label: 'useState',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'const [${1:state}, set${1/(.*)/${1:/capitalize}/}] = useState(${2:initialValue});',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'React Hook for state management',
            detail: 'React.useState',
            range: range
          },
          {
            label: 'useEffect',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'useEffect(() => {\n\t${1:// effect}\n\t${2:return () => {\n\t\t// cleanup\n\t};}\n}, [${3:dependencies}]);',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'React Hook for side effects',
            detail: 'React.useEffect',
            range: range
          },
          {
            label: 'useCallback',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'const ${1:memoizedCallback} = useCallback(\n\t(${2:params}) => {\n\t\t${3:// callback logic}\n\t},\n\t[${4:dependencies}]\n);',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'React Hook for memoizing callbacks',
            detail: 'React.useCallback',
            range: range
          },
          {
            label: 'useMemo',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'const ${1:memoizedValue} = useMemo(() => {\n\t${2:// expensive calculation}\n\treturn ${3:value};\n}, [${4:dependencies}]);',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'React Hook for memoizing values',
            detail: 'React.useMemo',
            range: range
          },
          {
            label: 'useRef',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'const ${1:ref} = useRef(${2:initialValue});',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'React Hook for creating refs',
            detail: 'React.useRef',
            range: range
          },
          {
            label: 'useContext',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'const ${1:value} = useContext(${2:Context});',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'React Hook for consuming context',
            detail: 'React.useContext',
            range: range
          },
          {
            label: 'useReducer',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'const [${1:state}, ${2:dispatch}] = useReducer(${3:reducer}, ${4:initialState});',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'React Hook for state management with reducer',
            detail: 'React.useReducer',
            range: range
          },

          // React Component Templates
          {
            label: 'rfc',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'import React from \'react\';\n\nconst ${1:ComponentName} = (${2:props}) => {\n\treturn (\n\t\t<div>\n\t\t\t${3:// component content}\n\t\t</div>\n\t);\n};\n\nexport default ${1:ComponentName};',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'React Functional Component template',
            detail: 'React Functional Component',
            range: range
          },
          {
            label: 'rfce',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'import React, { useState, useEffect } from \'react\';\n\nconst ${1:ComponentName} = () => {\n\tconst [${2:state}, set${2/(.*)/${1:/capitalize}/}] = useState(${3:initialValue});\n\n\tuseEffect(() => {\n\t\t${4:// effect logic}\n\t}, []);\n\n\treturn (\n\t\t<div>\n\t\t\t${5:// component content}\n\t\t</div>\n\t);\n};\n\nexport default ${1:ComponentName};',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'React Functional Component with hooks',
            detail: 'React Component with Hooks',
            range: range
          },

          // JavaScript Functions
          {
            label: 'function',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'function ${1:functionName}(${2:parameters}) {\n\t${3:// function body}\n\treturn ${4:value};\n}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Function declaration',
            detail: 'Function Declaration',
            range: range
          },
          {
            label: 'arrow',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'const ${1:functionName} = (${2:parameters}) => {\n\t${3:// function body}\n\treturn ${4:value};\n};',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Arrow function',
            detail: 'Arrow Function',
            range: range
          },
          {
            label: 'async',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'const ${1:functionName} = async (${2:parameters}) => {\n\ttry {\n\t\t${3:// async logic}\n\t\tconst result = await ${4:asyncOperation};\n\t\treturn result;\n\t} catch (error) {\n\t\tconsole.error(\'Error:\', error);\n\t\tthrow error;\n\t}\n};',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Async function with error handling',
            detail: 'Async Function',
            range: range
          },

          // Console methods
          {
            label: 'console.log',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'console.log(${1:value});',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Log output to console',
            detail: 'console.log',
            range: range
          },
          {
            label: 'console.error',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'console.error(${1:error});',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Log error to console',
            detail: 'console.error',
            range: range
          },
          {
            label: 'console.warn',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'console.warn(${1:warning});',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Log warning to console',
            detail: 'console.warn',
            range: range
          },

          // Common patterns
          {
            label: 'try-catch',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'try {\n\t${1:// try block}\n} catch (${2:error}) {\n\t${3:// error handling}\n\tconsole.error(\'Error:\', ${2:error});\n}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Try-catch block',
            detail: 'Try-Catch',
            range: range
          },
          {
            label: 'if-else',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'if (${1:condition}) {\n\t${2:// if block}\n} else {\n\t${3:// else block}\n}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'If-else statement',
            detail: 'If-Else',
            range: range
          },
          {
            label: 'for-loop',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'for (let ${1:i} = 0; ${1:i} < ${2:length}; ${1:i}++) {\n\t${3:// loop body}\n}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'For loop',
            detail: 'For Loop',
            range: range
          },
          {
            label: 'for-of',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'for (const ${1:item} of ${2:array}) {\n\t${3:// loop body}\n}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'For-of loop',
            detail: 'For-Of Loop',
            range: range
          },
          {
            label: 'for-in',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'for (const ${1:key} in ${2:object}) {\n\tif (${2:object}.hasOwnProperty(${1:key})) {\n\t\t${3:// loop body}\n\t}\n}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'For-in loop with hasOwnProperty check',
            detail: 'For-In Loop',
            range: range
          },

          // Array methods
          {
            label: 'map',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'map((${1:item}, ${2:index}) => {\n\treturn ${3:transformedItem};\n})',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Array map method',
            detail: 'Array.prototype.map',
            range: range
          },
          {
            label: 'filter',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'filter((${1:item}) => ${2:condition})',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Array filter method',
            detail: 'Array.prototype.filter',
            range: range
          },
          {
            label: 'reduce',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'reduce((${1:acc}, ${2:item}) => {\n\treturn ${3:newAcc};\n}, ${4:initialValue})',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Array reduce method',
            detail: 'Array.prototype.reduce',
            range: range
          },
          {
            label: 'forEach',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'forEach((${1:item}, ${2:index}) => {\n\t${3:// iteration logic}\n})',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Array forEach method',
            detail: 'Array.prototype.forEach',
            range: range
          },

          // Promise patterns
          {
            label: 'promise',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'new Promise((${1:resolve}, ${2:reject}) => {\n\t${3:// promise logic}\n\tif (${4:condition}) {\n\t\t${1:resolve}(${5:value});\n\t} else {\n\t\t${2:reject}(${6:error});\n\t}\n})',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Promise constructor',
            detail: 'Promise',
            range: range
          },
          {
            label: 'then-catch',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: '.then((${1:result}) => {\n\t${2:// success handling}\n})\n.catch((${3:error}) => {\n\t${4:// error handling}\n\tconsole.error(\'Error:\', ${3:error});\n});',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Promise then-catch chain',
            detail: 'Promise Chain',
            range: range
          },

          // Import/Export
          {
            label: 'import',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'import ${1:name} from \'${2:module}\';',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Import statement',
            detail: 'Import',
            range: range
          },
          {
            label: 'import-destructure',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'import { ${1:name} } from \'${2:module}\';',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Import with destructuring',
            detail: 'Import Destructuring',
            range: range
          },
          {
            label: 'export',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'export default ${1:name};',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Export default',
            detail: 'Export Default',
            range: range
          },
          {
            label: 'export-named',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'export { ${1:name} };',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Named export',
            detail: 'Named Export',
            range: range
          }
        ];

        return { suggestions };
      },
      triggerCharacters: ['.', ' ', '(', '{', '[', '"', "'", '`']
    });

    // 存储提供者引用以便清理
    setLspState(prev => ({
      ...prev,
      providers: [diagnosticsProvider, hoverProvider, completionProvider]
    }));
  };

  // 设置编辑器事件
  const setupEditorEvents = (editor, monaco) => {
    // 内容变化事件
    editor.onDidChangeModelContent(() => {
      const content = editor.getValue();
      setEditorState(prev => ({
        ...prev,
        content,
        modified: true
      }));
      
      // 更新当前文件
      setFileManager(prev => ({
        ...prev,
        openFiles: prev.openFiles.map((file, index) => 
          index === prev.activeFileIndex 
            ? { ...file, content, modified: true }
            : file
        )
      }));

      // 模拟实时诊断
      setTimeout(() => {
        const model = editor.getModel();
        const diagnostics = performDiagnostics(content);
        monaco.editor.setModelMarkers(model, 'javascript', diagnostics);
        setLspState(prev => ({ ...prev, diagnostics }));
      }, 500);
    });

    // 光标位置变化事件
    editor.onDidChangeCursorPosition((e) => {
      setEditorState(prev => ({
        ...prev,
        cursorPosition: { line: e.position.lineNumber, column: e.position.column }
      }));
    });

    // 选择变化事件
    editor.onDidChangeCursorSelection((e) => {
      setEditorState(prev => ({
        ...prev,
        selections: [e.selection]
      }));
    });
  };

  // 辅助函数
  const getTypeInfo = (word) => {
    const typeMap = {
      'useState': 'React Hook',
      'useEffect': 'React Hook',
      'console': 'Global Object',
      'function': 'Keyword',
      'const': 'Keyword',
      'let': 'Keyword',
      'var': 'Keyword'
    };
    return typeMap[word] || 'Variable';
  };

  const getDescription = (word) => {
    const descMap = {
      'useState': '用于在函数组件中添加状态',
      'useEffect': '用于处理副作用',
      'console': '浏览器控制台对象',
      'function': '函数声明关键字'
    };
    return descMap[word] || '用户定义的标识符';
  };

  const performDiagnostics = (content) => {
    const diagnostics = [];
    const lines = content.split('\n');
    
    lines.forEach((line, index) => {
      const lineNumber = index + 1;
      const trimmedLine = line.trim();
      
      // 语法检查
      // 检查未闭合的括号
      const openBrackets = (line.match(/\(/g) || []).length;
      const closeBrackets = (line.match(/\)/g) || []).length;
      if (openBrackets > closeBrackets && !line.includes('//')) {
        diagnostics.push({
          startLineNumber: lineNumber,
          startColumn: line.lastIndexOf('(') + 1,
          endLineNumber: lineNumber,
          endColumn: line.length + 1,
          message: '可能缺少闭合括号',
          severity: monaco.languages.MarkerSeverity.Warning
        });
      }
      
      // 检查未闭合的花括号
      const openBraces = (line.match(/\{/g) || []).length;
      const closeBraces = (line.match(/\}/g) || []).length;
      if (openBraces > closeBraces && !line.includes('//')) {
        diagnostics.push({
          startLineNumber: lineNumber,
          startColumn: line.lastIndexOf('{') + 1,
          endLineNumber: lineNumber,
          endColumn: line.length + 1,
          message: '可能缺少闭合花括号',
          severity: monaco.languages.MarkerSeverity.Warning
        });
      }
      
      // 检查未使用的变量
      if (trimmedLine.startsWith('const ') || trimmedLine.startsWith('let ') || trimmedLine.startsWith('var ')) {
        const varMatch = trimmedLine.match(/(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)/);
        if (varMatch) {
          const varName = varMatch[1];
          const restOfCode = lines.slice(index + 1).join('\n');
          if (!restOfCode.includes(varName) && !['useState', 'useEffect', 'useCallback', 'useMemo'].some(hook => trimmedLine.includes(hook))) {
            diagnostics.push({
              startLineNumber: lineNumber,
              startColumn: line.indexOf(varName) + 1,
              endLineNumber: lineNumber,
              endColumn: line.indexOf(varName) + varName.length + 1,
              message: `变量 '${varName}' 已声明但未使用`,
              severity: monaco.languages.MarkerSeverity.Info
            });
          }
        }
      }
      
      // 检查缺少分号
      if (trimmedLine && 
          !trimmedLine.endsWith(';') && 
          !trimmedLine.endsWith('{') && 
          !trimmedLine.endsWith('}') && 
          !trimmedLine.endsWith(',') &&
          !trimmedLine.startsWith('//') &&
          !trimmedLine.startsWith('/*') &&
          !trimmedLine.includes('if ') &&
          !trimmedLine.includes('for ') &&
          !trimmedLine.includes('while ') &&
          !trimmedLine.includes('function ') &&
          !trimmedLine.includes('class ') &&
          !trimmedLine.includes('import ') &&
          !trimmedLine.includes('export ') &&
          !trimmedLine.includes('return ') &&
          trimmedLine.length > 0) {
        diagnostics.push({
          startLineNumber: lineNumber,
          startColumn: line.length,
          endLineNumber: lineNumber,
          endColumn: line.length + 1,
          message: '建议添加分号',
          severity: monaco.languages.MarkerSeverity.Info
        });
      }
      
      // React 特定检查
      // 检查 useState 使用
      if (trimmedLine.includes('useState') && !trimmedLine.includes('const [')) {
        diagnostics.push({
          startLineNumber: lineNumber,
          startColumn: line.indexOf('useState') + 1,
          endLineNumber: lineNumber,
          endColumn: line.indexOf('useState') + 8,
          message: '建议使用解构赋值: const [state, setState] = useState()',
          severity: monaco.languages.MarkerSeverity.Info
        });
      }
      
      // 检查 useEffect 依赖
      if (trimmedLine.includes('useEffect') && !trimmedLine.includes('[') && !line.includes('//')) {
        diagnostics.push({
          startLineNumber: lineNumber,
          startColumn: line.indexOf('useEffect') + 1,
          endLineNumber: lineNumber,
          endColumn: line.indexOf('useEffect') + 9,
          message: 'useEffect 缺少依赖数组',
          severity: monaco.languages.MarkerSeverity.Warning
        });
      }
      
      // 检查 console.log 在生产代码中
      if (trimmedLine.includes('console.log') && !line.includes('//')) {
        diagnostics.push({
          startLineNumber: lineNumber,
          startColumn: line.indexOf('console.log') + 1,
          endLineNumber: lineNumber,
          endColumn: line.indexOf('console.log') + 11,
          message: '生产代码中应避免使用 console.log',
          severity: monaco.languages.MarkerSeverity.Info
        });
      }
      
      // 检查 == 而不是 ===
      if (trimmedLine.includes(' == ') && !trimmedLine.includes('===')) {
        diagnostics.push({
          startLineNumber: lineNumber,
          startColumn: line.indexOf(' == ') + 2,
          endLineNumber: lineNumber,
          endColumn: line.indexOf(' == ') + 4,
          message: '建议使用严格相等 === 而不是 ==',
          severity: monaco.languages.MarkerSeverity.Warning
        });
      }
      
      // 检查 != 而不是 !==
      if (trimmedLine.includes(' != ') && !trimmedLine.includes('!==')) {
        diagnostics.push({
          startLineNumber: lineNumber,
          startColumn: line.indexOf(' != ') + 2,
          endLineNumber: lineNumber,
          endColumn: line.indexOf(' != ') + 4,
          message: '建议使用严格不等 !== 而不是 !=',
          severity: monaco.languages.MarkerSeverity.Warning
        });
      }
      
      // 检查空的 catch 块
      if (trimmedLine.includes('} catch (') && index + 1 < lines.length) {
        const nextLine = lines[index + 1].trim();
        if (nextLine === '}' || (nextLine === '' && index + 2 < lines.length && lines[index + 2].trim() === '}')) {
          diagnostics.push({
            startLineNumber: lineNumber,
            startColumn: line.indexOf('catch') + 1,
            endLineNumber: lineNumber,
            endColumn: line.indexOf('catch') + 5,
            message: '空的 catch 块，建议添加错误处理逻辑',
            severity: monaco.languages.MarkerSeverity.Warning
          });
        }
      }
      
      // 检查函数命名规范
      const functionMatch = trimmedLine.match(/function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)/);
      if (functionMatch) {
        const funcName = functionMatch[1];
        if (funcName[0] === funcName[0].toUpperCase() && !trimmedLine.includes('function Component')) {
          diagnostics.push({
            startLineNumber: lineNumber,
            startColumn: line.indexOf(funcName) + 1,
            endLineNumber: lineNumber,
            endColumn: line.indexOf(funcName) + funcName.length + 1,
            message: '函数名建议使用小驼峰命名法',
            severity: monaco.languages.MarkerSeverity.Info
          });
        }
      }
      
      // 检查组件命名规范
      const componentMatch = trimmedLine.match(/const\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=.*=>/);
      if (componentMatch && trimmedLine.includes('return (')) {
        const compName = componentMatch[1];
        if (compName[0] !== compName[0].toUpperCase()) {
          diagnostics.push({
            startLineNumber: lineNumber,
            startColumn: line.indexOf(compName) + 1,
            endLineNumber: lineNumber,
            endColumn: line.indexOf(compName) + compName.length + 1,
            message: 'React 组件名应以大写字母开头',
            severity: monaco.languages.MarkerSeverity.Warning
          });
        }
      }
      
      // 检查异步函数中缺少 await
      if (trimmedLine.includes('async ') && content.includes('Promise') && !content.includes('await')) {
        diagnostics.push({
          startLineNumber: lineNumber,
          startColumn: line.indexOf('async') + 1,
          endLineNumber: lineNumber,
          endColumn: line.indexOf('async') + 5,
          message: '异步函数中可能缺少 await 关键字',
          severity: monaco.languages.MarkerSeverity.Info
        });
      }
      
      // 检查长行
      if (line.length > 120) {
        diagnostics.push({
          startLineNumber: lineNumber,
          startColumn: 121,
          endLineNumber: lineNumber,
          endColumn: line.length + 1,
          message: '行长度超过 120 字符，建议换行',
          severity: monaco.languages.MarkerSeverity.Info
        });
      }
      
      // 检查重复的 import
      if (trimmedLine.startsWith('import ')) {
        const importMatch = trimmedLine.match(/from\s+['"]([^'"]+)['"]/);
        if (importMatch) {
          const moduleName = importMatch[1];
          const otherImports = lines.filter((l, i) => i !== index && l.includes(`from '${moduleName}'`) || l.includes(`from "${moduleName}"`));
          if (otherImports.length > 0) {
            diagnostics.push({
              startLineNumber: lineNumber,
              startColumn: 1,
              endLineNumber: lineNumber,
              endColumn: line.length + 1,
              message: `重复导入模块 '${moduleName}'，建议合并导入`,
              severity: monaco.languages.MarkerSeverity.Info
            });
          }
        }
      }
      
      // 检查 TODO 和 FIXME 注释
      if (trimmedLine.includes('TODO') || trimmedLine.includes('FIXME')) {
        diagnostics.push({
          startLineNumber: lineNumber,
          startColumn: line.indexOf(trimmedLine.includes('TODO') ? 'TODO' : 'FIXME') + 1,
          endLineNumber: lineNumber,
          endColumn: line.length + 1,
          message: trimmedLine.includes('TODO') ? '待办事项' : '需要修复',
          severity: monaco.languages.MarkerSeverity.Info
        });
      }
    });
    
    return diagnostics;
  };

  // 文件操作函数
  const handleSaveFile = useCallback(() => {
    const currentFile = fileManager.openFiles[fileManager.activeFileIndex];
    console.log(`保存文件: ${currentFile.name}`);
    
    setFileManager(prev => ({
      ...prev,
      openFiles: prev.openFiles.map((file, index) => 
        index === prev.activeFileIndex 
          ? { ...file, modified: false }
          : file
      )
    }));
    
    setEditorState(prev => ({ ...prev, modified: false }));
  }, [fileManager.activeFileIndex, fileManager.openFiles]);

  const handleRunCode = useCallback(() => {
    const content = editorRef.current?.getValue();
    console.log('运行代码:', content);
    // 这里可以集成代码执行功能
  }, []);

  const handleFormatCode = useCallback(() => {
    if (editorRef.current) {
      editorRef.current.trigger('', 'editor.action.formatDocument');
    }
  }, []);

  const switchFile = useCallback((index) => {
    const file = fileManager.openFiles[index];
    setFileManager(prev => ({ ...prev, activeFileIndex: index }));
    setEditorState(prev => ({
      ...prev,
      content: file.content,
      language: file.language,
      fileName: file.name,
      modified: file.modified
    }));
    
    if (editorRef.current && monacoRef.current) {
      const model = monacoRef.current.editor.createModel(file.content, file.language);
      editorRef.current.setModel(model);
    }
  }, [fileManager.openFiles]);

  const toggleTheme = useCallback(() => {
    const newTheme = editorState.theme === 'powerautomation-light' ? 'powerautomation-dark' : 'powerautomation-light';
    setEditorState(prev => ({ ...prev, theme: newTheme }));
    if (monacoRef.current) {
      monacoRef.current.editor.setTheme(newTheme);
    }
  }, [editorState.theme]);

  if (!isVisible) return null;

  return (
    <div className="monaco-editor-modal">
      <div className="monaco-editor-container">
        {/* 编辑器头部 */}
        <div className="monaco-header">
          <div className="header-left">
            <h3>📝 Monaco Editor with LSP</h3>
            <div className="lsp-status">
              <span className={`lsp-indicator ${lspState.isConnected ? 'connected' : 'disconnected'}`}></span>
              <span>LSP: {lspState.serverStatus}</span>
            </div>
          </div>
          <div className="header-right">
            <div className="editor-stats">
              <span>行: {editorState.cursorPosition.line}</span>
              <span>列: {editorState.cursorPosition.column}</span>
              <span>语言: {editorState.language}</span>
            </div>
            <button className="theme-toggle-btn" onClick={toggleTheme}>
              {editorState.theme === 'powerautomation-light' ? '🌙' : '☀️'}
            </button>
            <button className="close-btn" onClick={onClose}>✖️</button>
          </div>
        </div>

        {/* 文件标签栏 */}
        <div className="file-tabs">
          {fileManager.openFiles.map((file, index) => (
            <div 
              key={index}
              className={`file-tab ${index === fileManager.activeFileIndex ? 'active' : ''} ${file.modified ? 'modified' : ''}`}
              onClick={() => switchFile(index)}
            >
              <span className="file-icon">
                {file.language === 'javascript' && '📄'}
                {file.language === 'css' && '🎨'}
                {file.language === 'json' && '⚙️'}
              </span>
              <span className="file-name">{file.name}</span>
              {file.modified && <span className="modified-indicator">●</span>}
            </div>
          ))}
        </div>

        {/* 编辑器主体 */}
        <div className="monaco-body">
          <div className="editor-area">
            <Editor
              height="100%"
              language={editorState.language}
              theme={editorState.theme}
              value={editorState.content}
              options={editorOptions}
              onMount={handleEditorDidMount}
            />
          </div>
          
          {/* 侧边面板 */}
          <div className="side-panel">
            {/* 诊断信息 */}
            <div className="panel-section">
              <h4>🔍 诊断信息</h4>
              <div className="diagnostics-list">
                {lspState.diagnostics.length === 0 ? (
                  <div className="no-issues">无问题</div>
                ) : (
                  lspState.diagnostics.map((diagnostic, index) => (
                    <div key={index} className={`diagnostic-item ${diagnostic.severity === 8 ? 'error' : diagnostic.severity === 4 ? 'warning' : 'info'}`}>
                      <span className="diagnostic-line">行 {diagnostic.startLineNumber}</span>
                      <span className="diagnostic-message">{diagnostic.message}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* 大纲视图 */}
            <div className="panel-section">
              <h4>📋 大纲</h4>
              <div className="outline-list">
                <div className="outline-item">
                  <span className="outline-icon">🔧</span>
                  <span>ExampleComponent</span>
                </div>
                <div className="outline-item">
                  <span className="outline-icon">⚡</span>
                  <span>handleDataFetch</span>
                </div>
                <div className="outline-item">
                  <span className="outline-icon">📦</span>
                  <span>useState</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 编辑器底部 */}
        <div className="monaco-footer">
          <div className="footer-left">
            <div className="editor-info">
              <span>文件: {editorState.fileName}</span>
              <span>大小: {editorState.content.length} 字符</span>
              <span>行数: {editorState.content.split('\n').length}</span>
              {editorState.modified && <span className="modified-status">● 已修改</span>}
            </div>
          </div>
          <div className="footer-right">
            <button className="footer-btn" onClick={handleSaveFile}>
              💾 保存 (Ctrl+S)
            </button>
            <button className="footer-btn" onClick={handleRunCode}>
              ▶️ 运行
            </button>
            <button className="footer-btn" onClick={handleFormatCode}>
              🔧 格式化 (Ctrl+Shift+F)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MonacoEditorComponent;


import React from 'react';

interface MonacoEditorProps {
  value?: string;
  language?: string;
  theme?: string;
  onChange?: (value: string) => void;
  onSave?: (value: string) => void;
  readOnly?: boolean;
  height?: string | number;
  width?: string | number;
  className?: string;
}

declare const MonacoEditor: React.FC<MonacoEditorProps>;
export default MonacoEditor;


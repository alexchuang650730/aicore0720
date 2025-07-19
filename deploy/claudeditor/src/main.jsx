import React from 'react'
import ReactDOM from 'react-dom/client'
import SmartUILayout from './components/SmartUILayout.jsx'
import './index.css'

// 删除 Made with Manus 元素的函数
const removeManusElements = () => {
  const manusElements = document.querySelectorAll('make-with-manus, [class*="manus"], [id*="manus"]');
  manusElements.forEach((el) => {
    if (el.textContent && el.textContent.includes('Made with Manus')) {
      el.remove();
    }
  });
  return manusElements.length;
};

// 页面加载完成后删除 Manus 元素
document.addEventListener('DOMContentLoaded', () => {
  // 立即删除
  removeManusElements();
  
  // 设置监听器删除动态添加的元素
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1) {
          // 检查节点本身
          if (node.tagName === 'MAKE-WITH-MANUS' || 
              (node.className && node.className.toString().includes('manus')) ||
              (node.id && node.id.includes('manus'))) {
            if (node.textContent && node.textContent.includes('Made with Manus')) {
              node.remove();
            }
          }
          
          // 检查子元素
          if (node.querySelectorAll) {
            const childManus = node.querySelectorAll('make-with-manus, [class*="manus"], [id*="manus"]');
            childManus.forEach(el => {
              if (el.textContent && el.textContent.includes('Made with Manus')) {
                el.remove();
              }
            });
          }
        }
      });
    });
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  // 定期检查并删除
  setInterval(removeManusElements, 1000);
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <SmartUILayout />
  </React.StrictMode>,
)


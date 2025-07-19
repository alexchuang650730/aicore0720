import React, { useState, useEffect } from 'react';
import testService from '../services/TestService';
import './TestPanel.css';

const TestPanel = () => {
  const [testSuites, setTestSuites] = useState([]);
  const [selectedSuite, setSelectedSuite] = useState(null);
  const [testResults, setTestResults] = useState([]);
  const [runningTests, setRunningTests] = useState(new Set());
  const [statistics, setStatistics] = useState({});
  const [coverage, setCoverage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // 初始化数据
    loadTestSuites();
    loadStatistics();
    
    // 设置实时更新监听
    const handleTestUpdate = (data) => {
      switch (data.type) {
        case 'test_completed':
          setRunningTests(prev => {
            const newSet = new Set(prev);
            newSet.delete(data.testId);
            return newSet;
          });
          loadTestResults();
          loadStatistics();
          break;
        case 'test_started':
          setRunningTests(prev => new Set(prev).add(data.testId));
          break;
        case 'tests_updated':
          loadTestResults();
          break;
      }
    };
    
    testService.addObserver(handleTestUpdate);
    
    return () => {
      testService.removeObserver(handleTestUpdate);
    };
  }, []);

  const loadTestSuites = () => {
    const suites = testService.getTestSuites();
    setTestSuites(suites);
    if (suites.length > 0 && !selectedSuite) {
      setSelectedSuite(suites[0]);
    }
  };

  const loadTestResults = () => {
    const results = testService.getAllTestResults();
    setTestResults(results);
  };

  const loadStatistics = () => {
    const stats = testService.getTestStatistics();
    setStatistics(stats);
  };

  const loadCoverage = async (suiteId) => {
    const coverageData = await testService.getTestCoverage(suiteId);
    setCoverage(coverageData);
  };

  const handleRunTestSuite = async (suiteId) => {
    setIsLoading(true);
    try {
      await testService.runTestSuite(suiteId);
      loadCoverage(suiteId);
    } catch (error) {
      console.error('运行测试套件失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunTestCase = async (testId) => {
    try {
      await testService.runTestCase(testId);
    } catch (error) {
      console.error('运行测试用例失败:', error);
    }
  };

  const handleStopTest = async (testId) => {
    await testService.stopTest(testId);
  };

  const handleGenerateReport = async (suiteId) => {
    await testService.generateTestReport(suiteId, 'html');
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'passed':
        return '✅';
      case 'failed':
      case 'error':
        return '❌';
      case 'running':
        return '🔄';
      case 'pending':
        return '⏳';
      case 'skipped':
        return '⏭️';
      default:
        return '❓';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'passed':
        return '#28a745';
      case 'failed':
      case 'error':
        return '#dc3545';
      case 'running':
        return '#007bff';
      case 'pending':
        return '#ffc107';
      case 'skipped':
        return '#6c757d';
      default:
        return '#6c757d';
    }
  };

  return (
    <div className="test-panel">
      <div className="test-panel-header">
        <h3>🧪 测试管理面板</h3>
        <div className="test-statistics">
          <div className="stat-item">
            <span className="stat-label">总计:</span>
            <span className="stat-value">{statistics.total || 0}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">通过:</span>
            <span className="stat-value passed">{statistics.passed || 0}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">失败:</span>
            <span className="stat-value failed">{statistics.failed || 0}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">运行中:</span>
            <span className="stat-value running">{statistics.running || 0}</span>
          </div>
        </div>
      </div>

      <div className="test-panel-content">
        <div className="test-suites-section">
          <h4>测试套件</h4>
          <div className="test-suites-list">
            {testSuites.map(suite => (
              <div 
                key={suite.id} 
                className={`test-suite-item ${selectedSuite?.id === suite.id ? 'selected' : ''}`}
                onClick={() => setSelectedSuite(suite)}
              >
                <div className="suite-header">
                  <span className="suite-name">{suite.name}</span>
                  <div className="suite-actions">
                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRunTestSuite(suite.id);
                      }}
                      disabled={isLoading}
                    >
                      {isLoading ? '运行中...' : '运行'}
                    </button>
                    <button 
                      className="btn btn-secondary btn-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleGenerateReport(suite.id);
                      }}
                    >
                      报告
                    </button>
                  </div>
                </div>
                <div className="suite-description">{suite.description}</div>
                <div className="suite-stats">
                  测试用例: {suite.testCases?.length || 0}
                </div>
              </div>
            ))}
          </div>
        </div>

        {selectedSuite && (
          <div className="test-cases-section">
            <h4>测试用例 - {selectedSuite.name}</h4>
            <div className="test-cases-list">
              {selectedSuite.testCases?.map(testCase => {
                const result = testService.getTestResult(testCase.id);
                const isRunning = runningTests.has(testCase.id);
                const status = isRunning ? 'running' : (result?.status || 'pending');
                
                return (
                  <div key={testCase.id} className="test-case-item">
                    <div className="test-case-header">
                      <span className="test-status" style={{ color: getStatusColor(status) }}>
                        {getStatusIcon(status)}
                      </span>
                      <span className="test-name">{testCase.name}</span>
                      <span className="test-type">{testCase.testType}</span>
                      <div className="test-actions">
                        {isRunning ? (
                          <button 
                            className="btn btn-danger btn-sm"
                            onClick={() => handleStopTest(testCase.id)}
                          >
                            停止
                          </button>
                        ) : (
                          <button 
                            className="btn btn-primary btn-sm"
                            onClick={() => handleRunTestCase(testCase.id)}
                          >
                            运行
                          </button>
                        )}
                      </div>
                    </div>
                    
                    {result && (
                      <div className="test-result">
                        <div className="result-info">
                          <span>执行时间: {result.executionTime?.toFixed(2) || 0}ms</span>
                          <span>开始时间: {new Date(result.startTime).toLocaleTimeString()}</span>
                        </div>
                        {result.errorMessage && (
                          <div className="error-message">
                            错误: {result.errorMessage}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {coverage && (
          <div className="coverage-section">
            <h4>测试覆盖率</h4>
            <div className="coverage-metrics">
              <div className="coverage-item">
                <span className="coverage-label">行覆盖率:</span>
                <div className="coverage-bar">
                  <div 
                    className="coverage-fill" 
                    style={{ width: `${coverage.lines}%` }}
                  ></div>
                  <span className="coverage-text">{coverage.lines}%</span>
                </div>
              </div>
              <div className="coverage-item">
                <span className="coverage-label">函数覆盖率:</span>
                <div className="coverage-bar">
                  <div 
                    className="coverage-fill" 
                    style={{ width: `${coverage.functions}%` }}
                  ></div>
                  <span className="coverage-text">{coverage.functions}%</span>
                </div>
              </div>
              <div className="coverage-item">
                <span className="coverage-label">分支覆盖率:</span>
                <div className="coverage-bar">
                  <div 
                    className="coverage-fill" 
                    style={{ width: `${coverage.branches}%` }}
                  ></div>
                  <span className="coverage-text">{coverage.branches}%</span>
                </div>
              </div>
              <div className="coverage-item">
                <span className="coverage-label">语句覆盖率:</span>
                <div className="coverage-bar">
                  <div 
                    className="coverage-fill" 
                    style={{ width: `${coverage.statements}%` }}
                  ></div>
                  <span className="coverage-text">{coverage.statements}%</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TestPanel;


import sys
import os
# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import json
from finance.analyze_financial_strategy import FinancialStrategyAnalyzer
from finance.rl.optimizers.strategy_optimizer import StrategyOptimizer, FinancialEnvironment, DQNAgent
from finance.data_utils import prepare_data

def test_strategy_analyzer():
    print("\n=== Testing FinancialStrategyAnalyzer ===")
    try:
        analyzer = FinancialStrategyAnalyzer()
        analyzer.load_strategy_dataset("/root/autodl-tmp/FinancialStrategy2Code/datasets/merged_strategy_dataset.json")
        print("✓ Dataset loaded successfully")

        # 测试策略模式提取
        patterns = analyzer.extract_strategy_patterns()
        print("✓ Strategy patterns extracted:", patterns.keys())

        # 测试风险管理分析
        test_code = """
        def strategy():
            stop_loss = 0.05
            position_size = calculate_position()
            if price < stop_loss_price:
                close_position()
        """
        risk_features = analyzer.analyze_risk_management(test_code)
        print("✓ Risk management analysis:", risk_features)

        # 测试强化学习特征生成
        rl_features = analyzer.generate_reinforcement_learning_features(test_code)
        print("✓ RL features generated:", rl_features)

        return True
    except Exception as e:
        print("✗ FinancialStrategyAnalyzer test failed:", str(e))
        return False

def test_rl_components():
    print("\n=== Testing RL Components ===")
    try:
        # 创建示例数据
        n_samples = 1000
        n_features = 3
        historical_data = np.random.randn(n_samples, n_features)
        print("✓ Test data created")

        # 测试数据准备
        features, state_size, action_size = prepare_data(historical_data)
        print(f"✓ Data prepared - Features shape: {features.shape}, State size: {state_size}, Action size: {action_size}")

        # 测试金融环境
        env = FinancialEnvironment(features)
        initial_state = env.reset()
        print(f"✓ Environment initialized - State shape: {initial_state.shape}")

        # 测试智能体
        agent = DQNAgent(state_size=len(initial_state), action_size=action_size)
        print("✓ Agent initialized")

        # 测试一个简单的交互
        state = np.asarray(initial_state, dtype=np.float32).flatten()
        action = agent.act(state)
        next_state, reward, done, info = env.step(action)
        next_state = np.asarray(next_state, dtype=np.float32).flatten()
        print(f"✓ Environment step completed - Action: {action}, Reward: {reward}")

        # 测试记忆和回放
        agent.remember(state, action, reward, next_state, done)
        loss = agent.replay(batch_size=1)
        print(f"✓ Memory and replay tested - Loss: {loss}")

        return True
    except Exception as e:
        print("✗ RL components test failed:", str(e))
        return False

def test_strategy_optimizer():
    print("\n=== Testing StrategyOptimizer ===")
    try:
        n_samples = 1000
        n_features = 3
        historical_data = np.random.randn(n_samples, n_features)
        features, state_size, action_size = prepare_data(historical_data)
        optimizer = StrategyOptimizer(features, action_size)
        print("✓ Optimizer initialized")
        optimizer.episodes = 2
        rewards = optimizer.train()
        print(f"✓ Training completed - Final reward: {rewards[-1]}")
        test_state = features[0].flatten()
        actions = optimizer.get_optimal_actions(test_state)
        print(f"✓ Optimal actions generated - First action: {actions[0]}")
        return True
    except Exception as e:
        print("✗ StrategyOptimizer test failed:", str(e))
        return False

def run_all_tests():
    print("Starting all tests...")
    
    results = {
        "StrategyAnalyzer": test_strategy_analyzer(),
        "RLComponents": test_rl_components(),
        "StrategyOptimizer": test_strategy_optimizer()
    }
    
    print("\n=== Test Results ===")
    for test_name, passed in results.items():
        print(f"{test_name}: {'✓ PASSED' if passed else '✗ FAILED'}")
    
    return all(results.values())

if __name__ == "__main__":
    success = run_all_tests()
    print(f"\nOverall test result: {'✓ ALL TESTS PASSED' if success else '✗ SOME TESTS FAILED'}")

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import nashpy as nash
from scipy.optimize import minimize, LinearConstraint
from loguru import logger
import json

class MarketRegime(Enum):
    BULL = "BULL"
    BEAR = "BEAR"
    SIDEWAYS = "SIDEWAYS"
    VOLATILE = "VOLATILE"

@dataclass
class MarketPlayer:
    """Represents a market participant"""
    name: str
    capital: float
    strategy_weights: Dict[str, float]  # Strategy name -> weight
    risk_tolerance: float  # 0-1
    market_impact: float  # How much they can move the market
    
@dataclass
class GameOutcome:
    """Result of a game theory simulation"""
    nash_equilibrium: np.ndarray
    expected_payoffs: Dict[str, float]
    optimal_strategies: Dict[str, Dict[str, float]]
    market_regime: MarketRegime
    confidence: float
    
class GameTheoryValidator:
    """
    Validates trading strategies using game theory principles
    Models the market as a multi-player game
    """
    
    def __init__(self):
        self.players = self._initialize_players()
        self.strategy_space = self._define_strategy_space()
        self.market_regimes = {}
        
    def _initialize_players(self) -> List[MarketPlayer]:
        """Initialize different types of market players"""
        return [
            MarketPlayer(
                name="Retail_Traders",
                capital=1e6,
                strategy_weights={"momentum": 0.7, "mean_reversion": 0.3},
                risk_tolerance=0.3,
                market_impact=0.1
            ),
            MarketPlayer(
                name="Institutional",
                capital=1e8,
                strategy_weights={"value": 0.5, "arbitrage": 0.3, "market_making": 0.2},
                risk_tolerance=0.5,
                market_impact=0.4
            ),
            MarketPlayer(
                name="Algo_Traders",
                capital=5e7,
                strategy_weights={"hft": 0.6, "stat_arb": 0.4},
                risk_tolerance=0.7,
                market_impact=0.3
            ),
            MarketPlayer(
                name="Market_Makers",
                capital=2e8,
                strategy_weights={"liquidity_provision": 0.8, "spread_capture": 0.2},
                risk_tolerance=0.4,
                market_impact=0.2
            )
        ]
    
    def _define_strategy_space(self) -> Dict[str, List[str]]:
        """Define possible strategies for each player type"""
        return {
            "actions": ["buy", "sell", "hold", "provide_liquidity"],
            "sizes": ["small", "medium", "large"],
            "timings": ["immediate", "scaled", "opportunistic"]
        }
    
    def detect_market_regime(self, market_data: pd.DataFrame) -> MarketRegime:
        """Detect current market regime using statistical methods"""
        if len(market_data) < 30:
            return MarketRegime.VOLATILE
        
        # Calculate metrics
        returns = market_data['close'].pct_change().dropna()
        volatility = returns.std()
        trend = (market_data['close'].iloc[-1] - market_data['close'].iloc[0]) / market_data['close'].iloc[0]
        
        # Moving averages
        sma_short = market_data['close'].rolling(10).mean().iloc[-1]
        sma_long = market_data['close'].rolling(30).mean().iloc[-1]
        
        # Classify regime
        if volatility > 0.05:  # High volatility
            return MarketRegime.VOLATILE
        elif trend > 0.1 and sma_short > sma_long:
            return MarketRegime.BULL
        elif trend < -0.1 and sma_short < sma_long:
            return MarketRegime.BEAR
        else:
            return MarketRegime.SIDEWAYS
    
    def calculate_payoff_matrix(self, 
                              market_data: pd.DataFrame,
                              player_actions: Dict[str, str],
                              market_regime: MarketRegime) -> np.ndarray:
        """Calculate payoff matrix for current market state"""
        n_players = len(self.players)
        
        # Initialize payoff matrix
        payoffs = np.zeros((n_players, n_players))
        
        # Calculate payoffs based on actions and market regime
        for i, player_i in enumerate(self.players):
            for j, player_j in enumerate(self.players):
                if i != j:
                    payoff = self._calculate_pairwise_payoff(
                        player_i, player_j,
                        player_actions.get(player_i.name, "hold"),
                        player_actions.get(player_j.name, "hold"),
                        market_regime, market_data
                    )
                    payoffs[i, j] = payoff
        
        return payoffs
    
    def _calculate_pairwise_payoff(self,
                                  player1: MarketPlayer,
                                  player2: MarketPlayer,
                                  action1: str,
                                  action2: str,
                                  regime: MarketRegime,
                                  market_data: pd.DataFrame) -> float:
        """Calculate payoff between two players given their actions"""
        base_payoff = 0
        
        # Market regime modifiers
        regime_modifiers = {
            MarketRegime.BULL: {"buy": 1.5, "sell": 0.5, "hold": 1.0},
            MarketRegime.BEAR: {"buy": 0.5, "sell": 1.5, "hold": 0.8},
            MarketRegime.SIDEWAYS: {"buy": 0.9, "sell": 0.9, "hold": 1.1},
            MarketRegime.VOLATILE: {"buy": 0.7, "sell": 0.7, "hold": 1.3}
        }
        
        # Action interactions
        if action1 == "buy" and action2 == "sell":
            # Opposing actions create opportunity
            base_payoff = 0.02 * regime_modifiers[regime]["buy"]
        elif action1 == action2 == "buy":
            # Competition reduces payoff
            base_payoff = -0.01 * player2.market_impact
        elif action1 == "provide_liquidity":
            # Liquidity providers earn from spreads
            volatility = market_data['close'].pct_change().std()
            base_payoff = 0.001 * volatility * 100
        
        # Adjust for player characteristics
        base_payoff *= player1.risk_tolerance
        base_payoff *= (1 - player2.market_impact)  # Larger players reduce opportunities
        
        return base_payoff
    
    def find_nash_equilibrium(self, payoff_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Find Nash equilibrium using nashpy"""
        try:
            game = nash.Game(payoff_matrix)
            equilibria = list(game.support_enumeration())
            
            if equilibria:
                # Return first equilibrium found
                return equilibria[0]
            else:
                # If no pure strategy equilibrium, compute mixed strategy
                n = payoff_matrix.shape[0]
                return np.ones(n) / n, np.ones(n) / n
                
        except Exception as e:
            logger.error(f"Error finding Nash equilibrium: {e}")
            n = payoff_matrix.shape[0]
            return np.ones(n) / n, np.ones(n) / n
    
    def validate_strategy(self,
                         strategy_name: str,
                         strategy_params: Dict[str, Any],
                         market_data: pd.DataFrame,
                         historical_performance: Optional[Dict] = None) -> Dict[str, Any]:
        """Validate a trading strategy using game theory"""
        
        # Detect market regime
        regime = self.detect_market_regime(market_data)
        
        # Simulate different player actions
        action_combinations = self._generate_action_combinations()
        
        results = []
        for actions in action_combinations:
            # Calculate payoff matrix
            payoff_matrix = self.calculate_payoff_matrix(market_data, actions, regime)
            
            # Find Nash equilibrium
            eq_strategy_1, eq_strategy_2 = self.find_nash_equilibrium(payoff_matrix)
            
            # Calculate expected payoffs
            expected_payoff = np.dot(eq_strategy_1, np.dot(payoff_matrix, eq_strategy_2))
            
            results.append({
                'actions': actions,
                'equilibrium': (eq_strategy_1, eq_strategy_2),
                'expected_payoff': expected_payoff
            })
        
        # Analyze results
        best_result = max(results, key=lambda x: x['expected_payoff'])
        worst_result = min(results, key=lambda x: x['expected_payoff'])
        
        # Calculate strategy robustness
        payoff_variance = np.var([r['expected_payoff'] for r in results])
        robustness_score = 1 / (1 + payoff_variance)  # Higher score = more robust
        
        # Evolutionary stability analysis
        ess_score = self._analyze_evolutionary_stability(
            strategy_params, market_data, regime
        )
        
        # Multi-player dynamics
        coalition_analysis = self._analyze_coalition_formation(
            self.players, strategy_params, regime
        )
        
        validation_result = {
            'strategy_name': strategy_name,
            'market_regime': regime.value,
            'nash_equilibrium': best_result['equilibrium'],
            'expected_payoff': best_result['expected_payoff'],
            'worst_case_payoff': worst_result['expected_payoff'],
            'robustness_score': robustness_score,
            'evolutionary_stability': ess_score,
            'coalition_risks': coalition_analysis,
            'recommendation': self._generate_recommendation(
                robustness_score, ess_score, best_result['expected_payoff']
            ),
            'optimal_position_size': self._calculate_optimal_position_size(
                payoff_variance, regime
            )
        }
        
        return validation_result
    
    def _generate_action_combinations(self) -> List[Dict[str, str]]:
        """Generate possible action combinations for players"""
        actions = ["buy", "sell", "hold"]
        combinations = []
        
        # Generate a subset of combinations (full cartesian product would be too large)
        for _ in range(10):
            combo = {}
            for player in self.players:
                combo[player.name] = np.random.choice(actions)
            combinations.append(combo)
        
        return combinations
    
    def _analyze_evolutionary_stability(self,
                                      strategy_params: Dict,
                                      market_data: pd.DataFrame,
                                      regime: MarketRegime) -> float:
        """Analyze if strategy is evolutionarily stable"""
        # Simulate strategy evolution over time
        generations = 100
        population_size = 1000
        mutation_rate = 0.01
        
        # Initialize population with random strategies
        population = np.random.rand(population_size, len(strategy_params))
        
        for gen in range(generations):
            # Calculate fitness for each strategy
            fitness = np.array([
                self._calculate_strategy_fitness(
                    individual, market_data, regime
                ) for individual in population
            ])
            
            # Selection
            probabilities = fitness / fitness.sum()
            selected_indices = np.random.choice(
                population_size, population_size, p=probabilities
            )
            population = population[selected_indices]
            
            # Mutation
            mask = np.random.rand(population_size, len(strategy_params)) < mutation_rate
            population[mask] += np.random.normal(0, 0.1, mask.sum())
            population = np.clip(population, 0, 1)
        
        # Calculate final diversity
        diversity = np.std(population, axis=0).mean()
        
        # Higher diversity means less stable
        stability_score = 1 / (1 + diversity)
        
        return stability_score
    
    def _calculate_strategy_fitness(self,
                                   strategy_vector: np.ndarray,
                                   market_data: pd.DataFrame,
                                   regime: MarketRegime) -> float:
        """Calculate fitness of a strategy in current market"""
        # Simple fitness function based on expected return and risk
        expected_return = np.random.normal(0.001, 0.01)  # Simplified
        risk = np.std(market_data['close'].pct_change()) * strategy_vector.sum()
        
        # Fitness = return - risk penalty
        fitness = expected_return - 0.5 * risk
        
        # Regime adjustments
        if regime == MarketRegime.BULL:
            fitness *= 1.2
        elif regime == MarketRegime.BEAR:
            fitness *= 0.8
        
        return max(0, fitness)
    
    def _analyze_coalition_formation(self,
                                   players: List[MarketPlayer],
                                   strategy_params: Dict,
                                   regime: MarketRegime) -> Dict[str, Any]:
        """Analyze potential coalition formations and their impact"""
        coalitions = []
        
        # Check pairwise coalitions
        for i, player1 in enumerate(players):
            for j, player2 in enumerate(players[i+1:], i+1):
                # Calculate coalition benefit
                individual_payoff = player1.capital * 0.01 + player2.capital * 0.01
                coalition_payoff = (player1.capital + player2.capital) * 0.012
                
                if coalition_payoff > individual_payoff:
                    coalitions.append({
                        'players': [player1.name, player2.name],
                        'benefit': coalition_payoff - individual_payoff,
                        'market_power': player1.market_impact + player2.market_impact
                    })
        
        # Find dominant coalition
        if coalitions:
            dominant = max(coalitions, key=lambda x: x['market_power'])
            risk_score = dominant['market_power']
        else:
            risk_score = 0
        
        return {
            'possible_coalitions': len(coalitions),
            'max_coalition_power': risk_score,
            'manipulation_risk': 'HIGH' if risk_score > 0.6 else 'MEDIUM' if risk_score > 0.3 else 'LOW'
        }
    
    def _generate_recommendation(self,
                               robustness: float,
                               stability: float,
                               expected_payoff: float) -> str:
        """Generate strategy recommendation based on validation results"""
        score = (robustness + stability + min(1, expected_payoff * 10)) / 3
        
        if score > 0.7:
            return "HIGHLY RECOMMENDED - Strategy shows strong game-theoretic properties"
        elif score > 0.5:
            return "RECOMMENDED - Strategy is viable but monitor market conditions"
        elif score > 0.3:
            return "USE WITH CAUTION - Strategy has vulnerabilities"
        else:
            return "NOT RECOMMENDED - High risk of adverse selection"
    
    def _calculate_optimal_position_size(self,
                                       payoff_variance: float,
                                       regime: MarketRegime) -> float:
        """Calculate optimal position size using Kelly Criterion adjusted for game theory"""
        # Base Kelly fraction
        win_probability = 0.55  # Slight edge
        win_loss_ratio = 1.5
        
        kelly_fraction = (win_probability * win_loss_ratio - (1 - win_probability)) / win_loss_ratio
        
        # Adjust for variance (higher variance = smaller position)
        variance_adjustment = 1 / (1 + payoff_variance * 10)
        
        # Regime adjustments
        regime_multipliers = {
            MarketRegime.BULL: 1.2,
            MarketRegime.BEAR: 0.8,
            MarketRegime.SIDEWAYS: 1.0,
            MarketRegime.VOLATILE: 0.6
        }
        
        optimal_size = kelly_fraction * variance_adjustment * regime_multipliers[regime]
        
        # Cap at reasonable levels
        return min(0.25, max(0.01, optimal_size))
    
    def simulate_market_impact(self,
                             trade_size: float,
                             current_liquidity: float,
                             player_actions: Dict[str, str]) -> Dict[str, float]:
        """Simulate market impact of a trade given other players' actions"""
        # Base impact
        base_impact = (trade_size / current_liquidity) ** 0.5
        
        # Adjust for other players
        buy_pressure = sum(1 for action in player_actions.values() if action == "buy")
        sell_pressure = sum(1 for action in player_actions.values() if action == "sell")
        
        net_pressure = buy_pressure - sell_pressure
        
        # Calculate slippage
        slippage = base_impact * (1 + abs(net_pressure) * 0.1)
        
        # Calculate execution probability
        if net_pressure > 2:  # Many buyers
            execution_prob = 0.7  # Harder to buy
        elif net_pressure < -2:  # Many sellers
            execution_prob = 0.7  # Harder to sell
        else:
            execution_prob = 0.95
        
        return {
            'expected_slippage': slippage,
            'execution_probability': execution_prob,
            'adverse_selection_risk': max(0, net_pressure) * 0.1
        }
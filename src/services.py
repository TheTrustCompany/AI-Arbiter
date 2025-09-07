"""
Service layer for handling agent operations and business logic
"""

import logging
import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from agent import arbiter_agent, ArbiterDependency
from models import Policy, Evidence, ArbitrationDecision

logger = logging.getLogger(__name__)

class ArbiterService:
    """
    Service class for handling AI agent operations and policy arbitration
    """
    
    def __init__(self):
        self.agent = arbiter_agent
        self.is_initialized = False
    
    async def initialize(self):
        """
        Initialize the service and agent
        """
        try:
            logger.info("Initializing Arbiter Service...")
            # Future: Initialize agent connections, load configurations, etc.
            self.is_initialized = True
            logger.info("Arbiter Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Arbiter Service: {str(e)}")
            raise
    
    async def cleanup(self):
        """
        Cleanup resources
        """
        try:
            logger.info("Cleaning up Arbiter Service...")
            # Future: Close connections, save state, etc.
            self.is_initialized = False
            logger.info("Arbiter Service cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def process_arbitration(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an arbitration request using the AI agent
        
        Args:
            request_data: Dictionary containing:
                - policy: Policy object or dict with policy data
                - opposer_evidences: List of Evidence objects or dicts
                - defender_evidences: List of Evidence objects or dicts
                - user_query: Optional query string for additional context
            
        Returns:
            Dict containing the arbitration decision and metadata
        """
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")
        
        try:
            logger.info("Processing arbitration request")
            
            # Prepare agent dependencies from request data
            agent_deps = self._prepare_agent_dependencies(request_data)
            
            # Call the agent with proper dependencies
            decision = await self._call_agent(request_data.get("user_query", ""), agent_deps)

            # Format the decision for API response
            formatted_result = self._format_arbitration_decision(decision)
            
            logger.info("Arbitration request processed successfully")
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error processing arbitration: {str(e)}")
            raise
    
    
    async def process_arbitration_stream(self, request_data: Dict[str, Any]):
        if not self.is_initialized:
            raise RuntimeError("Service not initialized")

        try:
            logger.info("Processing arbitration request with streaming")

            agent_deps = self._prepare_agent_dependencies(request_data)

            async with self.agent.run_stream(
                request_data.get("user_query", ""),
                deps=agent_deps
            ) as stream:
                async for partial_output in stream.stream_output():
                    formatted_result = self._format_arbitration_decision(partial_output)
                    yield f"'type': 'partial', data: {json.dumps(formatted_result)}\n\n"


            yield f"data: {json.dumps({'type': 'complete', 'message': 'done', 'data': formatted_result})}\n\n"

        except Exception as e:
            logger.error(f"Error processing arbitration with streaming: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    
    
    def _prepare_agent_dependencies(self, request_data: Dict[str, Any]) -> ArbiterDependency:
        """
        Prepare ArbiterDependency object for the agent from request data
        
        Args:
            request_data: Raw request data containing policy and evidence lists
            
        Returns:
            ArbiterDependency object for the agent
        """
        # Extract policy data
        policy_data = request_data.get("policy")
        if not policy_data:
            raise ValueError("Policy data is required for arbitration")
        
        # Convert policy data to Policy object if it's a dict
        if isinstance(policy_data, dict):
            policy = Policy(**policy_data)
        else:
            policy = policy_data
        
        # Extract and convert opposer evidences
        opposer_evidences_data = request_data.get("opposer_evidences", [])
        opposer_evidences = []
        for evidence_data in opposer_evidences_data:
            if isinstance(evidence_data, dict):
                opposer_evidences.append(Evidence(**evidence_data))
            else:
                opposer_evidences.append(evidence_data)
        
        # Extract and convert defender evidences
        defender_evidences_data = request_data.get("defender_evidences", [])
        defender_evidences = []
        for evidence_data in defender_evidences_data:
            if isinstance(evidence_data, dict):
                defender_evidences.append(Evidence(**evidence_data))
            else:
                defender_evidences.append(evidence_data)
        
        # Create ArbiterDependency object
        agent_deps = ArbiterDependency(
            policy=policy,
            opposer_evidences=opposer_evidences,
            defender_evidences=defender_evidences
        )
        
        logger.debug(f"Prepared agent dependencies for policy: {policy.id}")
        return agent_deps

    async def _call_agent(self, user_query: str, agent_deps: ArbiterDependency) -> ArbitrationDecision:
        """
        Call the AI agent with the prepared dependencies
        
        Args:
            user_query: The user's query or request for arbitration
            agent_deps: ArbiterDependency object containing policy and evidence data
            
        Returns:
            ArbitrationDecision from the agent
        """
        try:
            logger.debug("Calling arbiter agent...")
            
            # Run the agent with the prepared dependencies
            result = await self.agent.run(user_query, deps=agent_deps)

            # Extract the ArbitrationDecision from the result
            decision = result.output
            
            logger.debug(f"Agent call completed with decision: {decision.decision_type}")
            return decision
            
        except Exception as e:
            logger.error(f"Error calling agent: {str(e)}")
            raise
    
    def _format_arbitration_decision(self, decision: ArbitrationDecision) -> Dict[str, Any]:
        """
        Format the ArbitrationDecision for API consumption
        
        Args:
            decision: ArbitrationDecision object from the agent
            
        Returns:
            Formatted response dict
        """
        formatted = {
            "arbitration_result": {
                "decision_id": str(decision.id),
                "policy_id": str(decision.policy_id),
                "opposer_id": str(decision.opposer_id),
                "defender_id": str(decision.defender_id),
                "decision_type": decision.decision_type.value,
                "decision": decision.decision,
                "message": decision.message,
                "confidence_score": decision.confidence,
                "reasoning": decision.reasoning,
                "created_at": decision.created_at.isoformat()
            },
            "metadata": {
                "processing_completed": True,
                "agent_version": "1.0.0",
                "service_version": "1.0.0"
            }
        }
        
        logger.debug("ArbitrationDecision formatted for API response")
        return formatted
    
    async def validate_policy(self, policy_data: Dict[str, Any]) -> bool:
        """
        Validate a policy using basic checks
        
        Args:
            policy_data: Policy data to validate
            
        Returns:
            Boolean indicating if policy is valid
        """
        try:
            logger.info("Validating policy")
            
            # Basic validation - check if policy can be created
            if isinstance(policy_data, dict):
                policy = Policy(**policy_data)
                return True
            elif isinstance(policy_data, Policy):
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error validating policy: {str(e)}")
            return False
    
    async def get_policy_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """
        Get policy recommendations (placeholder for future implementation)
        
        Args:
            context: Context for recommendations
            
        Returns:
            List of recommendations
        """
        try:
            logger.info("Getting policy recommendations")
            # Future: Could use the agent for generating recommendations
            # For now, return basic recommendations based on context
            recommendations = [
                "Ensure policy has clear and measurable objectives",
                "Include specific implementation guidelines",
                "Define success criteria and evaluation metrics"
            ]
            
            if context.get("policy_type") == "security":
                recommendations.extend([
                    "Consider security implications and compliance requirements",
                    "Define access controls and authorization mechanisms"
                ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []

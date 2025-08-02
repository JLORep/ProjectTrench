#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Credential Management System
Secure storage, rotation, and management for 100+ API credentials
Created: 2025-08-02
"""

import os
import json
import base64
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import keyring
import secrets
from pathlib import Path
import logging
from enum import Enum
import aiofiles
import asyncio

class CredentialStatus(Enum):
    """Status of API credentials"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"
    RATE_LIMITED = "rate_limited"

@dataclass
class APICredential:
    """Represents a single API credential"""
    provider: str
    key_id: str
    encrypted_key: str
    status: CredentialStatus
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    rate_limit_hits: int = 0
    environment: str = "production"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CredentialRotationPolicy:
    """Policy for credential rotation"""
    provider: str
    rotation_days: int = 90
    auto_rotate: bool = True
    notify_before_days: int = 7
    max_usage_count: Optional[int] = None
    max_rate_limit_hits: int = 100

class SecureCredentialVault:
    """
    Secure storage for API credentials with encryption
    """
    
    def __init__(self, master_password: Optional[str] = None):
        self.vault_path = Path("data/.credentials")
        self.vault_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        self.cipher_suite = self._initialize_encryption(master_password)
        
        # Credential storage
        self.credentials: Dict[str, List[APICredential]] = {}
        self.rotation_policies: Dict[str, CredentialRotationPolicy] = {}
        
        # Load existing credentials
        self._load_credentials()
        
        # Initialize default rotation policies
        self._initialize_rotation_policies()
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def _initialize_encryption(self, master_password: Optional[str] = None) -> Fernet:
        """Initialize encryption with master password or system keyring"""
        if master_password:
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'trenchcoat_salt_2025',  # In production, use random salt
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        else:
            # Try to get key from system keyring
            stored_key = keyring.get_password("TrenchCoatPro", "master_key")
            if not stored_key:
                # Generate new key and store in keyring
                key = Fernet.generate_key()
                keyring.set_password("TrenchCoatPro", "master_key", key.decode())
            else:
                key = stored_key.encode()
        
        return Fernet(key)
    
    def _initialize_rotation_policies(self):
        """Set up default rotation policies for each provider"""
        default_policies = {
            # High-value providers - rotate more frequently
            'coingecko': CredentialRotationPolicy('coingecko', rotation_days=60),
            'coinmarketcap': CredentialRotationPolicy('coinmarketcap', rotation_days=60),
            'moralis': CredentialRotationPolicy('moralis', rotation_days=90),
            'birdeye': CredentialRotationPolicy('birdeye', rotation_days=90),
            
            # Medium rotation frequency
            'etherscan': CredentialRotationPolicy('etherscan', rotation_days=120),
            'bscscan': CredentialRotationPolicy('bscscan', rotation_days=120),
            'polygonscan': CredentialRotationPolicy('polygonscan', rotation_days=120),
            
            # Low rotation frequency
            'github': CredentialRotationPolicy('github', rotation_days=365),
            'reddit': CredentialRotationPolicy('reddit', rotation_days=180),
            
            # Default policy
            'default': CredentialRotationPolicy('default', rotation_days=90)
        }
        
        self.rotation_policies.update(default_policies)
    
    async def add_credential(self, provider: str, api_key: str, 
                           environment: str = "production",
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a new API credential"""
        # Encrypt the API key
        encrypted_key = self.cipher_suite.encrypt(api_key.encode()).decode()
        
        # Generate unique key ID
        key_id = f"{provider}_{environment}_{secrets.token_hex(8)}"
        
        # Calculate expiration based on rotation policy
        policy = self.rotation_policies.get(provider, self.rotation_policies['default'])
        expires_at = datetime.utcnow() + timedelta(days=policy.rotation_days)
        
        # Create credential object
        credential = APICredential(
            provider=provider,
            key_id=key_id,
            encrypted_key=encrypted_key,
            status=CredentialStatus.ACTIVE,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            environment=environment,
            metadata=metadata or {}
        )
        
        # Store credential
        if provider not in self.credentials:
            self.credentials[provider] = []
        
        self.credentials[provider].append(credential)
        
        # Save to disk
        await self._save_credentials()
        
        self.logger.info(f"Added credential for {provider} in {environment}")
        
        return key_id
    
    async def get_credential(self, provider: str, 
                           environment: str = "production") -> Optional[str]:
        """Get active credential for a provider"""
        if provider not in self.credentials:
            return None
        
        # Find active credential for environment
        active_creds = [
            cred for cred in self.credentials[provider]
            if cred.status == CredentialStatus.ACTIVE 
            and cred.environment == environment
            and (not cred.expires_at or cred.expires_at > datetime.utcnow())
        ]
        
        if not active_creds:
            return None
        
        # Get most recent active credential
        credential = max(active_creds, key=lambda c: c.created_at)
        
        # Update usage
        credential.last_used = datetime.utcnow()
        credential.usage_count += 1
        
        # Decrypt and return
        decrypted_key = self.cipher_suite.decrypt(credential.encrypted_key.encode()).decode()
        
        # Check if rotation needed
        await self._check_rotation_needed(credential)
        
        return decrypted_key
    
    async def rotate_credential(self, provider: str, new_api_key: str,
                              environment: str = "production") -> str:
        """Rotate credential for a provider"""
        # Mark old credentials as revoked
        if provider in self.credentials:
            for cred in self.credentials[provider]:
                if cred.environment == environment and cred.status == CredentialStatus.ACTIVE:
                    cred.status = CredentialStatus.REVOKED
        
        # Add new credential
        new_key_id = await self.add_credential(provider, new_api_key, environment)
        
        self.logger.info(f"Rotated credential for {provider} in {environment}")
        
        return new_key_id
    
    async def check_credential_health(self) -> Dict[str, Any]:
        """Check health of all credentials"""
        health_report = {
            'total_providers': len(self.credentials),
            'active_credentials': 0,
            'expiring_soon': [],
            'expired': [],
            'rate_limited': [],
            'recommendations': []
        }
        
        for provider, creds in self.credentials.items():
            for cred in creds:
                if cred.status == CredentialStatus.ACTIVE:
                    health_report['active_credentials'] += 1
                    
                    # Check expiration
                    if cred.expires_at:
                        days_until_expiry = (cred.expires_at - datetime.utcnow()).days
                        
                        if days_until_expiry < 0:
                            health_report['expired'].append({
                                'provider': provider,
                                'key_id': cred.key_id,
                                'expired_days_ago': -days_until_expiry
                            })
                        elif days_until_expiry < 7:
                            health_report['expiring_soon'].append({
                                'provider': provider,
                                'key_id': cred.key_id,
                                'days_until_expiry': days_until_expiry
                            })
                
                # Check rate limiting
                if cred.rate_limit_hits > 50:
                    health_report['rate_limited'].append({
                        'provider': provider,
                        'key_id': cred.key_id,
                        'hits': cred.rate_limit_hits
                    })
        
        # Generate recommendations
        if health_report['expired']:
            health_report['recommendations'].append(
                f"Rotate {len(health_report['expired'])} expired credentials immediately"
            )
        
        if health_report['expiring_soon']:
            health_report['recommendations'].append(
                f"{len(health_report['expiring_soon'])} credentials expiring soon - plan rotation"
            )
        
        return health_report
    
    async def _check_rotation_needed(self, credential: APICredential):
        """Check if credential needs rotation"""
        policy = self.rotation_policies.get(
            credential.provider, 
            self.rotation_policies['default']
        )
        
        # Check expiration
        if credential.expires_at:
            days_until_expiry = (credential.expires_at - datetime.utcnow()).days
            
            if days_until_expiry <= 0:
                self.logger.warning(f"Credential {credential.key_id} has expired")
                credential.status = CredentialStatus.EXPIRED
            elif days_until_expiry <= policy.notify_before_days:
                self.logger.warning(
                    f"Credential {credential.key_id} expires in {days_until_expiry} days"
                )
        
        # Check usage limits
        if policy.max_usage_count and credential.usage_count >= policy.max_usage_count:
            self.logger.warning(
                f"Credential {credential.key_id} has reached usage limit"
            )
        
        # Check rate limit hits
        if credential.rate_limit_hits >= policy.max_rate_limit_hits:
            self.logger.warning(
                f"Credential {credential.key_id} has high rate limit hits"
            )
            credential.status = CredentialStatus.RATE_LIMITED
    
    async def _save_credentials(self):
        """Save credentials to encrypted file"""
        data = {
            'credentials': {},
            'rotation_policies': {}
        }
        
        # Serialize credentials
        for provider, creds in self.credentials.items():
            data['credentials'][provider] = [
                {
                    **asdict(cred),
                    'status': cred.status.value,
                    'created_at': cred.created_at.isoformat(),
                    'expires_at': cred.expires_at.isoformat() if cred.expires_at else None,
                    'last_used': cred.last_used.isoformat() if cred.last_used else None
                }
                for cred in creds
            ]
        
        # Serialize policies
        for provider, policy in self.rotation_policies.items():
            data['rotation_policies'][provider] = asdict(policy)
        
        # Encrypt entire data
        encrypted_data = self.cipher_suite.encrypt(json.dumps(data).encode())
        
        # Save to file
        vault_file = self.vault_path / "credentials.vault"
        async with aiofiles.open(vault_file, 'wb') as f:
            await f.write(encrypted_data)
    
    def _load_credentials(self):
        """Load credentials from encrypted file"""
        vault_file = self.vault_path / "credentials.vault"
        
        if not vault_file.exists():
            return
        
        try:
            with open(vault_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt data
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            data = json.loads(decrypted_data)
            
            # Load credentials
            self.credentials = {}
            for provider, creds_data in data.get('credentials', {}).items():
                self.credentials[provider] = []
                
                for cred_data in creds_data:
                    credential = APICredential(
                        provider=cred_data['provider'],
                        key_id=cred_data['key_id'],
                        encrypted_key=cred_data['encrypted_key'],
                        status=CredentialStatus(cred_data['status']),
                        created_at=datetime.fromisoformat(cred_data['created_at']),
                        expires_at=datetime.fromisoformat(cred_data['expires_at']) 
                            if cred_data.get('expires_at') else None,
                        last_used=datetime.fromisoformat(cred_data['last_used']) 
                            if cred_data.get('last_used') else None,
                        usage_count=cred_data.get('usage_count', 0),
                        rate_limit_hits=cred_data.get('rate_limit_hits', 0),
                        environment=cred_data.get('environment', 'production'),
                        metadata=cred_data.get('metadata', {})
                    )
                    self.credentials[provider].append(credential)
            
            # Load rotation policies
            for provider, policy_data in data.get('rotation_policies', {}).items():
                self.rotation_policies[provider] = CredentialRotationPolicy(**policy_data)
                
        except Exception as e:
            self.logger.error(f"Failed to load credentials: {e}")


class APICredentialManager:
    """
    High-level manager for API credentials across all providers
    """
    
    def __init__(self):
        self.vault = SecureCredentialVault()
        self.provider_configs = self._load_provider_configs()
        
    def _load_provider_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load provider-specific configurations"""
        return {
            'coingecko': {
                'env_var': 'COINGECKO_API_KEY',
                'header_name': 'x-cg-demo-api-key',
                'requires_auth': True
            },
            'coinmarketcap': {
                'env_var': 'CMC_API_KEY',
                'header_name': 'X-CMC_PRO_API_KEY',
                'requires_auth': True
            },
            'moralis': {
                'env_var': 'MORALIS_API_KEY',
                'header_name': 'X-API-Key',
                'requires_auth': True
            },
            'birdeye': {
                'env_var': 'BIRDEYE_API_KEY',
                'header_name': 'X-API-KEY',
                'requires_auth': True
            },
            'etherscan': {
                'env_var': 'ETHERSCAN_API_KEY',
                'param_name': 'apikey',
                'requires_auth': True
            },
            'github': {
                'env_var': 'GITHUB_TOKEN',
                'header_name': 'Authorization',
                'auth_prefix': 'Bearer ',
                'requires_auth': True
            },
            'reddit': {
                'env_var': 'REDDIT_CLIENT_ID',
                'secret_env_var': 'REDDIT_CLIENT_SECRET',
                'auth_type': 'oauth',
                'requires_auth': True
            }
        }
    
    async def initialize_from_env(self):
        """Initialize credentials from environment variables"""
        initialized = []
        
        for provider, config in self.provider_configs.items():
            if config.get('requires_auth'):
                # Check for API key in environment
                env_var = config.get('env_var')
                if env_var and os.getenv(env_var):
                    api_key = os.getenv(env_var)
                    await self.vault.add_credential(
                        provider=provider,
                        api_key=api_key,
                        environment='production',
                        metadata={'source': 'environment'}
                    )
                    initialized.append(provider)
                
                # Handle providers with client ID/secret
                if config.get('secret_env_var'):
                    secret = os.getenv(config['secret_env_var'])
                    if secret:
                        await self.vault.add_credential(
                            provider=f"{provider}_secret",
                            api_key=secret,
                            environment='production',
                            metadata={'source': 'environment'}
                        )
        
        return initialized
    
    async def get_auth_headers(self, provider: str) -> Dict[str, str]:
        """Get authentication headers for a provider"""
        config = self.provider_configs.get(provider, {})
        
        if not config.get('requires_auth'):
            return {}
        
        # Get credential
        api_key = await self.vault.get_credential(provider)
        if not api_key:
            return {}
        
        headers = {}
        
        # Handle different auth types
        if config.get('header_name'):
            auth_prefix = config.get('auth_prefix', '')
            headers[config['header_name']] = f"{auth_prefix}{api_key}"
        
        return headers
    
    async def get_auth_params(self, provider: str) -> Dict[str, str]:
        """Get authentication parameters for a provider"""
        config = self.provider_configs.get(provider, {})
        
        if not config.get('requires_auth'):
            return {}
        
        # Get credential
        api_key = await self.vault.get_credential(provider)
        if not api_key:
            return {}
        
        params = {}
        
        # Handle parameter-based auth
        if config.get('param_name'):
            params[config['param_name']] = api_key
        
        return params
    
    async def handle_rate_limit(self, provider: str):
        """Handle rate limit hit for a provider"""
        if provider in self.vault.credentials:
            for cred in self.vault.credentials[provider]:
                if cred.status == CredentialStatus.ACTIVE:
                    cred.rate_limit_hits += 1
            
            await self.vault._save_credentials()
    
    async def get_health_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive health dashboard"""
        health = await self.vault.check_credential_health()
        
        # Add provider-specific status
        provider_status = {}
        for provider in self.provider_configs:
            has_active = any(
                cred.status == CredentialStatus.ACTIVE
                for cred in self.vault.credentials.get(provider, [])
            )
            provider_status[provider] = 'configured' if has_active else 'missing'
        
        health['provider_status'] = provider_status
        health['missing_providers'] = [
            p for p, status in provider_status.items() 
            if status == 'missing'
        ]
        
        return health


# Example usage
async def main():
    # Initialize manager
    manager = APICredentialManager()
    
    # Load credentials from environment
    initialized = await manager.initialize_from_env()
    print(f"Initialized credentials for: {initialized}")
    
    # Get auth headers for a provider
    headers = await manager.get_auth_headers('coingecko')
    print(f"CoinGecko headers: {headers}")
    
    # Check health
    health = await manager.get_health_dashboard()
    print(f"Credential health: {json.dumps(health, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
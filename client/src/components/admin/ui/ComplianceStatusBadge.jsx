import React from 'react';
import { Shield, Lock, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

const ComplianceStatusBadge = ({ method, legalHold, verified, size = 'md' }) => {
  // Define color schemes based on method and status
  const getBadgeConfig = () => {
    // Base configuration by disposal method
    const methodConfigs = {
      'SHRED': {
        bgColor: 'bg-red-50',
        textColor: 'text-red-700',
        borderColor: 'border-red-200',
        icon: Shield,
        label: 'Secure Shred',
        description: 'Physical destruction compliant'
      },
      'ARCHIVE': {
        bgColor: 'bg-blue-50',
        textColor: 'text-blue-700',
        borderColor: 'border-blue-200',
        icon: Lock,
        label: 'Secure Archive',
        description: 'Long-term encrypted storage'
      },
      'DELETE': {
        bgColor: 'bg-gray-50',
        textColor: 'text-gray-700',
        borderColor: 'border-gray-200',
        icon: XCircle,
        label: 'Secure Delete',
        description: 'Cryptographic erasure'
      },
      'ANONYMIZE': {
        bgColor: 'bg-purple-50',
        textColor: 'text-purple-700',
        borderColor: 'border-purple-200',
        icon: Shield,
        label: 'Data Anonymization',
        description: 'PII removal compliant'
      },
      'ENCRYPT': {
        bgColor: 'bg-indigo-50',
        textColor: 'text-indigo-700',
        borderColor: 'border-indigo-200',
        icon: Lock,
        label: 'Encrypt & Retain',
        description: 'Encrypted retention'
      }
    };
    
    const config = methodConfigs[method] || {
      bgColor: 'bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-200',
      icon: Shield,
      label: method || 'Unknown',
      description: 'Disposal method'
    };
    
    // Override for legal hold
    if (legalHold) {
      return {
        ...config,
        bgColor: 'bg-red-50',
        textColor: 'text-red-700',
        borderColor: 'border-red-300',
        icon: AlertTriangle,
        label: `${config.label} (Legal Hold)`,
        description: 'Suspended due to legal hold'
      };
    }
    
    // Add verification status
    if (verified !== undefined) {
      if (verified) {
        return {
          ...config,
          icon: CheckCircle,
          label: `${config.label} ✓`,
          description: 'Verified and compliant'
        };
      } else {
        return {
          ...config,
          bgColor: 'bg-yellow-50',
          textColor: 'text-yellow-700',
          borderColor: 'border-yellow-200',
          icon: AlertTriangle,
          label: `${config.label} ⚠`,
          description: 'Pending verification'
        };
      }
    }
    
    return config;
  };
  
  const config = getBadgeConfig();
  const Icon = config.icon;
  
  // Size variants
  const sizeClasses = {
    sm: {
      container: 'px-2 py-1 text-xs',
      icon: 'h-3 w-3'
    },
    md: {
      container: 'px-3 py-1.5 text-sm',
      icon: 'h-4 w-4'
    },
    lg: {
      container: 'px-4 py-2 text-base',
      icon: 'h-5 w-5'
    }
  };
  
  const sizeConfig = sizeClasses[size] || sizeClasses.md;
  
  return (
    <div className="inline-flex flex-col">
      <div className={`
        ${config.bgColor} 
        ${config.textColor} 
        border ${config.borderColor}
        ${sizeConfig.container}
        rounded-lg font-medium
        flex items-center gap-2
        transition-colors duration-200
        hover:opacity-90
      `}>
        <Icon className={sizeConfig.icon} />
        <span>{config.label}</span>
      </div>
      
      {/* Tooltip/description (optional - can be shown on hover) */}
      <div className="mt-1 text-xs text-gray-500 hidden group-hover:block">
        {config.description}
      </div>
    </div>
  );
};

// Prop types for better development experience
ComplianceStatusBadge.defaultProps = {
  method: 'DELETE',
  legalHold: false,
  verified: undefined,
  size: 'md'
};

export default ComplianceStatusBadge;
